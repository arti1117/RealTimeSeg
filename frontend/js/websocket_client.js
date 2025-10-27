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
    }

    /**
     * Get WebSocket URL - can be configured or use default
     */
    getWebSocketUrl(customUrl = null) {
        if (customUrl) {
            // Use custom URL (e.g., ngrok URL from Colab)
            // Ensure it has the /ws endpoint
            const url = customUrl.endsWith('/ws') ? customUrl : `${customUrl}/ws`;
            // Convert http to ws, https to wss
            return url.replace(/^http/, 'ws');
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
            return;
        }

        // Update server URL if custom URL provided
        if (customUrl) {
            this.serverUrl = this.getWebSocketUrl(customUrl);
        }

        try {
            console.log(`Connecting to ${this.serverUrl}...`);

            this.ws = new WebSocket(this.serverUrl);

            // Set up event handlers
            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onerror = (error) => this.handleError(error);
            this.ws.onclose = () => this.handleClose();

        } catch (error) {
            console.error('Connection failed:', error);
            if (this.onErrorCallback) {
                this.onErrorCallback('CONNECTION_FAILED', error.message);
            }
        }
    }

    /**
     * Handle WebSocket open
     */
    handleOpen() {
        console.log('WebSocket connected');
        this.isConnected = true;
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
        console.error('WebSocket error:', error);

        if (this.onErrorCallback) {
            this.onErrorCallback('WEBSOCKET_ERROR', 'Connection error occurred');
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

        // Attempt reconnection
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})...`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.ws) {
            this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
            this.ws.close();
            this.ws = null;
        }

        this.isConnected = false;
        console.log('Disconnected from server');
    }

    /**
     * Send video frame to server
     */
    sendFrame(frameData, timestamp) {
        if (!this.isConnected || !this.ws) {
            console.warn('Not connected, cannot send frame');
            return;
        }

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
