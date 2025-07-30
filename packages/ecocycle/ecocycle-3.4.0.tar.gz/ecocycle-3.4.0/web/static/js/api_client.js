/**
 * EcoCycle - Enhanced API Client
 * Provides a consistent interface for frontend-backend communication
 * Handles API requests, WebSocket integration, and offline capabilities
 *
 * Version 2.0 - Improved data integration and real-time synchronization
 */

class EcoCycleApiClient {
    /**
     * Initialize the API client
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        // API configuration
        this.baseUrl = options.baseUrl || this._getDefaultApiUrl();
        this.apiKey = options.apiKey || null;
        this.username = options.username || null;
        this.deviceId = options.deviceId || 'web-' + Math.random().toString(36).substring(2, 15);

        // WebSocket client reference if available
        this.wsClient = options.wsClient || null;

        // Cache settings
        this.enableCache = options.enableCache !== false;
        this.cacheTTL = options.cacheTTL || 300000; // 5 minutes default cache TTL
        this._cache = new Map();

        // Offline storage
        this.offlineStorage = new OfflineStorage('ecocycle_api_storage');

        // Request tracking
        this.pendingRequests = new Map();
        this.requestTimeouts = new Map();

        // Network status
        this._networkStatusListeners();
        this.isOnline = navigator.onLine;
    }

    /**
     * Get the default API URL based on current location
     * @private
     */
    _getDefaultApiUrl() {
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port || (protocol === 'https:' ? '443' : '80');
        return `${protocol}//${host}:${port}/api`;
    }

    /**
     * Set up network status detection
     * @private
     */
    _networkStatusListeners() {
        window.addEventListener('online', () => {
            console.log('Network connection restored');
            this.isOnline = true;
            this._processPendingRequests();
        });

        window.addEventListener('offline', () => {
            console.log('Network connection lost');
            this.isOnline = false;
        });
    }

    /**
     * Set the WebSocket client for real-time communication
     * @param {Object} wsClient - WebSocket client instance
     */
    setWebSocketClient(wsClient) {
        this.wsClient = wsClient;
    }

    /**
     * Set the current user
     * @param {string} username - Username
     * @param {string} apiKey - API key (optional)
     */
    setUser(username, apiKey = null) {
        this.username = username;
        if (apiKey) {
            this.apiKey = apiKey;
        }
    }

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    async request(endpoint, options = {}) {
        const method = options.method || 'GET';
        const data = options.data || null;
        const headers = options.headers || {};
        const useCache = options.useCache !== false && this.enableCache;
        const critical = options.critical === true;
        const forceNetwork = options.forceNetwork === true;

        // Add authentication if available
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        if (this.username) {
            headers['X-Username'] = this.username;
        }

        // Generate a unique request ID
        const requestId = options.requestId || `${method}-${endpoint}-${Date.now()}`;

        // Check if we're offline and not forcing network
        if (!this.isOnline && !forceNetwork) {
            console.log(`Network is offline, handling request ${requestId} accordingly`);

            // For critical requests, store them for later processing
            if (critical) {
                return this._handleOfflineRequest(endpoint, method, data, requestId);
            }

            // For GET requests, try to serve from cache
            if (method === 'GET' && useCache) {
                const cachedData = this._getFromCache(endpoint);
                if (cachedData) {
                    console.log(`Serving cached data for ${endpoint}`);
                    return Promise.resolve(cachedData);
                }
            }

            return Promise.reject({
                error: 'offline',
                message: 'Network is unavailable and no cached data found'
            });
        }

        // Format the URL
        let url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;

        // Check cache for GET requests
        if (method === 'GET' && useCache && !forceNetwork) {
            const cachedData = this._getFromCache(endpoint);
            if (cachedData) {
                console.log(`Serving cached data for ${endpoint}`);
                return Promise.resolve(cachedData);
            }
        }

        try {
            // Prepare fetch options
            const fetchOptions = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                credentials: 'include' // Include cookies for session-based auth
            };

            // Add body data for non-GET requests
            if (method !== 'GET' && data) {
                fetchOptions.body = JSON.stringify(data);
            }

            // Make the request
            const response = await fetch(url, fetchOptions);

            // Parse the response
            let responseData;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            // Check for error status
            if (!response.ok) {
                throw {
                    status: response.status,
                    message: responseData.message || response.statusText,
                    data: responseData
                };
            }

            // For GET requests, cache the response
            if (method === 'GET' && useCache) {
                this._addToCache(endpoint, responseData);
            }

            return responseData;
        } catch (error) {
            console.error(`API request error for ${endpoint}:`, error);

            // For critical requests that failed, store for retry
            if (critical) {
                this._storeFailedRequest(endpoint, method, data, requestId);
            }

            throw error;
        }
    }

    /**
     * Get a resource from the API
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    /**
     * Post data to the API
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to post
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', data });
    }

    /**
     * Put data to the API
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to put
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', data });
    }

    /**
     * Delete a resource from the API
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    /**
     * Get user statistics
     * @param {string} username - Username (defaults to current user)
     * @returns {Promise} - Promise resolving to user statistics
     */
    async getUserStats(username = null) {
        const user = username || this.username;
        if (!user) {
            throw new Error('Username is required');
        }
        return this.get(`stats/${user}`);
    }

    /**
     * Get user trips
     * @param {string} username - Username (defaults to current user)
     * @returns {Promise} - Promise resolving to user trips
     */
    async getUserTrips(username = null) {
        const user = username || this.username;
        if (!user) {
            throw new Error('Username is required');
        }
        return this.get(`trips/${user}`);
    }

    /**
     * Get user routes
     * @param {string} username - Username (defaults to current user)
     * @returns {Promise} - Promise resolving to user routes
     */
    async getUserRoutes(username = null) {
        const user = username || this.username;
        if (!user) {
            throw new Error('Username is required');
        }
        return this.get(`routes/${user}`);
    }

    /**
     * Save a new route
     * @param {Object} routeData - Route data
     * @returns {Promise} - Promise resolving to saved route
     */
    async saveRoute(routeData) {
        return this.post('routes', routeData);
    }

    /**
     * Start tracking a user's position
     * @returns {Promise} - Promise resolving to tracking session data
     */
    async startTracking() {
        return this.post('tracking/start', {
            device_id: this.deviceId,
            timestamp: Date.now()
        });
    }

    /**
     * Update tracking position
     * @param {Object} position - Position data
     * @param {string} trackingId - Tracking session ID
     * @returns {Promise} - Promise resolving to acknowledgment
     */
    async updateTracking(position, trackingId) {
        // If WebSocket is available and connected, use that for real-time updates
        if (this.wsClient && this.wsClient.connected) {
            return this.wsClient.sendTrackUpdate({
                tracking_id: trackingId,
                position: position,
                timestamp: Date.now()
            });
        }

        // Fall back to REST API
        return this.post('tracking/update', {
            tracking_id: trackingId,
            position: position,
            device_id: this.deviceId,
            timestamp: Date.now()
        }, { critical: true });
    }

    /**
     * End tracking session
     * @param {string} trackingId - Tracking session ID
     * @returns {Promise} - Promise resolving to session summary
     */
    async endTracking(trackingId) {
        return this.post('tracking/end', {
            tracking_id: trackingId,
            device_id: this.deviceId,
            timestamp: Date.now()
        });
    }

    /**
     * Get synchronization status
     * @returns {Promise} - Promise resolving to sync status
     */
    async getSyncStatus() {
        return this.get('sync/status');
    }

    /**
     * Request synchronization
     * @param {Object} options - Sync options
     * @returns {Promise} - Promise resolving to sync request acknowledgment
     */
    async requestSync(options = {}) {
        // If WebSocket is available and connected, use that for real-time sync
        if (this.wsClient && this.wsClient.connected) {
            return this.wsClient.requestSync(options);
        }

        // Fall back to REST API
        return this.post('sync/request', {
            device_id: this.deviceId,
            entity_types: options.entityTypes || ['all'],
            last_sync: options.lastSync || 0
        });
    }

    /**
     * Upload changes to the server
     * @param {Array} changes - Array of changes to upload
     * @returns {Promise} - Promise resolving to upload response
     */
    async uploadChanges(changes) {
        // If WebSocket is available and connected, use that for faster updates
        if (this.wsClient && this.wsClient.connected) {
            const requestId = `upload-${Date.now()}`;
            return new Promise((resolve, reject) => {
                // Set up a response handler for this specific request
                const responseHandler = (message) => {
                    if (message.type === 'upload_response' && message.request_id === requestId) {
                        this.wsClient.removeEventListener('message', responseHandler);
                        if (message.success) {
                            resolve(message);
                        } else {
                            reject(message);
                        }
                    }
                };

                // Listen for the response
                this.wsClient.addEventListener('message', responseHandler);

                // Send the changes
                this.wsClient.send({
                    type: 'upload_changes',
                    request_id: requestId,
                    changes: changes,
                    device_id: this.deviceId,
                    timestamp: Date.now()
                }, true, true);

                // Set a timeout
                setTimeout(() => {
                    this.wsClient.removeEventListener('message', responseHandler);
                    reject({
                        error: 'timeout',
                        message: 'Request timed out'
                    });
                }, 30000);
            });
        }

        // Fall back to REST API
        return this.post('sync/upload', {
            device_id: this.deviceId,
            changes: changes
        }, { critical: true });
    }

    /**
     * Register for push notifications
     * @param {string} token - Device token
     * @param {string} platform - Platform (web, android, ios)
     * @returns {Promise} - Promise resolving to registration result
     */
    async registerPushNotification(token, platform = 'web') {
        return this.post('notifications/register', {
            token: token,
            platform: platform,
            device_id: this.deviceId
        });
    }

    /**
     * Update notification settings
     * @param {Object} settings - Notification settings
     * @returns {Promise} - Promise resolving to updated settings
     */
    async updateNotificationSettings(settings) {
        return this.post('notifications/settings', settings);
    }

    /**
     * Join a challenge
     * @param {string} challengeId - Challenge ID
     * @returns {Promise} - Promise resolving to join result
     */
    async joinChallenge(challengeId) {
        return this.post('challenges/join', {
            challenge_id: challengeId
        });
    }

    /**
     * Update challenge progress
     * @param {string} challengeId - Challenge ID
     * @param {Object} progress - Progress data
     * @returns {Promise} - Promise resolving to updated challenge
     */
    async updateChallengeProgress(challengeId, progress) {
        return this.post(`challenges/${challengeId}/progress`, progress);
    }

    /**
     * Create a forum post
     * @param {Object} postData - Post data
     * @returns {Promise} - Promise resolving to created post
     */
    async createForumPost(postData) {
        return this.post('forum/posts', postData);
    }

    /**
     * Get forum posts
     * @param {Object} filters - Filter criteria
     * @returns {Promise} - Promise resolving to forum posts
     */
    async getForumPosts(filters = {}) {
        let queryString = '';
        if (Object.keys(filters).length > 0) {
            queryString = '?' + new URLSearchParams(filters).toString();
        }
        return this.get(`forum/posts${queryString}`);
    }

    /**
     * Get user statistics with detailed breakdown
     * @param {string} username - Username (defaults to current user)
     * @param {boolean} detailed - Whether to include detailed stats
     * @returns {Promise} - Promise resolving to user statistics
     */
    async getUserDetailedStats(username = null, detailed = true) {
        const user = username || this.username;
        if (!user) {
            throw new Error('Username is required');
        }
        return this.get(`stats/${user}?detailed=${detailed ? 1 : 0}`);
    }

    /**
     * Get environmental impact data
     * @param {string} username - Username (defaults to current user)
     * @returns {Promise} - Promise resolving to environmental impact data
     */
    async getEnvironmentalImpact(username = null) {
        const user = username || this.username;
        if (!user) {
            throw new Error('Username is required');
        }
        return this.get(`environmental-impact/${user}`);
    }

    /**
     * Get route analysis data
     * @param {string} routeId - Route ID
     * @returns {Promise} - Promise resolving to route analysis data
     */
    async getRouteAnalysis(routeId) {
        if (!routeId) {
            throw new Error('Route ID is required');
        }
        return this.get(`routes/analysis/${routeId}`);
    }

    /**
     * Compare multiple routes
     * @param {Array} routeIds - Array of route IDs to compare
     * @returns {Promise} - Promise resolving to route comparison data
     */
    async compareRoutes(routeIds) {
        if (!Array.isArray(routeIds) || routeIds.length < 2) {
            throw new Error('At least two route IDs are required for comparison');
        }
        return this.post('routes/compare', { route_ids: routeIds });
    }

    /**
     * Get route safety assessment
     * @param {string} routeId - Route ID
     * @returns {Promise} - Promise resolving to safety assessment data
     */
    async getRouteSafetyAssessment(routeId) {
        if (!routeId) {
            throw new Error('Route ID is required');
        }
        return this.get(`routes/safety/${routeId}`);
    }

    /**
     * Get alternative routes for a given start and end point
     * @param {Object} startPoint - Start coordinates {lat, lng}
     * @param {Object} endPoint - End coordinates {lat, lng}
     * @param {Object} options - Route options (mode, preferences, etc.)
     * @returns {Promise} - Promise resolving to alternative routes
     */
    async getAlternativeRoutes(startPoint, endPoint, options = {}) {
        if (!startPoint || !endPoint) {
            throw new Error('Start and end points are required');
        }

        return this.post('routes/alternatives', {
            start: startPoint,
            end: endPoint,
            options: options
        });
    }

    /**
     * Handle a request when offline
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @param {string} requestId - Request ID
     * @returns {Promise} - Promise resolving or rejecting based on request type
     * @private
     */
    _handleOfflineRequest(endpoint, method, data, requestId) {
        // Store the request for later
        this._storeFailedRequest(endpoint, method, data, requestId);

        // For GET requests, try to serve from IndexedDB
        if (method === 'GET') {
            return this.offlineStorage.get(endpoint)
                .then(storedData => {
                    if (storedData) {
                        return Promise.resolve(storedData.data);
                    }
                    return Promise.reject({
                        error: 'offline',
                        message: 'Network is unavailable and no stored data found'
                    });
                });
        }

        // For other methods, just acknowledge the queuing
        return Promise.resolve({
            success: false,
            queued: true,
            message: 'Request queued for processing when online',
            request_id: requestId
        });
    }

    /**
     * Store a failed request for retry when online
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @param {string} requestId - Request ID
     * @private
     */
    _storeFailedRequest(endpoint, method, data, requestId) {
        const request = {
            id: requestId,
            endpoint,
            method,
            data,
            timestamp: Date.now()
        };

        // Add to pending requests
        this.pendingRequests.set(requestId, request);

        // Save to storage
        const pendingRequests = Array.from(this.pendingRequests.values());
        localStorage.setItem('ecocycle_pending_requests', JSON.stringify(pendingRequests));

        console.log(`Request ${requestId} stored for later processing`);
    }

    /**
     * Process pending requests when coming back online
     * @private
     */
    async _processPendingRequests() {
        // Load pending requests from storage
        try {
            const storedRequests = localStorage.getItem('ecocycle_pending_requests');
            if (storedRequests) {
                const requests = JSON.parse(storedRequests);
                requests.forEach(request => {
                    this.pendingRequests.set(request.id, request);
                });
            }
        } catch (e) {
            console.error('Error loading pending requests:', e);
        }

        if (this.pendingRequests.size === 0) {
            return;
        }

        console.log(`Processing ${this.pendingRequests.size} pending requests`);

        // Process in batches to avoid overwhelming the server
        const batchSize = 5;
        const requestIds = Array.from(this.pendingRequests.keys());

        // Process batches sequentially
        for (let i = 0; i < requestIds.length; i += batchSize) {
            const batch = requestIds.slice(i, i + batchSize);
            await Promise.allSettled(
                batch.map(async (requestId) => {
                    const request = this.pendingRequests.get(requestId);
                    if (!request) return;

                    try {
                        await this.request(request.endpoint, {
                            method: request.method,
                            data: request.data,
                            requestId: request.id,
                            forceNetwork: true
                        });

                        // Remove processed request
                        this.pendingRequests.delete(requestId);
                    } catch (error) {
                        console.error(`Error processing pending request ${requestId}:`, error);

                        // Keep the request if it's a network error
                        if (error.status === undefined) {
                            // It's a network error, keep the request
                            return;
                        }

                        // For other errors, remove the request
                        this.pendingRequests.delete(requestId);
                    }
                })
            );

            // Small delay between batches
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // Update storage with remaining requests
        const remainingRequests = Array.from(this.pendingRequests.values());
        if (remainingRequests.length > 0) {
            localStorage.setItem('ecocycle_pending_requests', JSON.stringify(remainingRequests));
        } else {
            localStorage.removeItem('ecocycle_pending_requests');
        }

        console.log(`Processed pending requests, ${this.pendingRequests.size} remaining`);
    }

    /**
     * Add data to cache
     * @param {string} key - Cache key
     * @param {*} data - Data to cache
     * @private
     */
    _addToCache(key, data) {
        this._cache.set(key, {
            data,
            timestamp: Date.now()
        });

        // Also store in IndexedDB for offline access
        this.offlineStorage.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    /**
     * Get data from cache
     * @param {string} key - Cache key
     * @returns {*} - Cached data or null
     * @private
     */
    _getFromCache(key) {
        const cached = this._cache.get(key);

        if (cached) {
            // Check if cache is still valid
            if (Date.now() - cached.timestamp < this.cacheTTL) {
                return cached.data;
            }

            // If expired, remove from cache
            this._cache.delete(key);
        }

        return null;
    }

    /**
     * Clear the API cache
     * @param {string} key - Specific key to clear (optional)
     */
    clearCache(key = null) {
        if (key) {
            this._cache.delete(key);
            this.offlineStorage.delete(key);
        } else {
            this._cache.clear();
            this.offlineStorage.clear();
        }
    }
}

/**
 * Offline storage class for persisting data
 */
class OfflineStorage {
    /**
     * Initialize offline storage
     * @param {string} storeName - Name of the storage
     */
    constructor(storeName) {
        this.storeName = storeName;
        this.dbName = 'ecocycle_offline_db';
        this.dbVersion = 1;
        this.db = null;

        // Initialize the database
        this._initDb();
    }

    /**
     * Initialize the IndexedDB database
     * @private
     */
    _initDb() {
        const request = indexedDB.open(this.dbName, this.dbVersion);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Create object store if it doesn't exist
            if (!db.objectStoreNames.contains(this.storeName)) {
                db.createObjectStore(this.storeName, { keyPath: 'key' });
                console.log(`Created object store ${this.storeName}`);
            }
        };

        request.onsuccess = (event) => {
            this.db = event.target.result;
            console.log(`IndexedDB initialized for ${this.storeName}`);
        };

        request.onerror = (event) => {
            console.error('Error initializing IndexedDB:', event.target.error);
        };
    }

    /**
     * Get a value from storage
     * @param {string} key - Key to retrieve
     * @returns {Promise} - Promise resolving to stored value
     */
    get(key) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                return setTimeout(() => this.get(key).then(resolve).catch(reject), 100);
            }

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get({ key });

            request.onsuccess = (event) => {
                const result = event.target.result;
                resolve(result ? result.value : null);
            };

            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }

    /**
     * Set a value in storage
     * @param {string} key - Key to store under
     * @param {*} value - Value to store
     * @returns {Promise} - Promise resolving when stored
     */
    set(key, value) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                return setTimeout(() => this.set(key, value).then(resolve).catch(reject), 100);
            }

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.put({ key, value });

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }

    /**
     * Delete a value from storage
     * @param {string} key - Key to delete
     * @returns {Promise} - Promise resolving when deleted
     */
    delete(key) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                return setTimeout(() => this.delete(key).then(resolve).catch(reject), 100);
            }

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete({ key });

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }

    /**
     * Clear all values from storage
     * @returns {Promise} - Promise resolving when cleared
     */
    clear() {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                return setTimeout(() => this.clear().then(resolve).catch(reject), 100);
            }

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.clear();

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }
}

// Global instance for easy access
let ecocycleApi = null;

/**
 * Initialize the global API client
 * @param {Object} options - Configuration options
 * @returns {EcoCycleApiClient} - The client instance
 */
function initApiClient(options) {
    ecocycleApi = new EcoCycleApiClient(options);
    return ecocycleApi;
}

/**
 * Get the global API client instance
 * @returns {EcoCycleApiClient|null} - The client instance or null
 */
function getApiClient() {
    return ecocycleApi;
}
