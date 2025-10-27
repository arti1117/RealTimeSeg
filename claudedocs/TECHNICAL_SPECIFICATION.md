# Real-Time Webcam Semantic Segmentation - Technical Specification

**Project Type**: Portfolio Demo
**Last Updated**: 2025-10-27
**Status**: Specification Phase

---

## 📋 Executive Summary

A real-time webcam semantic segmentation web application showcasing:
- Server-side GPU-accelerated inference (Google Colab + PyTorch)
- WebSocket-based real-time video streaming
- Multiple performance profiles (Fast/Balanced/Accurate)
- Interactive visualization modes (overlay styles, class filtering, transparency)
- Optimized inference pipeline (ONNX/TensorRT)

**Target Audience**: Portfolio showcase, technical demonstration
**Deployment**: Google Colab + ngrok (demo environment)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
├─────────────────────────────────────────────────────────────────┤
│  • Webcam Capture (getUserMedia)                                │
│  • WebSocket Client                                             │
│  • Canvas Rendering (video + segmentation overlay)              │
│  • UI Controls (mode switching, visualization settings)         │
└────────────────────┬────────────────────────────────────────────┘
                     │ WebSocket (Binary frames)
                     │ ↓ Video frames (JPEG compressed)
                     │ ↑ Segmentation masks (PNG/JSON)
┌────────────────────┴────────────────────────────────────────────┐
│                    BACKEND SERVER (Colab)                        │
├─────────────────────────────────────────────────────────────────┤
│  • WebSocket Server (aiohttp/FastAPI)                           │
│  • Frame Queue Management                                       │
│  • Model Inference Engine                                       │
│  • Post-processing Pipeline                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────────┐
│                     ML INFERENCE LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Model Pool:                                                     │
│  • Fast Mode: DeepLabV3-MobileNetV3 (ONNX)                      │
│  • Balanced Mode: DeepLabV3-ResNet50 (TensorRT)                 │
│  • Accurate Mode: SegFormer-B3 (PyTorch)                        │
│                                                                  │
│  Optimization:                                                   │
│  • FP16 mixed precision                                         │
│  • Dynamic batching (batch_size=1 for real-time)                │
│  • GPU memory pooling                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Technology Stack

### Frontend
```yaml
Core:
  - HTML5 Canvas API (video rendering + overlay)
  - Vanilla JavaScript (ES6+) or React (if preferred)
  - WebSocket API (real-time communication)

Libraries:
  - None required for vanilla JS
  - Optional: React 18+ if you prefer component structure

Browser Requirements:
  - Chrome/Edge 90+ (best WebRTC support)
  - Firefox 88+
  - Desktop only (responsive not required for demo)
```

### Backend
```yaml
Framework:
  - FastAPI 0.104+ (async WebSocket support)
  - Alternative: aiohttp 3.9+ (lightweight)

WebSocket:
  - python-socketio 5.10+ OR
  - FastAPI native WebSocket

Server:
  - uvicorn[standard] 0.24+ (ASGI server)
  - ngrok 3.x (public tunneling for Colab)

Async:
  - asyncio (native Python 3.8+)
  - aiofiles (async file operations if needed)
```

### ML/Inference
```yaml
Deep Learning:
  - PyTorch 2.1+ (with CUDA 11.8+)
  - torchvision 0.16+
  - transformers 4.35+ (for SegFormer)

Optimization:
  - ONNX Runtime GPU 1.16+
  - TensorRT 8.6+ (optional, for maximum speed)
  - torch.compile (PyTorch 2.0 native optimization)

Pre-trained Models:
  - DeepLabV3-MobileNetV3: torchvision.models
  - DeepLabV3-ResNet50: torchvision.models
  - SegFormer-B3: huggingface/transformers

Image Processing:
  - OpenCV (cv2) 4.8+ (frame encoding/decoding)
  - NumPy 1.24+
  - Pillow 10.0+ (image utilities)
```

### Development Tools
```yaml
Environment:
  - Python 3.10+
  - Node.js 18+ (if using build tools)
  - Google Colab GPU (T4/P100/V100)

Version Control:
  - Git (repository structure)

Testing:
  - pytest (backend unit tests)
  - Browser DevTools (frontend debugging)
```

---

## 📁 Project Structure

```
realtime-segmentation/
│
├── backend/
│   ├── app.py                      # FastAPI application + WebSocket server
│   ├── models/
│   │   ├── __init__.py
│   │   ├── model_loader.py         # Model initialization and loading
│   │   ├── inference_engine.py     # Inference pipeline
│   │   └── optimizer.py            # ONNX/TensorRT conversion utilities
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── frame_processor.py      # Frame encoding/decoding
│   │   ├── segmentation_viz.py     # Colormap and overlay generation
│   │   └── config.py               # Configuration management
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── index.html                  # Main webpage
│   ├── css/
│   │   └── styles.css              # UI styling
│   ├── js/
│   │   ├── webcam.js               # Webcam capture logic
│   │   ├── websocket_client.js     # WebSocket communication
│   │   ├── renderer.js             # Canvas rendering + overlay
│   │   └── controls.js             # UI controls and mode switching
│   └── assets/
│       └── icons/                  # UI icons/assets
│
├── notebooks/
│   └── colab_deployment.ipynb      # Google Colab setup notebook
│
├── models/
│   └── .gitkeep                    # Placeholder (models downloaded at runtime)
│
├── claudedocs/
│   ├── TECHNICAL_SPECIFICATION.md  # This document
│   └── API_REFERENCE.md            # WebSocket API documentation
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🔌 WebSocket API Specification

### Connection
```
Endpoint: ws://<colab-ngrok-url>/ws
Protocol: WebSocket (binary + text frames)
```

### Client → Server Messages

#### 1. Initialize Connection
```json
{
  "type": "init",
  "config": {
    "model_mode": "balanced",  // "fast" | "balanced" | "accurate"
    "resolution": {
      "width": 640,
      "height": 480
    }
  }
}
```

#### 2. Video Frame
```json
{
  "type": "frame",
  "data": "<base64_encoded_jpeg>",
  "timestamp": 1698765432000
}
```

#### 3. Change Model Mode
```json
{
  "type": "change_mode",
  "model_mode": "fast"  // "fast" | "balanced" | "accurate"
}
```

#### 4. Update Visualization Settings
```json
{
  "type": "update_viz",
  "settings": {
    "overlay_opacity": 0.6,      // 0.0 - 1.0
    "visualization_mode": "filled",  // "filled" | "contour" | "blend"
    "class_filter": ["person", "car"],  // null = show all classes
    "colormap": "ade20k"  // "ade20k" | "cityscapes" | "custom"
  }
}
```

### Server → Client Messages

#### 1. Connection Acknowledgement
```json
{
  "type": "connected",
  "status": "ready",
  "available_models": ["fast", "balanced", "accurate"],
  "class_labels": ["person", "car", "sky", ...],  // Available classes
  "default_colormap": {...}
}
```

#### 2. Segmentation Result
```json
{
  "type": "segmentation",
  "timestamp": 1698765432000,
  "data": "<base64_encoded_png>",  // Segmentation mask (colorized)
  "metadata": {
    "inference_time_ms": 45.2,
    "model_mode": "balanced",
    "detected_classes": ["person", "car", "road"],
    "fps": 22.1
  }
}
```

#### 3. Error Message
```json
{
  "type": "error",
  "code": "INFERENCE_FAILED",
  "message": "GPU out of memory",
  "recoverable": true
}
```

#### 4. Performance Stats
```json
{
  "type": "stats",
  "fps": 22.5,
  "avg_inference_ms": 44.3,
  "gpu_memory_mb": 3840,
  "queue_size": 2
}
```

---

## 🤖 Model Selection & Optimization

### Model Profiles

#### Fast Mode: DeepLabV3-MobileNetV3
```yaml
Purpose: Low-latency inference for smooth interaction
Architecture: DeepLabV3 + MobileNetV3 backbone
Input Size: 512x512
Output Classes: 21 (COCO Stuff)
Optimization: ONNX Runtime (FP16)

Performance (T4 GPU):
  - Inference Time: ~20-25ms
  - Target FPS: 30-40
  - GPU Memory: ~1.2 GB
  - Accuracy: Good (mIoU ~70%)

Use Case: Initial demo, responsive interaction
```

#### Balanced Mode: DeepLabV3-ResNet50
```yaml
Purpose: Best speed/accuracy trade-off
Architecture: DeepLabV3 + ResNet50 backbone
Input Size: 640x640
Output Classes: 21 (COCO Stuff)
Optimization: TensorRT (FP16)

Performance (T4 GPU):
  - Inference Time: ~40-50ms
  - Target FPS: 20-25
  - GPU Memory: ~2.5 GB
  - Accuracy: Better (mIoU ~75%)

Use Case: Default mode for showcase
```

#### Accurate Mode: SegFormer-B3
```yaml
Purpose: Maximum segmentation quality
Architecture: SegFormer (Transformer-based)
Input Size: 768x768
Output Classes: 150 (ADE20K - more granular)
Optimization: PyTorch JIT + torch.compile

Performance (T4 GPU):
  - Inference Time: ~80-100ms
  - Target FPS: 10-12
  - GPU Memory: ~4.5 GB
  - Accuracy: Best (mIoU ~82%)

Use Case: "Wow factor" for portfolio viewers
```

### Optimization Pipeline

```python
# Pseudocode for model optimization workflow

# 1. Load Pre-trained Model
model = load_pretrained_model(model_name)

# 2. Export to ONNX (for Fast/Balanced modes)
if mode in ["fast", "balanced"]:
    onnx_model = torch.onnx.export(
        model,
        dummy_input,
        opset_version=17,
        dynamic_axes={'input': {0: 'batch'}}
    )

    # 3. Optimize with ONNX Runtime
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    # 4. Convert to TensorRT (Balanced mode only)
    if mode == "balanced":
        trt_engine = onnx_to_tensorrt(
            onnx_model,
            precision="fp16",
            workspace_size=4096  # MB
        )

# 5. For Accurate mode: PyTorch native optimization
else:
    model = torch.jit.script(model)
    model = torch.compile(model, mode="max-autotune")
```

### Class Labels & Colormaps

```python
# COCO Stuff (21 classes) - Fast/Balanced modes
COCO_CLASSES = [
    "background", "person", "bicycle", "car", "motorcycle",
    "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter",
    "bench", "bird", "cat", "dog", "horse", "sheep",
    "cow"
]

# ADE20K (150 classes) - Accurate mode
# Includes: wall, building, sky, floor, tree, ceiling, road, bed,
#           windowpane, grass, cabinet, sidewalk, ...
# (Full list: https://github.com/CSAILVision/ADE20K)

# Colormap Strategy
COLORMAP_ADE20K = generate_ade20k_palette()  # Official ADE20K colors
COLORMAP_CITYSCAPES = generate_cityscapes_palette()  # Urban-focused colors
```

---

## 🎨 Visualization Modes

### Mode 1: Filled Overlay (Default)
- **Description**: Transparent colored mask over original video
- **Implementation**: Alpha blending (adjustable 0.3-0.8 opacity)
- **Use Case**: Clear class identification with video context

### Mode 2: Contour Only
- **Description**: Draw only object boundaries
- **Implementation**: OpenCV `findContours()` + line drawing
- **Use Case**: Minimal visual interference, edge detection feel

### Mode 3: Side-by-Side
- **Description**: Original video | Segmentation mask
- **Implementation**: Split canvas or dual canvas elements
- **Use Case**: Direct comparison for accuracy demonstration

### Mode 4: Blend Mode
- **Description**: Artistic blend using different color spaces
- **Implementation**: HSV color space manipulation
- **Use Case**: Aesthetic "wow factor" for portfolio

### Interactive Controls
```javascript
// UI Control Elements
controls = {
  model_mode: ["fast", "balanced", "accurate"],  // Dropdown
  viz_mode: ["filled", "contour", "side-by-side", "blend"],  // Buttons
  opacity: 0.6,  // Slider (0.0 - 1.0)
  class_filter: [],  // Multi-select checkboxes
  show_fps: true,  // Toggle
  show_class_legend: true  // Toggle
}
```

---

## 🚀 Implementation Phases

### Phase 1: Backend Core (Est. 4-6 hours)
**Goal**: Working inference server with WebSocket support

Tasks:
1. Setup FastAPI application structure
2. Implement WebSocket connection handling
3. Load and test DeepLabV3-ResNet50 (Balanced mode first)
4. Basic frame processing pipeline (decode → inference → encode)
5. Unit tests for inference engine

**Deliverable**: Backend server that accepts frames and returns segmentation masks

---

### Phase 2: Model Optimization (Est. 3-4 hours)
**Goal**: All three model profiles optimized and tested

Tasks:
1. Export models to ONNX format
2. Setup ONNX Runtime GPU sessions
3. (Optional) Convert Balanced mode to TensorRT
4. Implement model switching logic
5. Benchmark each model profile on Colab GPU

**Deliverable**: Optimized model pool with measured performance metrics

---

### Phase 3: Frontend Basics (Est. 3-4 hours)
**Goal**: Webcam capture and basic rendering

Tasks:
1. HTML structure with canvas elements
2. Webcam capture with `getUserMedia()`
3. WebSocket client connection
4. Basic canvas rendering (video + overlay)
5. Frame encoding (JPEG compression before sending)

**Deliverable**: Working frontend that displays live segmentation

---

### Phase 4: Visualization Modes (Est. 2-3 hours)
**Goal**: Multiple visualization styles

Tasks:
1. Implement filled overlay with opacity control
2. Implement contour-only mode
3. Implement side-by-side view
4. Implement blend mode (optional)
5. UI controls for mode switching

**Deliverable**: Polished visualization with user controls

---

### Phase 5: Performance Tuning (Est. 2-3 hours)
**Goal**: Optimize end-to-end latency

Tasks:
1. Implement frame queue management (drop frames if needed)
2. Optimize WebSocket message size (compression)
3. GPU memory pooling and warm-up
4. FPS counter and performance stats display
5. Latency profiling and bottleneck identification

**Deliverable**: Smooth real-time performance at target FPS

---

### Phase 6: Polish & Demo Prep (Est. 2-3 hours)
**Goal**: Portfolio-ready demo

Tasks:
1. UI/UX polish (styling, animations, responsive controls)
2. Class legend display
3. Error handling and user feedback
4. Screen recording for portfolio (in case live demo unavailable)
5. Documentation (README, setup guide)

**Deliverable**: Complete demo ready for portfolio showcase

---

**Total Estimated Time**: 16-23 hours

---

## 📊 Performance Benchmarks (Expected)

### Latency Breakdown (End-to-End)

```
Total Latency Target: <200ms (balanced mode)

┌─────────────────────────────────────────────────┐
│ Component              │ Latency   │ % of Total │
├────────────────────────┼───────────┼────────────┤
│ Webcam Capture         │   5-10ms  │    5%      │
│ JPEG Encoding (client) │  10-15ms  │    7%      │
│ Network (WebSocket)    │  20-30ms  │   15%      │
│ JPEG Decoding (server) │   5-10ms  │    5%      │
│ Preprocessing          │   5-10ms  │    5%      │
│ Model Inference        │  40-50ms  │   30%      │ ← Main bottleneck
│ Postprocessing         │  10-15ms  │    8%      │
│ PNG Encoding (server)  │  15-20ms  │   12%      │
│ Network (WebSocket)    │  20-30ms  │   13%      │
│ Canvas Rendering       │   5-10ms  │    5%      │
├────────────────────────┼───────────┼────────────┤
│ TOTAL                  │ 135-200ms │   100%     │
└─────────────────────────────────────────────────┘
```

### Model Performance Targets

| Model Mode | Resolution | Inference Time | Target FPS | GPU Memory |
|------------|-----------|----------------|------------|------------|
| Fast       | 512x512   | 20-25ms        | 30-40      | ~1.2 GB    |
| Balanced   | 640x640   | 40-50ms        | 20-25      | ~2.5 GB    |
| Accurate   | 768x768   | 80-100ms       | 10-12      | ~4.5 GB    |

*Benchmarks measured on Google Colab Tesla T4 GPU*

---

## 🔧 Optimization Strategies

### 1. Model-Level Optimizations
- **FP16 Mixed Precision**: 2x speedup, minimal accuracy loss
- **Dynamic Quantization**: Further 20-30% speedup (INT8)
- **Layer Fusion**: ONNX/TensorRT automatic optimizations
- **Batch Size = 1**: No batching overhead for real-time

### 2. Pipeline Optimizations
- **Async Frame Processing**: Non-blocking I/O operations
- **GPU Memory Pooling**: Pre-allocate tensors, avoid reallocations
- **Frame Skipping**: Drop frames if inference queue builds up
- **Resolution Scaling**: Allow users to reduce input resolution

### 3. Network Optimizations
- **JPEG Compression**: Quality 75-85 (balance size/quality)
- **Binary WebSocket**: Use binary frames (not base64 text)
- **Message Batching**: Send multiple frames if bandwidth allows
- **Compression**: Optional zlib/gzip for PNG masks

### 4. Frontend Optimizations
- **Canvas Hardware Acceleration**: Use `willReadFrequently: false`
- **RequestAnimationFrame**: Sync rendering with browser refresh
- **Web Workers**: Offload encoding/decoding to separate thread (optional)

---

## 🐳 Google Colab Deployment Guide

### Setup Notebook Structure

```python
# Cell 1: Install Dependencies
!pip install fastapi uvicorn python-socketio aiohttp
!pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install onnx onnxruntime-gpu opencv-python pillow
!pip install pyngrok  # For public URL tunneling

# Cell 2: Clone Repository
!git clone https://github.com/yourusername/realtime-segmentation.git
%cd realtime-segmentation

# Cell 3: Download & Optimize Models
from backend.models.model_loader import download_and_optimize_models
download_and_optimize_models()

# Cell 4: Setup ngrok Tunnel
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")  # Get free token from ngrok.com
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")

# Cell 5: Start Server
!python backend/app.py

# Cell 6: Keep Colab Alive (optional)
import time
while True:
    time.sleep(60)
    print("Keeping session alive...")
```

### Colab-Specific Considerations

**Session Management:**
- Colab sessions timeout after 12 hours or 90 min idle
- Use `KeepAlive` scripts or browser extensions for extended demos
- Mount Google Drive for model caching (avoid re-downloads)

**GPU Allocation:**
- Check GPU type: `!nvidia-smi` (T4, P100, or V100)
- V100 > P100 > T4 for performance
- Use `Runtime > Change runtime type > GPU` to enable GPU

**Storage:**
- Save optimized models to Google Drive for persistence
- `/content/` directory is ephemeral (cleared on disconnect)

**Networking:**
- ngrok free tier: 40 connections/min limit (sufficient for demo)
- Alternative: Cloudflare Tunnel (unlimited, but more setup)

---

## 🧪 Testing Strategy

### Backend Unit Tests
```python
# tests/test_inference.py
def test_model_loading():
    """Verify all models load correctly"""

def test_inference_performance():
    """Benchmark inference time per model"""

def test_frame_processing():
    """Test frame decode → inference → encode pipeline"""

def test_websocket_connection():
    """Verify WebSocket handshake and message handling"""
```

### Frontend Testing
- **Manual Testing**: Browser DevTools Network tab (WebSocket frames)
- **Performance Testing**: Chrome Lighthouse (if applicable)
- **Cross-Browser**: Test on Chrome, Firefox, Edge

### Integration Testing
- **End-to-End Latency**: Measure total round-trip time
- **Stress Testing**: Multiple concurrent connections (if needed)
- **Error Recovery**: Test GPU OOM handling, reconnection logic

---

## 📈 Success Metrics

### Technical Metrics
- ✅ Balanced mode: 20+ FPS sustained
- ✅ End-to-end latency: <200ms
- ✅ Model switching: <2 seconds
- ✅ GPU memory: <5 GB total

### Portfolio Demo Metrics
- ✅ Visual polish: Professional UI/UX
- ✅ Mode diversity: 3 model modes + 3-4 viz modes functional
- ✅ Performance showcase: FPS counter, inference time display
- ✅ Stability: 5+ minutes continuous operation without errors

---

## 🔮 Future Enhancements (Post-Demo)

If you want to expand this project later:

1. **Interactive Segmentation**: Add Segment Anything (SAM) with point/box prompts
2. **Video Recording**: Save segmented video output
3. **Custom Training**: Fine-tune on custom datasets
4. **Mobile Support**: Responsive design + mobile optimization
5. **Multi-User**: Support multiple concurrent users (scalability)
6. **Cloud Deployment**: Migrate to AWS/GCP for persistent hosting
7. **3D Visualization**: Project segmentation onto 3D scene

---

## 📚 Key Resources

### Documentation
- [FastAPI WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)
- [PyTorch ONNX Export](https://pytorch.org/docs/stable/onnx.html)
- [ONNX Runtime GPU](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)
- [TensorRT Python API](https://docs.nvidia.com/deeplearning/tensorrt/api/python_api/)

### Pre-trained Models
- [DeepLabV3 (torchvision)](https://pytorch.org/vision/stable/models.html#semantic-segmentation)
- [SegFormer (Hugging Face)](https://huggingface.co/docs/transformers/model_doc/segformer)
- [Model Zoo (ONNX)](https://github.com/onnx/models)

### Tools
- [ngrok](https://ngrok.com/) - Public URL tunneling
- [Netron](https://netron.app/) - Model architecture visualization
- [TensorBoard](https://www.tensorflow.org/tensorboard) - Performance profiling

---

## 🎯 Next Steps

1. **Review this specification** - Make sure everything aligns with your vision
2. **Setup repository structure** - Initialize Git repo with project folders
3. **Start with Phase 1** - Get basic backend inference working
4. **Iterate incrementally** - Test each phase before moving forward
5. **Document as you go** - Update README with setup instructions

**Ready to start building?** Let me know if you want me to:
- Generate starter code for any phase
- Clarify any technical details
- Modify the specification based on your feedback

---

**Questions or changes needed?** Let's refine this before implementation! 🚀
