/**
 * Canvas renderer for displaying segmentation results
 */
class CanvasRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.currentImage = null;
    }

    /**
     * Render segmentation result on canvas
     */
    renderSegmentation(base64Data) {
        const img = new Image();

        img.onload = () => {
            // Clear canvas first
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            // Scale image to fit canvas while maintaining aspect ratio
            const canvasAspect = this.canvas.width / this.canvas.height;
            const imgAspect = img.width / img.height;

            let drawWidth, drawHeight, offsetX = 0, offsetY = 0;

            if (imgAspect > canvasAspect) {
                // Image is wider - fit to width
                drawWidth = this.canvas.width;
                drawHeight = this.canvas.width / imgAspect;
                offsetY = (this.canvas.height - drawHeight) / 2;
            } else {
                // Image is taller - fit to height
                drawHeight = this.canvas.height;
                drawWidth = this.canvas.height * imgAspect;
                offsetX = (this.canvas.width - drawWidth) / 2;
            }

            // Draw the segmented image scaled to fit
            this.ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);

            this.currentImage = img;
        };

        img.onerror = (error) => {
            console.error('Failed to load segmentation image:', error);
        };

        // Handle data URL format
        if (!base64Data.startsWith('data:')) {
            img.src = `data:image/jpeg;base64,${base64Data}`;
        } else {
            img.src = base64Data;
        }
    }

    /**
     * Clear canvas
     */
    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Draw loading state
     */
    drawLoading() {
        this.clear();

        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '24px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(
            'Processing...',
            this.canvas.width / 2,
            this.canvas.height / 2
        );
    }

    /**
     * Draw error state
     */
    drawError(message) {
        this.clear();

        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = '#ff0000';
        this.ctx.font = '20px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(
            'Error: ' + message,
            this.canvas.width / 2,
            this.canvas.height / 2
        );
    }

    /**
     * Get canvas dimensions
     */
    getDimensions() {
        return {
            width: this.canvas.width,
            height: this.canvas.height
        };
    }
}
