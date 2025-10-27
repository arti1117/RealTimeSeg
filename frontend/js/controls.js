/**
 * UI controls manager
 */
class ControlsManager {
    constructor(webcam, wsClient, renderer) {
        this.webcam = webcam;
        this.wsClient = wsClient;
        this.renderer = renderer;

        // UI elements
        this.elements = {
            btnConnect: document.getElementById('btn-connect'),
            btnDisconnect: document.getElementById('btn-disconnect'),
            statusDot: document.getElementById('status-dot'),
            statusText: document.getElementById('status-text'),
            loading: document.getElementById('loading'),
            modelMode: document.getElementById('model-mode'),
            vizButtons: document.querySelectorAll('.btn-viz'),
            opacitySlider: document.getElementById('opacity-slider'),
            opacityValue: document.getElementById('opacity-value'),
            statFps: document.getElementById('stat-fps'),
            statInference: document.getElementById('stat-inference'),
            statClasses: document.getElementById('stat-classes'),
            classLegend: document.getElementById('class-legend')
        };

        // State
        this.currentVizMode = 'filled';
        this.currentOpacity = 0.6;

        // Initialize
        this.setupEventListeners();
        this.setupWebSocketCallbacks();
    }

    /**
     * Setup UI event listeners
     */
    setupEventListeners() {
        // Connect button
        this.elements.btnConnect.addEventListener('click', () => {
            this.handleConnect();
        });

        // Disconnect button
        this.elements.btnDisconnect.addEventListener('click', () => {
            this.handleDisconnect();
        });

        // Model mode selector
        this.elements.modelMode.addEventListener('change', (e) => {
            this.handleModelModeChange(e.target.value);
        });

        // Visualization mode buttons
        this.elements.vizButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.handleVizModeChange(btn.dataset.mode);
            });
        });

        // Opacity slider
        this.elements.opacitySlider.addEventListener('input', (e) => {
            this.handleOpacityChange(e.target.value);
        });
    }

    /**
     * Setup WebSocket callbacks
     */
    setupWebSocketCallbacks() {
        // Connected callback
        this.wsClient.onConnected(() => {
            console.log('Connected to server');
            this.updateConnectionStatus('connected');
            this.hideLoading();
        });

        // Disconnected callback
        this.wsClient.onDisconnected(() => {
            console.log('Disconnected from server');
            this.updateConnectionStatus('disconnected');
            this.webcam.stopCapture();
        });

        // Segmentation result callback
        this.wsClient.onSegmentation((data) => {
            this.handleSegmentationResult(data);
        });

        // Error callback
        this.wsClient.onError((code, message) => {
            console.error(`Error [${code}]:`, message);
            this.showError(message);
        });

        // Stats callback
        this.wsClient.onStats((data) => {
            this.updateStats(data);
        });
    }

    /**
     * Handle connect button
     */
    async handleConnect() {
        this.showLoading('Connecting...');

        // Initialize webcam
        const webcamReady = await this.webcam.init();
        if (!webcamReady) {
            this.hideLoading();
            this.showError('Failed to initialize webcam');
            return;
        }

        // Connect to WebSocket
        await this.wsClient.connect();

        // Wait a bit for connection
        await new Promise(resolve => setTimeout(resolve, 1000));

        if (this.wsClient.isConnected) {
            // Start capturing frames
            this.webcam.startCapture((frameData, timestamp) => {
                this.wsClient.sendFrame(frameData, timestamp);
            });

            // Enable/disable buttons
            this.elements.btnConnect.disabled = true;
            this.elements.btnDisconnect.disabled = false;

            // Start stats polling
            this.startStatsPolling();
        } else {
            this.hideLoading();
            this.showError('Failed to connect to server');
        }
    }

    /**
     * Handle disconnect button
     */
    handleDisconnect() {
        // Stop webcam capture
        this.webcam.cleanup();

        // Disconnect WebSocket
        this.wsClient.disconnect();

        // Stop stats polling
        this.stopStatsPolling();

        // Clear canvas
        this.renderer.clear();

        // Enable/disable buttons
        this.elements.btnConnect.disabled = false;
        this.elements.btnDisconnect.disabled = true;

        // Update UI
        this.updateConnectionStatus('disconnected');
        this.clearStats();
    }

    /**
     * Handle model mode change
     */
    handleModelModeChange(mode) {
        console.log('Changing model mode to:', mode);
        this.wsClient.changeMode(mode);
        this.showLoading('Switching model...');

        // Hide loading after a delay
        setTimeout(() => {
            this.hideLoading();
        }, 2000);
    }

    /**
     * Handle visualization mode change
     */
    handleVizModeChange(mode) {
        console.log('Changing visualization mode to:', mode);

        // Update button states
        this.elements.vizButtons.forEach(btn => {
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        this.currentVizMode = mode;

        // Send update to server
        this.wsClient.updateVisualization({
            visualization_mode: mode
        });
    }

    /**
     * Handle opacity change
     */
    handleOpacityChange(value) {
        const opacity = value / 100;
        this.currentOpacity = opacity;

        // Update display
        this.elements.opacityValue.textContent = `${value}%`;

        // Send update to server
        this.wsClient.updateVisualization({
            overlay_opacity: opacity
        });
    }

    /**
     * Handle segmentation result
     */
    handleSegmentationResult(data) {
        // Render segmentation
        this.renderer.renderSegmentation(data.data);

        // Update stats
        if (data.metadata) {
            this.updateStats(data.metadata);

            // Update detected classes
            if (data.metadata.detected_classes) {
                this.updateClassLegend(data.metadata.detected_classes);
            }
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(status) {
        this.elements.statusDot.className = `status-dot ${status}`;

        const statusText = {
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'connecting': 'Connecting...'
        };

        this.elements.statusText.textContent = statusText[status] || status;
    }

    /**
     * Show loading overlay
     */
    showLoading(message = 'Loading...') {
        this.elements.loading.classList.remove('hidden');
        const loadingText = this.elements.loading.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        this.elements.loading.classList.add('hidden');
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
    }

    /**
     * Update performance stats
     */
    updateStats(stats) {
        if (stats.fps !== undefined) {
            this.elements.statFps.textContent = stats.fps.toFixed(1);
        }

        if (stats.inference_time_ms !== undefined) {
            this.elements.statInference.textContent = `${stats.inference_time_ms.toFixed(1)} ms`;
        } else if (stats.avg_inference_ms !== undefined) {
            this.elements.statInference.textContent = `${stats.avg_inference_ms.toFixed(1)} ms`;
        }
    }

    /**
     * Clear stats display
     */
    clearStats() {
        this.elements.statFps.textContent = '0';
        this.elements.statInference.textContent = '0 ms';
        this.elements.statClasses.textContent = '-';
        this.elements.classLegend.innerHTML = '<p class="help-text">No classes detected yet</p>';
    }

    /**
     * Update class legend
     */
    updateClassLegend(classes) {
        if (!classes || classes.length === 0) {
            this.elements.classLegend.innerHTML = '<p class="help-text">No classes detected</p>';
            this.elements.statClasses.textContent = '0';
            return;
        }

        // Update class count
        this.elements.statClasses.textContent = classes.length;

        // Update legend
        this.elements.classLegend.innerHTML = classes
            .map(className => `
                <div class="class-item">
                    <div class="class-color" style="background: ${this.getColorForClass(className)}"></div>
                    <span>${className}</span>
                </div>
            `)
            .join('');
    }

    /**
     * Get color for class (simple hash-based color generation)
     */
    getColorForClass(className) {
        // Simple hash function
        let hash = 0;
        for (let i = 0; i < className.length; i++) {
            hash = className.charCodeAt(i) + ((hash << 5) - hash);
        }

        // Convert to color
        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 70%, 60%)`;
    }

    /**
     * Start periodic stats polling
     */
    startStatsPolling() {
        this.statsInterval = setInterval(() => {
            this.wsClient.requestStats();
        }, 2000); // Every 2 seconds
    }

    /**
     * Stop stats polling
     */
    stopStatsPolling() {
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
            this.statsInterval = null;
        }
    }
}
