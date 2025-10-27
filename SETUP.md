# Setup Guide

Complete setup instructions for the Real-Time Semantic Segmentation project.

## Prerequisites

- Python 3.10+
- CUDA-capable GPU (for optimal performance)
- Webcam
- Modern web browser (Chrome/Edge/Firefox)

## Setup Options

### Option 1: Google Colab (Recommended for Demo)

**Easiest setup with free GPU access**

1. Open `notebooks/colab_deployment.ipynb` in Google Colab
2. Enable GPU: `Runtime` → `Change runtime type` → `GPU`
3. Get ngrok token from https://ngrok.com (free)
4. Run all cells in order
5. Access the public URL provided

**Pros:**
- Free GPU access (T4/P100/V100)
- No local installation needed
- Quick deployment

**Cons:**
- Session timeout after 12 hours
- 90-minute idle disconnect
- Requires internet connection

---

### Option 2: Local Development

**Full control with persistent environment**

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/RealTimeSeg.git
cd RealTimeSeg
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Install PyTorch with CUDA (check https://pytorch.org for your CUDA version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
cd backend
pip install -r requirements.txt
```

#### Step 4: Download Models (Optional)

Models will download automatically on first run, but you can pre-download:

```python
python -c "
import torchvision.models.segmentation as models
from transformers import SegformerForSemanticSegmentation

print('Downloading models...')
models.deeplabv3_mobilenet_v3_large(pretrained=True)
models.deeplabv3_resnet50(pretrained=True)
SegformerForSemanticSegmentation.from_pretrained('nvidia/segformer-b3-finetuned-ade-512-512')
print('Done!')
"
```

#### Step 5: Run Server

```bash
# From backend directory
python app.py
```

Server will start on `http://localhost:8000`

#### Step 6: Access Frontend

Open your browser and navigate to:
```
http://localhost:8000
```

**Pros:**
- Full control over environment
- No session timeouts
- Better for development

**Cons:**
- Requires local GPU for best performance
- More complex setup
- Larger disk space requirement

---

## Verification

### Check GPU Availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

### Test Webcam

Open browser console (F12) and run:
```javascript
navigator.mediaDevices.getUserMedia({video: true})
  .then(stream => console.log("Webcam OK"))
  .catch(err => console.error("Webcam error:", err));
```

### Check Server

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "available_models": ["fast", "balanced", "accurate"],
  "active_connections": 0
}
```

---

## Usage

### 1. Start Application

- **Local**: Run `python app.py` in backend directory
- **Colab**: Run all cells in deployment notebook

### 2. Connect Webcam

1. Click **"Connect"** button
2. Allow webcam access when prompted
3. Wait for "Connected" status

### 3. Adjust Settings

**Performance Profile:**
- **Fast Mode**: 30-40 FPS, lower accuracy
- **Balanced Mode**: 20-25 FPS, good trade-off (default)
- **Accurate Mode**: 10-12 FPS, best quality

**Visualization Style:**
- **Filled Overlay**: Transparent colored mask
- **Contours**: Object boundaries only
- **Side-by-Side**: Original + segmentation
- **Blend**: Artistic HSV blending

**Opacity:** Adjust overlay transparency (0-100%)

### 4. Monitor Performance

Check the **Performance** section:
- **FPS**: Current frame rate
- **Inference**: Model processing time
- **Classes**: Detected object types

---

## Troubleshooting

### Webcam Not Working

**Problem:** "Failed to access webcam"

**Solutions:**
1. Check browser permissions (camera allowed?)
2. Close other apps using webcam (Zoom, Skype, etc.)
3. Try different browser (Chrome recommended)
4. Check system privacy settings

### Low FPS / Laggy

**Problem:** Performance below target FPS

**Solutions:**
1. Switch to **Fast Mode**
2. Reduce webcam resolution (in browser settings)
3. Close other GPU-intensive applications
4. Check GPU memory: `nvidia-smi`
5. Restart server to clear GPU cache

### Connection Failed

**Problem:** "Failed to connect to server"

**Solutions:**
1. Check server is running: `curl http://localhost:8000/health`
2. Verify correct URL (http not https for local)
3. Check firewall settings
4. For Colab: Verify ngrok tunnel is active

### GPU Out of Memory

**Problem:** CUDA out of memory error

**Solutions:**
1. Use **Fast Mode** (lower memory)
2. Restart server to clear cache
3. Reduce input resolution
4. Close other GPU processes

### Models Not Loading

**Problem:** "Failed to load model"

**Solutions:**
1. Check internet connection (first download)
2. Verify disk space (~3GB needed for models)
3. Try manual download (see Step 4 above)
4. Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`

### Server Errors

**Problem:** 500 Internal Server Error

**Solutions:**
1. Check server logs in terminal
2. Verify all dependencies installed: `pip list`
3. Check Python version: `python --version` (3.10+ required)
4. Restart server
5. Check backend/README.md for detailed debugging

---

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 90+ | ✅ Full | Recommended |
| Edge 90+ | ✅ Full | Chromium-based |
| Firefox 88+ | ✅ Good | Slightly slower WebRTC |
| Safari 14+ | ⚠️ Partial | WebSocket issues possible |

---

## Performance Expectations

### Google Colab

| GPU | Fast Mode | Balanced | Accurate |
|-----|-----------|----------|----------|
| T4 | 35-40 FPS | 22-25 FPS | 10-12 FPS |
| P100 | 40-45 FPS | 28-30 FPS | 14-16 FPS |
| V100 | 45+ FPS | 35+ FPS | 18-20 FPS |

### Local Hardware

| GPU | Fast Mode | Balanced | Accurate |
|-----|-----------|----------|----------|
| RTX 3060 | 40+ FPS | 30+ FPS | 15+ FPS |
| RTX 3070 | 45+ FPS | 35+ FPS | 18+ FPS |
| RTX 3080 | 50+ FPS | 40+ FPS | 22+ FPS |

*Performance varies based on resolution, system load, and other factors*

---

## Next Steps

1. **Test Different Modes**: Try all three performance profiles
2. **Experiment with Visualization**: Test different overlay styles
3. **Try Different Scenes**: Indoor, outdoor, multiple objects
4. **Record Demo**: Screen record for portfolio
5. **Optimize Further**: See TECHNICAL_SPECIFICATION.md for advanced tuning

---

## Getting Help

- **Technical Docs**: See `claudedocs/TECHNICAL_SPECIFICATION.md`
- **API Reference**: See `backend/README.md`
- **Issues**: Check common problems above
- **Logs**: Check terminal output for detailed errors

---

## For Portfolio Presentation

1. **Screen Recording**: Record 2-3 minute demo showing:
   - Different performance modes
   - Multiple visualization styles
   - Real-time FPS/performance stats
   - Various object types (people, objects, scenes)

2. **Screenshots**: Capture:
   - UI overview
   - Different visualization modes
   - Performance stats
   - Code architecture

3. **Talking Points**:
   - Real-time GPU inference
   - WebSocket streaming
   - Multiple model profiles
   - Optimization techniques (FP16, ONNX)
   - Full-stack implementation
