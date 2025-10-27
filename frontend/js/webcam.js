/**
 * Webcam capture and frame management
 */
class WebcamCapture {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.video = document.createElement('video');
        this.stream = null;
        this.isCapturing = false;
        this.frameRate = 30; // Target frame rate
        this.captureInterval = null;
        this.onFrameCallback = null;

        // Video constraints
        this.constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };
    }

    /**
     * Initialize webcam and start video stream
     */
    async init() {
        try {
            console.log('Requesting webcam access...');
            this.stream = await navigator.mediaDevices.getUserMedia(this.constraints);

            this.video.srcObject = this.stream;
            this.video.autoplay = true;
            this.video.playsInline = true;

            // Wait for video to be ready
            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    console.log(`Webcam initialized: ${this.video.videoWidth}x${this.video.videoHeight}`);

                    // Set canvas size to match video
                    this.canvas.width = this.video.videoWidth;
                    this.canvas.height = this.video.videoHeight;

                    resolve();
                };
            });

            return true;
        } catch (error) {
            console.error('Failed to initialize webcam:', error);
            alert('Failed to access webcam. Please check permissions.');
            return false;
        }
    }

    /**
     * Start capturing frames
     */
    startCapture(onFrameCallback) {
        if (this.isCapturing) {
            console.warn('Already capturing');
            return;
        }

        this.onFrameCallback = onFrameCallback;
        this.isCapturing = true;

        const intervalMs = 1000 / this.frameRate;

        this.captureInterval = setInterval(() => {
            this.captureFrame();
        }, intervalMs);

        console.log(`Started capturing at ${this.frameRate} FPS`);
    }

    /**
     * Stop capturing frames
     */
    stopCapture() {
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }

        this.isCapturing = false;
        console.log('Stopped capturing');
    }

    /**
     * Capture a single frame
     */
    captureFrame() {
        if (!this.video || !this.video.videoWidth) {
            return;
        }

        // Draw video frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Get frame data as JPEG
        const frameData = this.canvas.toDataURL('image/jpeg', 0.8);

        // Call callback with frame data
        if (this.onFrameCallback) {
            this.onFrameCallback(frameData, Date.now());
        }
    }

    /**
     * Clean up resources
     */
    cleanup() {
        this.stopCapture();

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.video) {
            this.video.srcObject = null;
        }

        console.log('Webcam cleanup complete');
    }

    /**
     * Set target frame rate
     */
    setFrameRate(fps) {
        const wasCapturing = this.isCapturing;
        const callback = this.onFrameCallback;

        if (wasCapturing) {
            this.stopCapture();
        }

        this.frameRate = fps;

        if (wasCapturing && callback) {
            this.startCapture(callback);
        }

        console.log(`Frame rate set to ${fps} FPS`);
    }

    /**
     * Get current video dimensions
     */
    getDimensions() {
        return {
            width: this.video.videoWidth,
            height: this.video.videoHeight
        };
    }

    /**
     * Check if webcam is active
     */
    isActive() {
        return this.stream !== null && this.stream.active;
    }
}
