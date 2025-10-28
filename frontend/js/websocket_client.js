/**
 * WebSocket client for real-time communication with backend
 */
class WebSocketClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.wasConnected = false; // Track if we ever successfully connected

        // Callbacks
        this.onConnectedCallback = null;
        this.onDisconnectedCallback = null;
        this.onSegmentationCallback = null;
        this.onErrorCallback = null;
        this.onStatsCallback = null;

        // State
        this.serverUrl = this.getWebSocketUrl();
        this.classLabels = [];
        this.availableModels = [];

        // Performance optimization
        this.pendingFrames = 0;
        this.maxPendingFrames = 2; // Drop frames if backend is too slow
        this.lastFrameTime = 0;
        this.minFrameInterval = 33; // Min 33ms between frames (~30 FPS max)
        this.useBinaryFrames = true; // Use binary WebSocket for better performance
    }

    /**
     * Get WebSocket URL - can be configured or use default
     */
    getWebSocketUrl(customUrl = null) {
        if (customUrl) {
            // Clean up the URL
            let cleanUrl = customUrl.trim();

            // Remove trailing slash if present
            cleanUrl = cleanUrl.replace(/\/$/, '');

            // Add /ws endpoint if not present
            if (!cleanUrl.endsWith('/ws')) {
                cleanUrl = cleanUrl + '/ws';
            }

            // Convert http/https to ws/wss
            if (cleanUrl.startsWith('https://')) {
                cleanUrl = cleanUrl.replace('https://', 'wss://');
            } else if (cleanUrl.startsWith('http://')) {
                cleanUrl = cleanUrl.replace('http://', 'ws://');
            } else if (!cleanUrl.startsWith('ws://') && !cleanUrl.startsWith('wss://')) {
                // No protocol specified, assume https (ngrok uses https)
                cleanUrl = 'wss://' + cleanUrl;
            }

            console.log(`🔗 Backend URL converted: ${customUrl} → ${cleanUrl}`);
            return cleanUrl;
        }

        // Default: use current page location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws`;
    }

    /**
     * Connect to WebSocket server
     */
    async connect(customUrl = null) {
        if (this.isConnected) {
            console.warn('Already connected');
            return Promise.resolve();
        }

        // Update server URL if custom URL provided
        if (customUrl) {
            this.serverUrl = this.getWebSocketUrl(customUrl);
        }

        // Return a promise that resolves when connected or rejects on error
        return new Promise((resolve, reject) => {
            const connectionTimeout = 10000; // 10 second timeout
            let timeoutId;

            try {
                console.log(`Connecting to ${this.serverUrl}...`);

                this.ws = new WebSocket(this.serverUrl);

                // Set up connection timeout
                timeoutId = setTimeout(() => {
                    if (this.ws && this.ws.readyState !== WebSocket.OPEN) {
                        this.ws.close();
                        reject(new Error('Connection timeout - server did not respond within 10 seconds'));
                    }
                }, connectionTimeout);

                // Set up event handlers
                this.ws.onopen = () => {
                    clearTimeout(timeoutId);
                    this.handleOpen();
                    resolve(); // Resolve promise on successful connection
                };

                this.ws.onmessage = (event) => this.handleMessage(event);

                this.ws.onerror = (error) => {
                    clearTimeout(timeoutId);
                    this.handleError(error);
                    reject(new Error('WebSocket connection failed')); // Reject promise on error
                };

                this.ws.onclose = () => this.handleClose();

            } catch (error) {
                clearTimeout(timeoutId);
                console.error('Connection failed:', error);
                if (this.onErrorCallback) {
                    this.onErrorCallback('CONNECTION_FAILED', error.message);
                }
                reject(error);
            }
        });
    }

    /**
     * Handle WebSocket open
     */
    handleOpen() {
        console.log('✅ WebSocket connected successfully');
        this.isConnected = true;
        this.wasConnected = true; // Mark that we successfully connected
        this.reconnectAttempts = 0;

        if (this.onConnectedCallback) {
            this.onConnectedCallback();
        }
    }

    /**
     * Handle incoming messages
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            const msgType = data.type;

            switch (msgType) {
                case 'connected':
                    this.handleConnectedMessage(data);
                    break;

                case 'segmentation':
                    // Mark frame as processed
                    this.pendingFrames = Math.max(0, this.pendingFrames - 1);

                    if (this.onSegmentationCallback) {
                        this.onSegmentationCallback(data);
                    }
                    break;

                case 'stats':
                    if (this.onStatsCallback) {
                        this.onStatsCallback(data);
                    }
                    break;

                case 'error':
                    console.error('Server error:', data.message);
                    if (this.onErrorCallback) {
                        this.onErrorCallback(data.code, data.message);
                    }
                    break;

                case 'mode_changed':
                    console.log('Model mode changed:', data.model_mode);
                    this.classLabels = data.class_labels || [];
                    break;

                case 'viz_updated':
                    console.log('Visualization updated:', data.settings);
                    break;

                default:
                    console.log('Unknown message type:', msgType);
            }
        } catch (error) {
            console.error('Failed to parse message:', error);
        }
    }

    /**
     * Handle connected message from server
     */
    handleConnectedMessage(data) {
        console.log('Server ready:', data.status);
        this.classLabels = data.class_labels || [];
        this.availableModels = data.available_models || [];

        console.log('Available models:', this.availableModels);
        console.log('Class labels:', this.classLabels.length);
    }

    /**
     * Handle WebSocket error
     */
    handleError(error) {
        console.error('❌ WebSocket error:', error);
        console.error('❌ Failed to connect to:', this.serverUrl);
        console.error('');
        console.error('💡 Troubleshooting Checklist:');
        console.error('   1. ✓ Backend Running: Check Colab Cell 6 shows "Uvicorn running on http://0.0.0.0:8000"');
        console.error('   2. ✓ ngrok Active: Verify ngrok URL in Cell 7 matches what you entered');
        console.error('   3. ✓ URL Format: Should be https://xxx.ngrok-free.dev (no /ws suffix needed)');
        console.error('   4. ✓ Network: Check your internet connection');
        console.error('   5. ✓ Browser Console: Look for CORS or mixed content errors');
        console.error('');

        // Determine likely cause based on URL
        let troubleshootMsg = 'Connection failed. ';
        if (this.serverUrl.includes('ngrok')) {
            troubleshootMsg += 'Check that ngrok tunnel is active in Colab and URL is correct.';
        } else if (this.serverUrl.includes('localhost') || this.serverUrl.includes('127.0.0.1')) {
            troubleshootMsg += 'Check that backend server is running locally.';
        } else {
            troubleshootMsg += 'Check that backend server is running and URL is correct.';
        }

        if (this.onErrorCallback) {
            this.onErrorCallback('WEBSOCKET_ERROR', troubleshootMsg);
        }
    }

    /**
     * Handle WebSocket close
     */
    handleClose() {
        console.log('WebSocket disconnected');
        this.isConnected = false;

        if (this.onDisconnectedCallback) {
            this.onDisconnectedCallback();
        }

        // Only attempt auto-reconnection if we were previously connected
        // This prevents repeated failed connection attempts on initial connection failure
        if (this.wasConnected && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else if (!this.wasConnected) {
            console.log('Initial connection failed - not attempting auto-reconnect');
        } else {
            console.log('Max reconnection attempts reached');
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.ws) {
            this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
            this.wasConnected = false; // Reset connection tracking
            this.ws.close();
            this.ws = null;
        }

        this.isConnected = false;
        console.log('Disconnected from server');
    }

    /**
     * Send video frame to server with smart throttling
     */
    sendFrame(frameData, timestamp) {
        if (!this.isConnected || !this.ws) {
            console.warn('Not connected, cannot send frame');
            return;
        }

        // Frame skipping: drop if backend is too slow
        if (this.pendingFrames >= this.maxPendingFrames) {
            console.debug('Dropping frame - backend busy');
            return;
        }

        // Rate limiting: enforce minimum interval between frames
        const now = Date.now();
        if (now - this.lastFrameTime < this.minFrameInterval) {
            return;
        }
        this.lastFrameTime = now;

        this.pendingFrames++;

        const message = {
            type: 'frame',
            data: frameData,
            timestamp: timestamp
        };

        this.ws.send(JSON.stringify(message));
    }

    /**
     * Change model mode
     */
    changeMode(modelMode) {
        if (!this.isConnected || !this.ws) {
            console.warn('Not connected, cannot change mode');
            return;
        }

        const message = {
            type: 'change_mode',
            model_mode: modelMode
        };

        this.ws.send(JSON.stringify(message));
        console.log('Requested mode change to:', modelMode);
    }

    /**
     * Update visualization settings
     */
    updateVisualization(settings) {
        if (!this.isConnected || !this.ws) {
            console.warn('Not connected, cannot update visualization');
            return;
        }

        const message = {
            type: 'update_viz',
            settings: settings
        };

        this.ws.send(JSON.stringify(message));
        console.log('Updated visualization settings:', settings);
    }

    /**
     * Request performance stats
     */
    requestStats() {
        if (!this.isConnected || !this.ws) {
            return;
        }

        const message = {
            type: 'get_stats'
        };

        this.ws.send(JSON.stringify(message));
    }

    /**
     * Set callback for connection events
     */
    onConnected(callback) {
        this.onConnectedCallback = callback;
    }

    onDisconnected(callback) {
        this.onDisconnectedCallback = callback;
    }

    onSegmentation(callback) {
        this.onSegmentationCallback = callback;
    }

    onError(callback) {
        this.onErrorCallback = callback;
    }

    onStats(callback) {
        this.onStatsCallback = callback;
    }

    /**
     * Get class labels
     */
    getClassLabels() {
        return this.classLabels;
    }

    /**
     * Get available models
     */
    getAvailableModels() {
        return this.availableModels;
    }
}
