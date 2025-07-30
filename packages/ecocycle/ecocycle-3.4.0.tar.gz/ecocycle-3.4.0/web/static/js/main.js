/**
 * EcoCycle Web Dashboard - Main JavaScript
 * Handles frontend functionality for the EcoCycle web dashboard
 */

// Check if the application is online
const isOnline = () => navigator.onLine;

// Track online/offline status
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Show offline indicator when user goes offline
function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offline-indicator');
    
    if (!isOnline()) {
        // Create offline indicator if it doesn't exist
        if (!offlineIndicator) {
            const indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = '<i class="fas fa-wifi-slash me-2"></i> You\'re offline. Some features may be limited.';
            document.body.appendChild(indicator);
            
            // Show sync status as offline
            const syncStatusIcon = document.getElementById('sync-status-icon');
            const syncStatusText = document.getElementById('sync-status-text');
            if (syncStatusIcon && syncStatusText) {
                syncStatusIcon.innerHTML = '<i class="fas fa-times-circle text-danger fa-2x"></i>';
                syncStatusText.textContent = 'Offline - Data will sync when connection is restored';
            }
        }
    } else {
        // Remove offline indicator
        if (offlineIndicator) {
            offlineIndicator.remove();
            
            // Attempt to sync offline data
            synchronizeOfflineData();
        }
    }
}

// Function to synchronize offline data when coming back online
function synchronizeOfflineData() {
    // In a real application, this would pull data from IndexedDB/localStorage
    // and sync it with the server
    
    console.log('Syncing offline data...');
    
    // Update sync status to show syncing
    const syncStatusIcon = document.getElementById('sync-status-icon');
    const syncStatusText = document.getElementById('sync-status-text');
    const lastSyncTime = document.getElementById('last-sync-time');
    
    if (syncStatusIcon && syncStatusText) {
        syncStatusIcon.innerHTML = '<i class="fas fa-sync-alt fa-spin text-primary fa-2x"></i>';
        syncStatusText.textContent = 'Syncing offline data...';
        
        // Simulate sync completion
        setTimeout(() => {
            syncStatusIcon.innerHTML = '<i class="fas fa-check-circle text-success fa-2x"></i>';
            syncStatusText.textContent = 'All data in sync';
            
            if (lastSyncTime) {
                lastSyncTime.textContent = 'Last synced: Just now';
            }
            
            console.log('Offline data sync complete');
        }, 2000);
    }
}

// Initialize real-time tracking
function initializeTracking() {
    // This would normally connect to WebSocket for real-time updates
    const trackingButton = document.getElementById('start-tracking');
    
    if (trackingButton) {
        trackingButton.addEventListener('click', function() {
            if (this.dataset.tracking === 'false') {
                // Start tracking
                this.dataset.tracking = 'true';
                this.innerHTML = '<i class="fas fa-stop-circle me-2"></i>Stop Tracking';
                this.classList.replace('btn-success', 'btn-danger');
                
                startRealTimeTracking();
            } else {
                // Stop tracking
                this.dataset.tracking = 'false';
                this.innerHTML = '<i class="fas fa-play-circle me-2"></i>Start Tracking';
                this.classList.replace('btn-danger', 'btn-success');
                
                stopRealTimeTracking();
            }
        });
    }
}

// Functions for real-time tracking
function startRealTimeTracking() {
    // In a real app, this would initialize geolocation tracking
    console.log('Starting real-time tracking...');
    
    // Show tracking status
    const trackingStatus = document.getElementById('tracking-status');
    if (trackingStatus) {
        trackingStatus.innerHTML = '<span class="pulse me-2"></span> Tracking in progress...';
        trackingStatus.classList.remove('d-none');
    }
    
    // Fetch API call to backend to start tracking session
    fetch('/api/tracking/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Tracking session started', data);
        // Store tracking ID for updates
        localStorage.setItem('currentTrackingId', data.tracking_id);
        
        // Start position watch in browser
        startPositionWatch();
    })
    .catch(error => {
        console.error('Error starting tracking session:', error);
    });
}

function stopRealTimeTracking() {
    // In a real app, this would stop geolocation tracking
    console.log('Stopping real-time tracking...');
    
    // Hide tracking status
    const trackingStatus = document.getElementById('tracking-status');
    if (trackingStatus) {
        trackingStatus.classList.add('d-none');
    }
    
    // Stop position watch
    stopPositionWatch();
    
    // Fetch API call to backend to end tracking session
    const trackingId = localStorage.getItem('currentTrackingId');
    
    fetch('/api/tracking/end', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tracking_id: trackingId
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Tracking session ended', data);
        // Clear tracking ID
        localStorage.removeItem('currentTrackingId');
    })
    .catch(error => {
        console.error('Error ending tracking session:', error);
    });
}

// Geolocation tracking
let positionWatchId = null;

function startPositionWatch() {
    if (navigator.geolocation) {
        positionWatchId = navigator.geolocation.watchPosition(
            updatePosition,
            handlePositionError,
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }
}

function stopPositionWatch() {
    if (positionWatchId !== null) {
        navigator.geolocation.clearWatch(positionWatchId);
        positionWatchId = null;
    }
}

function updatePosition(position) {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const accuracy = position.coords.accuracy;
    const speed = position.coords.speed || 0;
    
    console.log(`Position update: ${lat}, ${lng} (accuracy: ${accuracy}m, speed: ${speed}m/s)`);
    
    // Update tracking UI if it exists
    const positionDisplay = document.getElementById('current-position');
    if (positionDisplay) {
        positionDisplay.textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
    
    const speedDisplay = document.getElementById('current-speed');
    if (speedDisplay) {
        // Convert m/s to km/h
        const speedKmh = (speed * 3.6).toFixed(1);
        speedDisplay.textContent = `${speedKmh} km/h`;
    }
    
    // Send position update to server
    sendPositionUpdate({
        lat,
        lng,
        accuracy,
        speed,
        timestamp: new Date().toISOString()
    });
}

function handlePositionError(error) {
    console.error('Geolocation error:', error.message);
    
    // Show error in UI
    const trackingStatus = document.getElementById('tracking-status');
    if (trackingStatus) {
        trackingStatus.innerHTML = `<i class="fas fa-exclamation-triangle text-warning me-2"></i> Location error: ${error.message}`;
    }
}

function sendPositionUpdate(positionData) {
    const trackingId = localStorage.getItem('currentTrackingId');
    
    // Store in local IndexedDB/localStorage for offline support
    storePositionLocally(trackingId, positionData);
    
    // Only send to server if online
    if (isOnline()) {
        fetch('/api/tracking/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tracking_id: trackingId,
                position: positionData
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Position update sent to server');
        })
        .catch(error => {
            console.error('Error sending position update:', error);
        });
    }
}

// Local storage for offline support
function storePositionLocally(trackingId, positionData) {
    // In a real app, this would use IndexedDB
    // For simplicity, we'll use localStorage here
    
    let trackingData = localStorage.getItem(`tracking_${trackingId}`);
    
    if (trackingData) {
        try {
            trackingData = JSON.parse(trackingData);
            trackingData.positions.push(positionData);
            localStorage.setItem(`tracking_${trackingId}`, JSON.stringify(trackingData));
        } catch (e) {
            console.error('Error storing position locally:', e);
        }
    } else {
        // Initialize tracking data
        const newTrackingData = {
            id: trackingId,
            start_time: new Date().toISOString(),
            positions: [positionData]
        };
        localStorage.setItem(`tracking_${trackingId}`, JSON.stringify(newTrackingData));
    }
}

// Initialize file upload handling
function initializeFileUpload() {
    const fileUpload = document.getElementById('file-upload');
    const uploadArea = document.getElementById('upload-area');
    
    if (fileUpload && uploadArea) {
        uploadArea.addEventListener('click', () => {
            fileUpload.click();
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-primary');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-primary');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-primary');
            
            if (e.dataTransfer.files.length) {
                fileUpload.files = e.dataTransfer.files;
                handleFileSelection(e.dataTransfer.files[0]);
            }
        });
        
        fileUpload.addEventListener('change', () => {
            if (fileUpload.files.length) {
                handleFileSelection(fileUpload.files[0]);
            }
        });
    }
}

function handleFileSelection(file) {
    const preview = document.getElementById('media-preview');
    const uploadForm = document.getElementById('upload-form');
    
    if (preview && file) {
        // Show preview of image or video
        const fileType = file.type.split('/')[0];
        
        if (fileType === 'image') {
            preview.innerHTML = `<img src="${URL.createObjectURL(file)}" class="img-fluid rounded" alt="Preview">`;
        } else if (fileType === 'video') {
            preview.innerHTML = `
                <video controls class="img-fluid rounded">
                    <source src="${URL.createObjectURL(file)}" type="${file.type}">
                    Your browser does not support the video tag.
                </video>
            `;
        } else {
            preview.innerHTML = `<div class="alert alert-warning">File type not supported for preview.</div>`;
        }
        
        // Set file type in form
        const fileTypeInput = document.getElementById('file-type');
        if (fileTypeInput) {
            fileTypeInput.value = fileType;
        }
        
        // Show upload button
        const uploadButton = document.getElementById('upload-button');
        if (uploadButton) {
            uploadButton.classList.remove('d-none');
        }
    }
}

// Initialize notification registration
function initializeNotifications() {
    const enableNotificationsBtn = document.getElementById('enable-notifications');
    
    if (enableNotificationsBtn) {
        enableNotificationsBtn.addEventListener('click', () => {
            registerForPushNotifications();
        });
    }
}

function registerForPushNotifications() {
    // Check if browser supports notifications
    if (!('Notification' in window)) {
        alert('This browser does not support desktop notifications');
        return;
    }
    
    // Request permission
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            // Get push subscription
            subscribeToPushManager();
        } else {
            alert('Notification permission denied');
        }
    });
}

function subscribeToPushManager() {
    // In a real app, this would use the Push API
    console.log('Subscribing to push notifications...');
    
    // In this example, we'll just simulate a device token
    const deviceToken = 'simulated-device-token-' + Math.random().toString(36).substring(2, 15);
    
    // Register with server
    fetch('/api/notifications/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: deviceToken,
            platform: 'web'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Registered for push notifications', data);
        
        // Show success message
        alert('Successfully registered for notifications!');
        
        // Store token locally
        localStorage.setItem('pushNotificationToken', deviceToken);
    })
    .catch(error => {
        console.error('Error registering for push notifications:', error);
    });
}

// Initialize document
document.addEventListener('DOMContentLoaded', function() {
    // Check online status
    updateOnlineStatus();
    
    // Initialize tracking functionality
    initializeTracking();
    
    // Initialize file upload
    initializeFileUpload();
    
    // Initialize notifications
    initializeNotifications();
    
    // Add responsive behavior for sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }
    
    console.log('EcoCycle web dashboard initialized');
});
