# Backend Server

FastAPI-based WebSocket server for real-time semantic segmentation.

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

The server will start on `http://localhost:8000`

### Google Colab Deployment

See `notebooks/colab_deployment.ipynb` for complete Colab setup.

## Architecture

```
app.py                    # Main FastAPI application
├── models/
│   ├── model_loader.py       # Model loading and caching
│   └── inference_engine.py   # Inference pipeline
└── utils/
    ├── config.py             # Configuration
    ├── frame_processor.py    # Frame encoding/decoding
    └── segmentation_viz.py   # Visualization rendering
```

## API Endpoints

### HTTP Endpoints

- `GET /` - Serve frontend
- `GET /health` - Health check

### WebSocket Endpoint

- `WS /ws` - Real-time segmentation stream

## WebSocket Messages

### Client → Server

**Initialize Connection**
```json
{
  "type": "init",
  "config": {
    "model_mode": "balanced",
    "resolution": {"width": 640, "height": 480}
  }
}
```

**Send Frame**
```json
{
  "type": "frame",
  "data": "<base64_jpeg>",
  "timestamp": 1234567890
}
```

**Change Model**
```json
{
  "type": "change_mode",
  "model_mode": "fast"
}
```

**Update Visualization**
```json
{
  "type": "update_viz",
  "settings": {
    "overlay_opacity": 0.6,
    "visualization_mode": "filled"
  }
}
```

### Server → Client

**Connection Acknowledgement**
```json
{
  "type": "connected",
  "status": "ready",
  "available_models": ["fast", "balanced", "accurate"]
}
```

**Segmentation Result**
```json
{
  "type": "segmentation",
  "data": "<base64_png>",
  "metadata": {
    "inference_time_ms": 45.2,
    "fps": 22.1,
    "detected_classes": ["person", "car"]
  }
}
```

## Model Profiles

| Mode | Model | Input Size | FPS Target | Memory |
|------|-------|-----------|-----------|--------|
| Fast | DeepLabV3-MobileNetV3 | 512x512 | 30-40 | 1.2 GB |
| Balanced | DeepLabV3-ResNet50 | 640x640 | 20-25 | 2.5 GB |
| Accurate | SegFormer-B3 | 768x768 | 10-12 | 4.5 GB |

## Configuration

Edit `utils/config.py` to customize:
- Server host/port
- Model profiles
- Frame processing settings
- Visualization defaults

## Performance Tuning

### GPU Optimization
- Models automatically use FP16 on GPU
- Warm-up inference reduces first-frame latency
- Frame queue prevents backlog

### Memory Management
- Model caching reduces switching overhead
- Frame compression reduces network bandwidth
- Automatic queue size limiting

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend
python app.py
```

### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Port Already in Use
```python
# Change port in utils/config.py
SERVER_CONFIG = {
    "port": 8001  # Change from 8000
}
```

## Dependencies

See `requirements.txt` for complete list.

Key dependencies:
- FastAPI + uvicorn (web server)
- PyTorch + torchvision (deep learning)
- transformers (SegFormer model)
- OpenCV + Pillow (image processing)
- ONNX Runtime (optimization)
