/**
 * EcoCycle - Enhanced WebSocket Client
 * Handles real-time communication between web client and Python backend
 * Features improved reliability, offline support, and synchronization
 */

class EcoCycleWebSocketClient {
    /**
     * Initialize the WebSocket client
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        // User identification
        this.userId = options.userId;
        this.token = options.token;
        this.deviceId = options.deviceId || 'web-' + Math.random().toString(36).substring(2, 15);
        
        // Connection settings
        this.url = options.url || this._getDefaultWebSocketUrl();
        this.autoReconnect = options.autoReconnect !== false;
        this.enableOfflineQueue = options.enableOfflineQueue !== false;
        this.heartbeatInterval = options.heartbeatInterval || 30000; // 30 seconds
        this.reconnectInterval = options.reconnectInterval || 5000; // 5 seconds
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        
        // Callbacks
        this.onMessage = options.onMessage || ((msg) => console.log('WebSocket message:', msg));
        this.onConnect = options.onConnect || (() => console.log('WebSocket connected'));
        this.onDisconnect = options.onDisconnect || (() => console.log('WebSocket disconnected'));
        this.onError = options.onError || ((err) => console.error('WebSocket error:', err));
        this.onSyncComplete = options.onSyncComplete || (() => console.log('Sync completed'));
        this.onSyncProgress = options.onSyncProgress || (() => {});
        
        // State
        this.socket = null;
        this.connected = false;
        this.intentionalClose = false;
        this.reconnectAttempts = 0;
        this.heartbeatTimer = null;
        this.lastSyncTime = 0;
        this.syncInProgress = false;
        
        // Message and operation queues
        this.messageQueue = [];
        this.offlineOperations = [];
        
        // Metrics
        this.metrics = {
            messagesSent: 0,
            messagesReceived: 0,
            connectCount: 0,
            latency: 0
        };
        
        // Set up network detection
        this._setupNetworkDetection();
        
        // Initialize message handlers
        this._initMessageHandlers();
        
        // Load offline queue if enabled
        if (this.enableOfflineQueue) {
            this._loadOfflineQueue();
        }
    }
    
    /**
     * Get the default WebSocket URL
     * @private
     */
    _getDefaultWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = 5052;
        return `${protocol}//${host}:${port}`;
    }
    
    /**
     * Initialize message handlers
     * @private
     */
    _initMessageHandlers() {
        this.messageHandlers = {
            connected: this._handleConnected.bind(this),
            sync: this._handleSync.bind(this),
            sync_status: this._handleSyncStatus.bind(this),
            sync_progress: this._handleSyncProgress.bind(this),
            sync_response: this._handleSyncResponse.bind(this),
            sync_acknowledged: this._handleSyncAcknowledged.bind(this),
            notification: this._handleNotification.bind(this),
            pong: this._handlePong.bind(this),
            error: this._handleError.bind(this),
            track_update: this._handleTrackUpdate.bind(this)
        };
    }
    
    /**
     * Set up network status detection
     * @private
     */
    _setupNetworkDetection() {
        window.addEventListener('online', () => {
            console.log('Network connection restored');
            
            if (!this.connected && this.autoReconnect) {
                this.reconnectAttempts = 0;
                this.connect();
            }
            
            this._processOfflineOperations();
        });
        
        window.addEventListener('offline', () => {
            console.log('Network connection lost');
            
            if (this.connected) {
                this.connected = false;
                this.onDisconnect({ reason: 'network_disconnected' });
            }
        });
    }
    
    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.socket && (this.socket.readyState === WebSocket.OPEN || 
                          this.socket.readyState === WebSocket.CONNECTING)) {
            console.log('WebSocket already connected or connecting');
            return;
        }
        
        this.intentionalClose = false;
        this.metrics.connectCount++;
        
        console.log(`Connecting to ${this.url}`);
        this.socket = new WebSocket(this.url);
        
        // Set up handlers
        this.socket.onopen = this._handleOpen.bind(this);
        this.socket.onmessage = this._handleMessage.bind(this);
        this.socket.onclose = this._handleClose.bind(this);
        this.socket.onerror = this._handleSocketError.bind(this);
    }
    
    /**
     * Handle WebSocket open event
     * @private
     */
    _handleOpen() {
        console.log('WebSocket connection established');
        this.reconnectAttempts = 0;
        
        // Send authentication
        const authMessage = {
            auth: true,
            user_id: this.userId,
            token: this.token,
            device_id: this.deviceId,
            user_agent: navigator.userAgent,
            timestamp: Date.now()
        };
        
        this._sendMessage(authMessage);
        this._setupHeartbeat();
    }
    
    /**
     * Handle incoming WebSocket message
     * @param {Event} event - WebSocket message event
     * @private
     */
    _handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            this.metrics.messagesReceived++;
            this._processMessage(message);
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
            this.onError({
                type: 'parse_error',
                message: 'Failed to parse message',
                original_error: error
            });
        }
    }
    
    /**
     * Handle WebSocket close event
     * @param {Event} event - WebSocket close event
     * @private
     */
    _handleClose(event) {
        this.connected = false;
        console.log(`WebSocket connection closed: ${event.code} - ${event.reason}`);
        
        // Clear heartbeat timer
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
        
        // Attempt to reconnect if not intentionally closed
        if (!this.intentionalClose && this.autoReconnect && navigator.onLine) {
            this._attemptReconnect();
        }
        
        this.onDisconnect({
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
        });
    }
    
    /**
     * Handle WebSocket error
     * @param {Event} error - WebSocket error event
     * @private
     */
    _handleSocketError(error) {
        console.error('WebSocket error:', error);
        this.onError({
            type: 'connection_error',
            message: 'WebSocket connection error',
            original_error: error
        });
    }
    
    /**
     * Disconnect from the WebSocket server
     * @param {string} reason - Reason for disconnection
     */
    disconnect(reason = 'User initiated disconnect') {
        console.log(`Disconnecting: ${reason}`);
        this.intentionalClose = true;
        
        // Clear heartbeat timer
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
        
        if (this.socket) {
            // Try to send clean disconnect message
            if (this.socket.readyState === WebSocket.OPEN) {
                try {
                    this._sendMessage({
                        type: 'disconnect',
                        reason: reason
                    });
                } catch (e) {
                    // Ignore errors during shutdown
                }
            }
            
            this.socket.close(1000, reason);
            this.socket = null;
        }
        
        this.connected = false;
        
        // Save offline queue
        if (this.enableOfflineQueue && this.messageQueue.length > 0) {
            this._saveOfflineQueue();
        }
    }
    
    /**
     * Send a message to the WebSocket server
     * @param {Object} message - Message to send
     * @param {boolean} requiresAck - Whether this message requires acknowledgment
     * @param {boolean} storeIfOffline - Whether to store this message if offline
     * @returns {boolean} - Whether the message was sent
     */
    send(message, requiresAck = false, storeIfOffline = true) {
        // If not connected, queue the message
        if (!this.connected) {
            if (this.enableOfflineQueue && storeIfOffline) {
                // Queue important operations for offline sync
                if (message.type && message.type.includes('sync') && message.data) {
                    console.log('Storing sync operation for offline processing');
                    this.offlineOperations.push({
                        ...message,
                        queued_at: Date.now()
                    });
                    this._saveOfflineQueue();
                }
                
                // Queue regular message
                this.messageQueue.push(message);
                console.log(`WebSocket not connected, queued message: ${message.type || 'unknown'}`);
                return false;
            } else {
                console.log('Message not sent: disconnected and offline queuing disabled');
                return false;
            }
        }
        
        return this._sendMessage(message, requiresAck);
    }
    
    /**
     * Internal method to send a message to the socket
     * @param {Object} message - Message to send
     * @param {boolean} requiresAck - Whether this message requires acknowledgment
     * @returns {boolean} - Whether the message was sent
     * @private
     */
    _sendMessage(message, requiresAck = false) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return false;
        }
        
        try {
            // Ensure message is an object with a type
            if (typeof message === 'string') {
                message = { type: 'message', content: message };
            } else if (!message.type) {
                message.type = 'message';
            }
            
            // Add timestamp and message ID if not present
            if (!message.timestamp) {
                message.timestamp = Date.now();
            }
            
            if (requiresAck && !message.message_id) {
                message.message_id = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
                message.requires_ack = true;
            }
            
            const messageStr = JSON.stringify(message);
            this.socket.send(messageStr);
            
            // Update metrics
            this.metrics.messagesSent++;
            
            return true;
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            this.onError({
                type: 'send_error',
                message: 'Failed to send WebSocket message',
                original_error: error,
                original_message: message
            });
            return false;
        }
    }
    
    /**
     * Set up heartbeat for connection monitoring
     * @private
     */
    _setupHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }
        
        this.heartbeatTimer = setInterval(() => {
            if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
                this._sendMessage({
                    type: 'ping',
                    timestamp: Date.now()
                });
            }
        }, this.heartbeatInterval);
    }
    
    /**
     * Attempt to reconnect to the WebSocket server
     * @private
     */
    _attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Maximum reconnect attempts reached');
            return;
        }
        
        // Don't attempt reconnection if we're offline
        if (!navigator.onLine) {
            console.log('Network is offline - skipping reconnect until online');
            return;
        }
        
        this.reconnectAttempts++;
        
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        
        setTimeout(() => {
            if (!this.connected && navigator.onLine) {
                this.connect();
            }
        }, this.reconnectInterval);
    }
    
    /**
     * Process an incoming message from the server
     * @param {Object} message - Parsed message object
     * @private
     */
    _processMessage(message) {
        try {
            const { type } = message;
            
            // Handle based on message type
            if (type && this.messageHandlers[type]) {
                this.messageHandlers[type](message);
            } else {
                // Default handler
                console.log(`Unhandled message type: ${type || 'unknown'}`);
                this.onMessage(message);
            }
        } catch (error) {
            console.error('Error processing message:', error);
            this.onError({
                type: 'processing_error',
                message: 'Error processing WebSocket message',
                original_error: error,
                original_message: message
            });
        }
    }
    
    /**
     * Send queued messages after connecting
     * @private
     */
    _sendQueuedMessages() {
        if (this.messageQueue.length > 0 && this.connected) {
            console.log(`Sending ${this.messageQueue.length} queued messages`);
            
            // Process queue in batches
            const batchSize = 10;
            const processNextBatch = () => {
                const batch = this.messageQueue.splice(0, batchSize);
                
                if (batch.length === 0) return;
                
                batch.forEach(message => {
                    this._sendMessage(message);
                });
                
                // Schedule next batch if more messages
                if (this.messageQueue.length > 0) {
                    setTimeout(processNextBatch, 100); // Small delay
                }
            };
            
            processNextBatch();
        }
    }
    
    /**
     * Process operations that were queued while offline
     * @private
     */
    _processOfflineOperations() {
        if (!this.connected || !this.offlineOperations.length) {
            return;
        }
        
        console.log(`Processing ${this.offlineOperations.length} offline operations`);
        
        // Group operations by type
        const operationsByType = {};
        this.offlineOperations.forEach(op => {
            if (!operationsByType[op.type]) {
                operationsByType[op.type] = [];
            }
            operationsByType[op.type].push(op);
        });
        
        // Process each type
        Object.keys(operationsByType).forEach(type => {
            const operations = operationsByType[type];
            console.log(`Processing ${operations.length} ${type} operations`);
            
            // Send batch request
            this.send({
                type: 'sync_request',
                operations: operations,
                timestamp: Date.now(),
                request_id: `offline-sync-${Date.now()}`
            });
        });
        
        // Clear processed operations
        this.offlineOperations = [];
        localStorage.removeItem('ecocycle_offline_operations');
    }
    
    /**
     * Save the offline queue to local storage
     * @private
     */
    _saveOfflineQueue() {
        if (this.enableOfflineQueue) {
            try {
                localStorage.setItem('ecocycle_message_queue', JSON.stringify(this.messageQueue));
                localStorage.setItem('ecocycle_offline_operations', JSON.stringify(this.offlineOperations));
            } catch (e) {
                console.error('Error saving offline queue to local storage:', e);
            }
        }
    }
    
    /**
     * Load the offline queue from local storage
     * @private
     */
    _loadOfflineQueue() {
        if (this.enableOfflineQueue) {
            try {
                const queueData = localStorage.getItem('ecocycle_message_queue');
                const operationsData = localStorage.getItem('ecocycle_offline_operations');
                
                if (queueData) {
                    this.messageQueue = JSON.parse(queueData);
                    console.log(`Loaded ${this.messageQueue.length} messages from offline queue`);
                }
                
                if (operationsData) {
                    this.offlineOperations = JSON.parse(operationsData);
                    console.log(`Loaded ${this.offlineOperations.length} operations from offline queue`);
                }
            } catch (e) {
                console.error('Error loading offline queue from local storage:', e);
            }
        }
    }
    
    /**
     * Request data synchronization from the server
     * @param {Object} options - Sync options
     * @returns {string} - Request ID of the sync request
     */
    requestSync(options = {}) {
        const requestId = `sync_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
        
        this.syncInProgress = true;
        
        const syncRequest = {
            type: 'sync_request',
            request_id: requestId,
            timestamp: Date.now(),
            force: options.force === true,
            items: options.items || [],
            last_sync: this.lastSyncTime
        };
        
        console.log(`Requesting sync: ${requestId}`);
        
        this.send(syncRequest, true, true);
        
        return requestId;
    }
    
    /**
     * Send tracking update to the server
     * @param {Object} trackData - Tracking data
     * @param {boolean} critical - Whether this update is critical
     * @returns {boolean} - Whether the update was sent
     */
    sendTrackUpdate(trackData, critical = false) {
        return this.send({
            type: 'track_update',
            data: trackData,
            timestamp: Date.now(),
            critical: critical
        }, false, critical);
    }
    
    /**
     * Get the current connection state and metrics
     * @returns {Object} - Connection state and metrics
     */
    getStatus() {
        return {
            connected: this.connected,
            lastSyncTime: this.lastSyncTime ? new Date(this.lastSyncTime) : null,
            syncInProgress: this.syncInProgress,
            reconnectAttempts: this.reconnectAttempts,
            metrics: { ...this.metrics },
            offlineOperationCount: this.offlineOperations.length,
            queuedMessageCount: this.messageQueue.length
        };
    }
    
    // Message Type Handlers
    
    _handleConnected(message) {
        console.log('Successfully authenticated with WebSocket server');
        this.connected = true;
        
        // Load offline queue if enabled
        if (this.enableOfflineQueue) {
            this._loadOfflineQueue();
        }
        
        // Send queued messages
        this._sendQueuedMessages();
        
        // Process offline operations
        if (this.offlineOperations.length > 0) {
            setTimeout(() => this._processOfflineOperations(), 1000);
        }
        
        // Notify callback
        this.onConnect(message);
    }
    
    _handleSync(message) {
        console.log('Sync received:', message);
        
        this.lastSyncTime = Date.now();
        this.syncInProgress = false;
        
        this.onMessage(message);
    }
    
    _handleSyncResponse(message) {
        console.log('Sync response received:', message);
        
        this.syncInProgress = false;
        this.lastSyncTime = Date.now();
        
        if (message.success) {
            // Clean up offline operations if this was an offline sync
            if (message.request_id && message.request_id.startsWith('offline-sync')) {
                this.offlineOperations = [];
                localStorage.removeItem('ecocycle_offline_operations');
            }
            
            if (typeof this.onSyncComplete === 'function') {
                this.onSyncComplete(message);
            }
        } else {
            console.error('Sync failed:', message.error || 'Unknown error');
            
            this.onError({
                type: 'sync_error',
                message: message.error || 'Sync failed',
                details: message
            });
        }
        
        this.onMessage(message);
    }
    
    _handleSyncProgress(message) {
        console.log(`Sync progress: ${message.progress}%`);
        
        if (typeof this.onSyncProgress === 'function') {
            this.onSyncProgress({
                progress: message.progress,
                itemsProcessed: message.items_processed,
                totalItems: message.total_items,
                requestId: message.request_id
            });
        }
        
        this.onMessage(message);
    }
    
    _handleSyncStatus(message) {
        console.log('Sync status update:', message.status);
        
        if (message.status) {
            this.lastSyncTime = message.status.last_sync || this.lastSyncTime;
            this.syncInProgress = message.status.sync_in_progress || false;
        }
        
        this.onMessage(message);
    }
    
    _handleSyncAcknowledged(message) {
        console.log('Sync request acknowledged:', message.message);
        
        this.syncInProgress = true;
        
        this.onMessage(message);
    }
    
    _handleNotification(message) {
        console.log('Notification received:', message.data);
        
        // Check if we need to sync
        if (message.data && message.data.type === 'sync_required') {
            this.requestSync();
        }
        
        this.onMessage(message);
    }
    
    _handlePong(message) {
        const latency = Date.now() - message.timestamp;
        this.metrics.latency = latency;
        
        console.log(`WebSocket latency: ${latency}ms`);
    }
    
    _handleError(message) {
        console.error('Server error:', message.message);
        
        this.onError({
            type: 'server_error',
            message: message.message,
            code: message.code
        });
    }
    
    _handleTrackUpdate(message) {
        console.log('Track update received:', message);
        
        this.onMessage(message);
    }
}

// Global instance for easy access
let ecocycleWs = null;

/**
 * Initialize the global WebSocket client
 * @param {Object} options - Configuration options
 * @returns {EcoCycleWebSocketClient} - The client instance
 */
function initWebSocketClient(options) {
    ecocycleWs = new EcoCycleWebSocketClient(options);
    return ecocycleWs;
}

/**
 * Get the global WebSocket client instance
 * @returns {EcoCycleWebSocketClient|null} - The client instance or null
 */
function getWebSocketClient() {
    return ecocycleWs;
}
