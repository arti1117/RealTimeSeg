# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real-time semantic segmentation system with GPU-accelerated inference and WebSocket streaming. Portfolio demo showcasing full-stack ML deployment with FastAPI backend and vanilla JavaScript frontend.

**Tech Stack**: PyTorch 2.8.0 • FastAPI 0.104+ • WebSocket • Vanilla JS • Google Colab

## Development Commands

### Backend Server

```bash
# Setup (from project root)
cd backend
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# Run server (default: http://localhost:8000)
python app.py

# Alternative: Run with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Check server health
curl http://localhost:8000/health

# Run tests
python tests/test_websocket_fixes.py
```

### Frontend Development

```bash
# Start local HTTP server for frontend (from project root)
./scripts/start_frontend.sh        # Linux/Mac
scripts\start_frontend.bat         # Windows

# Stop frontend server when done
./scripts/stop_frontend.sh         # Linux/Mac
scripts\stop_frontend.bat          # Windows
```

### Model Operations

```python
# Pre-download models (optional, auto-downloads on first use)
python -c "
import torchvision.models.segmentation as models
from transformers import SegformerForSemanticSegmentation
models.deeplabv3_mobilenet_v3_large(pretrained=True)
models.deeplabv3_resnet50(pretrained=True)
SegformerForSemanticSegmentation.from_pretrained('nvidia/segformer-b3-finetuned-ade-512-512')
"

# Check GPU availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

### Google Colab Deployment

Use `notebooks/colab_deployment.ipynb` for cloud deployment with free GPU access. Requires ngrok token from https://ngrok.com.

## Architecture Overview

### Split Architecture Pattern

Backend and frontend run **separately** - backend provides WebSocket API, frontend served independently (local HTTP server or static hosting).

**Backend (FastAPI)**: `backend/app.py` port 8000
**Frontend (Vanilla JS)**: `frontend/index.html` separate server

### Critical WebSocket Flow (PERFORMANCE OPTIMIZED)

**The network layer was the main bottleneck** - Not the GPU inference. Original implementation sent 1280x720 frames at quality 0.8 = ~150KB/frame = 6MB/s over ngrok (unusable).

**Fix applied**: Downscaling to 640x360 + quality 0.5 = ~25KB/frame = 1MB/s (smooth 20-25 FPS).

```
Frontend                          Backend
────────                          ───────
webcam.captureFrame(0.5, 640)    [downscale to 640px, JPEG quality 0.5]
  ↓
wsClient.sendFrame()              [smart throttling: max 2 pending, 33ms interval]
  ↓
WebSocket → /ws                   manager.connect(websocket)
                                    ↓
                                  inference_engine.predict(frame)
                                    ↓
                                  visualizer.render(mask, mode="filled")
                                    ↓
WebSocket ← segmentation result
  ↓
renderer.renderSegmentation()     [draw on canvas]
```

**See `docs/COMPLETE_PERFORMANCE_GUIDE.md` for detailed optimization breakdown (83% bandwidth reduction, 5x latency improvement).**

### Core Components

#### Backend Architecture (`backend/`)

**Main Application** (`app.py`):
- FastAPI WebSocket server with async frame processing
- `ConnectionManager`: Per-client state management with frame queuing (max queue size: 3)
- Message handlers: `handle_frame()`, `handle_mode_change()`, `handle_viz_update()`
- Global instances: `model_loader`, `frame_processor`, `manager`

**Model Pipeline** (`models/`):
- `ModelLoader`: Loads and caches PyTorch models, applies FP16 optimization on GPU
- `InferenceEngine`: Handles inference with performance tracking, warm-up iterations
- Model caching prevents reload on switching (fast mode changes)

**Utilities** (`utils/`):
- `config.py`: Model profiles (fast/balanced/accurate), server config, class labels
- `frame_processor.py`: Base64 encoding/decoding, preprocessing, postprocessing
- `segmentation_viz.py`: 4 visualization modes (filled, contour, side-by-side, blend)

#### Frontend Architecture (`frontend/`)

**Modular JavaScript** (`js/`):
- `webcam.js`: WebRTC camera access with MediaStream API
- `websocket_client.js`: WebSocket communication with automatic reconnection
- `renderer.js`: Canvas-based rendering with requestAnimationFrame
- `controls.js`: UI state management and event handling

**HTML Structure** (`index.html`):
- Main canvas for video + segmentation display
- Control panel with model selection, visualization modes, opacity slider
- Performance metrics display (FPS, inference time, detected classes)

### Model Profiles

Three performance tiers configured in `backend/utils/config.py`:

| Mode | Model | Input Size | Classes | Target FPS | GPU Memory |
|------|-------|-----------|---------|-----------|-----------|
| fast | DeepLabV3-MobileNetV3 | 512×512 | 21 (COCO) | 30-40 | ~1.2 GB |
| balanced | DeepLabV3-ResNet50 | 640×640 | 21 (COCO) | 20-25 | ~2.5 GB |
| accurate | SegFormer-B3 | 768×768 | 150 (ADE20K) | 10-12 | ~4.5 GB |
| sota | Mask2Former-Swin-Large | 1024×1024 | 150 (ADE20K) | 5-8 | ~6.5 GB |

**Fast/Balanced**: Use `torchvision.models.segmentation` (DeepLabV3)
**Accurate**: Uses `transformers.SegformerForSemanticSegmentation`
**SOTA**: Uses `transformers.Mask2FormerForUniversalSegmentation` (57.7% mIoU on ADE20K)

Models auto-download on first use and cache in `./models/` directory.

### WebSocket Protocol

#### Client → Server Messages

```json
{"type": "frame", "data": "<base64_jpeg>", "timestamp": 1234567890}
{"type": "change_mode", "model_mode": "fast|balanced|accurate"}
{"type": "update_viz", "settings": {"overlay_opacity": 0.6, "visualization_mode": "filled"}}
{"type": "get_stats"}
```

#### Server → Client Messages

```json
{"type": "connected", "status": "ready", "available_models": [...], "class_labels": [...]}
{"type": "segmentation", "data": "<base64_jpeg>", "metadata": {"inference_time_ms": 45.2, "fps": 22.1, "detected_classes": [...]}}
{"type": "mode_changed", "model_mode": "fast", "class_labels": [...]}
{"type": "error", "code": "ERROR_CODE", "message": "...", "recoverable": true}
```

### Inference Pipeline Flow

1. **Client**: Capture webcam frame → JPEG encode → Base64 → WebSocket send
2. **Server**: Receive → Decode → Preprocess (resize, normalize) → GPU inference → Postprocess mask
3. **Visualization**: Apply selected mode (filled/contour/side-by-side/blend) → JPEG encode → Base64 → WebSocket send
4. **Client**: Receive → Decode → Canvas render → Performance metrics update

**Frame Queue**: Server queues max 3 frames per client to prevent backlog on slow processing.

**Model Warm-up Caching** (CRITICAL FIX): `InferenceEngine` tracks warmed-up models in `self.warmed_up_models` dict. First connection warms up (500-2000ms), subsequent connections skip warm-up (0ms). This prevents redundant initialization on every connection.

```python
# backend/models/inference_engine.py
def warm_up(self, force: bool = False):
    if not force and self.model_loader.is_model_warmed_up(self.current_mode):
        print(f"Model '{self.current_mode}' already warmed up, skipping")
        return
    # ... perform warm-up ...
    self.model_loader.mark_model_warmed_up(self.current_mode)
```

**FP16 Optimization**: Automatically applied on CUDA devices for ~2x speedup with minimal accuracy loss.

## Configuration Files

### Backend Configuration (`backend/utils/config.py`)

**Key Settings**:
- `MODEL_PROFILES`: Define model configs (name, backbone, input_size, num_classes, expected_fps, memory_mb)
- `SERVER_CONFIG`: Host, port, CORS, queue size, default model
- `FRAME_CONFIG`: JPEG quality, PNG compression, max dimensions
- `VIZ_CONFIG`: Default opacity, visualization modes, colormap
- `DEVICE`: Auto-detect CUDA vs CPU from `CUDA_VISIBLE_DEVICES` env var
- `USE_FP16`: Auto-enable on CUDA devices

**Class Labels**:
- `COCO_CLASSES`: 21 classes for fast/balanced modes
- `ADE20K_CLASSES`: 150 classes (abbreviated to 30 in config) for accurate mode

### Important Architecture Patterns

**Async WebSocket Pattern**:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    inference_engine = InferenceEngine(model_loader, frame_processor)
    # Initialize per-client state with inference engine and visualizer
    while True:
        message = await websocket.receive_text()
        await handle_frame(websocket, data)  # Process asynchronously
```

**Per-Client State Management**:
Each WebSocket connection has isolated state including:
- Model mode (fast/balanced/accurate)
- Visualization settings (mode, opacity, class filter)
- Dedicated `InferenceEngine` and `SegmentationVisualizer` instances
- Frame queue for backpressure management

**Model Switching**: Models are pre-loaded and cached, switching changes pointer without reload. Call `warm_up()` after switch.

**Error Recovery**: All errors marked as `recoverable: true` - client can retry without reconnecting.

## Running from Different Directories

**Always run backend server from `backend/` directory**:
```bash
cd backend && python app.py
```

This ensures correct Python module imports (`from models import ModelLoader`, `from utils import config`).

Frontend can be served from any directory but assets use relative paths from `frontend/`.

## Common Development Scenarios

### Adding a New Model Profile

1. Add config to `backend/utils/config.py` in `MODEL_PROFILES`
2. Update `ModelLoader._load_*()` methods if using new model type
3. Update `InferenceEngine.predict()` to handle new model's output format
4. Update warm_up() method in inference engine to handle new model type
5. Add class labels if using different dataset
6. Update Colab notebook to download new model

**Example**: SOTA mode with Mask2Former was added following this pattern

### Changing Visualization Modes

Visualization logic in `backend/utils/segmentation_viz.py`:
- `render()`: Main entry point, dispatches to mode-specific methods
- `_render_filled()`: Transparent colored overlay
- `_render_contour()`: Edge detection with class colors
- `_render_side_by_side()`: Original and segmentation side-by-side
- `_render_blend()`: HSV color space blending

### Performance Optimization

**Network Layer** (Primary bottleneck for ngrok/Colab):
- Frontend: `webcam.js` line 75 → `this.captureFrame(0.5, 640)` controls quality and resolution
- Backend: `utils/config.py` → `FRAME_CONFIG` sets JPEG quality (60) and max dimensions (960x540)
- **For localhost**: Increase to `captureFrame(0.7, 960)` for better quality
- **For slow networks**: Reduce to `captureFrame(0.4, 480)` if laggy

**GPU Memory**: Adjust `input_size` in model profiles (smaller = less memory)
**FPS**: Use fast mode, reduce webcam resolution, or adjust `FRAME_CONFIG.max_width/height`
**Queue Management**: Adjust `SERVER_CONFIG.max_queue_size` (lower = more frame drops but less latency)
**Compression**: Tune `FRAME_CONFIG.jpeg_quality` (lower = faster but lower quality)

**Frame Processing** (`backend/utils/frame_processor.py`):
- Uses `cv2.INTER_AREA` for downscaling (faster than `INTER_LINEAR`)
- In-place normalization: `tensor.div_(255.0)` instead of `tensor / 255.0`
- Contiguous arrays: `np.ascontiguousarray(resized)` for faster processing

### Deployment Patterns

**Local Development**: Backend on localhost:8000, frontend on separate local server
**Google Colab**: Backend with ngrok tunnel, frontend connects to public URL
**Production**: Backend on cloud server (AWS/GCP), frontend on CDN/static hosting

Frontend needs backend WebSocket URL - configurable via custom URL input in UI.

## Documentation References

- **Technical Specification**: `docs/TECHNICAL_SPECIFICATION.md` - Complete system design
- **Setup Guide**: `SETUP.md` - Installation and troubleshooting
- **Backend API**: `backend/README.md` - WebSocket API reference
- **WebSocket Connection Fix**: `docs/WEBSOCKET_CONNECTION_FIX.md` - Connection troubleshooting (RECENT FIX)
- **Performance Guide**: `docs/COMPLETE_PERFORMANCE_GUIDE.md` - Optimization details (83% bandwidth reduction)
- **Deployment Docs**: `docs/` - Colab deployment, troubleshooting, architecture guides

## Project Structure Notes

```
backend/
  app.py                    # Main WebSocket server entrypoint
  models/                   # ML model loading and inference
    model_loader.py         # Model management and caching
    inference_engine.py     # Inference with performance tracking
  utils/                    # Utilities and configuration
    config.py               # Central configuration (models, server, viz)
    frame_processor.py      # Image encoding/decoding
    segmentation_viz.py     # Visualization rendering

frontend/
  index.html                # Main UI
  js/                       # Modular JavaScript components
    webcam.js               # Camera capture
    websocket_client.js     # WebSocket communication
    renderer.js             # Canvas rendering
    controls.js             # UI controls

models/                     # Model cache directory (auto-created)
notebooks/                  # Google Colab deployment notebook
docs/                       # Detailed documentation (deployment, troubleshooting)
scripts/                    # Utility scripts (frontend server, git helpers)
```

## Known Constraints

- **Python 3.10+** required for backend
- **CUDA-capable GPU** strongly recommended (CPU mode supported but slow)
- **Browser compatibility**: Chrome/Edge recommended, Firefox good, Safari partial WebSocket support
- **Google Colab**: 90-minute idle timeout, 12-hour max session
- **Model downloads**: ~3GB total for all three models on first run
- **WebSocket connection**: Frontend must be able to reach backend URL (firewall/CORS considerations)

## Common Issues

### "Failed to connect" Error (FIXED 2025-10-28)

**Problem**: Users experiencing repeated "Failed to connect" errors when connecting to backend, especially over ngrok.

**Root Cause**: The `connect()` method in `frontend/js/websocket_client.js` returned immediately without waiting for WebSocket to open. Frontend waited 1 second and checked `isConnected`, but ngrok connections took 2-5 seconds.

**Solution Applied** (`frontend/js/websocket_client.js` lines 71-126):
- Made `connect()` return a Promise that resolves on `onopen` event
- Added 10-second connection timeout
- Smart auto-reconnect: only retry if `wasConnected` flag is true (prevents spam on initial failure)

**Controls.js integration** (`frontend/js/controls.js` lines 107-144):
```javascript
try {
    await this.wsClient.connect(backendUrl || null);  // Now properly waits
    this.webcam.startCapture(...);  // Only starts if connected
} catch (error) {
    this.showError(`Failed to connect: ${error.message}`);
}
```

**Troubleshooting checklist**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify ngrok URL format: `https://xxx.ngrok-free.dev` (no /ws suffix, no trailing slash)
3. Check browser console for detailed WebSocket errors
4. Ensure ngrok tunnel is active (Colab Cell 7 for Colab deployment)

**See `docs/WEBSOCKET_CONNECTION_FIX.md` for comprehensive troubleshooting guide.**

### Frontend: "Address already in use" (Port 8080)

**Error**: `OSError: [Errno 98] Address already in use`

**Cause**: A previous frontend server instance is still running on port 8080

**Solution**: Stop the existing server before starting a new one:
```bash
./scripts/stop_frontend.sh         # Linux/Mac
scripts\stop_frontend.bat          # Windows
```

Then start the frontend server again.

### Mask2Former Special Handling

**Issue**: Mask2Former returns `Mask2FormerForUniversalSegmentationOutput` with semantic map in `.semantic_segmentation` attribute, NOT standard `logits` or `out` keys.

**Solution** (`backend/models/inference_engine.py` lines 180-187):
```python
if self.current_mode == "sota":
    outputs = self.current_model(pixel_values=tensor)
    semantic_map = outputs.semantic_segmentation  # ← Special attribute
    mask = torch.argmax(semantic_map, dim=0)
```

Other models (fast/balanced/accurate) use standard `.out` or direct logits.

### ngrok Tunnel "Endpoint Already Online"

**Error**: `ERR_NGROK_334: endpoint already online`

**Cause**: Trying to create duplicate ngrok tunnel with same custom domain

**Solution**: Notebook Cell 4.5 has manual cleanup:
```python
import pyngrok.ngrok as ngrok
ngrok.kill()
time.sleep(2)
```

Or use the safe tunnel creation in Cell 5 (auto-detects and reuses existing tunnels).
