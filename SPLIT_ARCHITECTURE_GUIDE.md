# Split Architecture Deployment Guide

**New Architecture**: Frontend (Local) + Backend (Google Colab GPU)

This guide explains how to run the frontend locally while the backend runs on Google Colab with free GPU access.

---

## 🏗️ Architecture Overview

```
┌─────────────────────┐         ┌──────────────────────┐
│  YOUR LOCAL         │         │  GOOGLE COLAB        │
│  MACHINE            │         │  (Free GPU)          │
├─────────────────────┤         ├──────────────────────┤
│                     │         │                      │
│  Frontend Server    │◄────────┤  Backend Server      │
│  (Port 8080)        │  ngrok  │  (Port 8000)         │
│                     │  WebSocket                     │
│  - HTML/CSS/JS      │         │  - FastAPI           │
│  - Webcam capture   │         │  - PyTorch Models    │
│  - UI controls      │         │  - GPU Inference     │
│                     │         │                      │
└─────────────────────┘         └──────────────────────┘
        ↑
        │ http://localhost:8080
        │
   Your Browser
```

**Benefits:**
- ✅ Frontend runs locally (fast, stable)
- ✅ Backend uses free Colab GPU (powerful inference)
- ✅ No frontend upload needed
- ✅ Easy development and testing

---

## 🚀 Quick Start (5 Minutes)

### **Part 1: Start Backend on Colab** ☁️

1. **Open Colab**: https://colab.research.google.com
2. **Upload notebook**: `notebooks/colab_deployment.ipynb`
3. **Enable GPU**: Runtime → Change runtime type → GPU
4. **Run cells 1-5**:
   - Cell 1: Check GPU ✅
   - Cell 2: Clone repository
   - Cell 3: Install dependencies (~3-5 min)
   - Cell 4: Download models (~2-3 min, optional)
   - Cell 5: Setup ngrok (paste your token from https://ngrok.com)

5. **Cell 6: Start server**
   ```python
   import sys, os
   sys.path.insert(0, '/content/RealTimeSeg/backend')
   os.chdir('/content/RealTimeSeg/backend')
   os.environ['CUDA_VISIBLE_DEVICES'] = '0'
   !python app.py
   ```

6. **📋 COPY THE NGROK URL** from Cell 5 output:
   ```
   🌐 PUBLIC URL: https://abc123.ngrok.io
   ```
   **Keep this URL handy!**

---

### **Part 2: Start Frontend Locally** 🖥️

**On Linux/Mac:**
```bash
cd /home/arti/Documents/RealTimeSeg
chmod +x start_frontend.sh
./start_frontend.sh
```

**On Windows:**
```cmd
cd C:\path\to\RealTimeSeg
start_frontend.bat
```

**Or manually:**
```bash
cd RealTimeSeg/frontend
python3 -m http.server 8080
```

✅ **Frontend running at**: http://localhost:8080

---

### **Part 3: Connect Everything** 🔗

1. **Open your browser**: http://localhost:8080
2. **You'll see the interface!**
3. **In the "Backend Server URL" field**, paste your ngrok URL:
   ```
   https://abc123.ngrok.io
   ```
4. **Click "Connect"** button
5. **Allow webcam** when prompted
6. **🎉 Watch the magic!**

---

## 📖 Detailed Setup Instructions

### Prerequisites

**Local Machine:**
- Python 3.8+ (for running HTTP server)
- Modern web browser (Chrome recommended)
- Webcam

**Google Colab:**
- Google account
- ngrok account (free) - https://ngrok.com

---

### Step-by-Step Backend Setup (Colab)

#### Step 1: Open Colab Notebook
1. Go to https://colab.research.google.com
2. Upload: `RealTimeSeg/notebooks/colab_deployment.ipynb`
3. Or clone from GitHub if you pushed the code

#### Step 2: Enable GPU
**CRITICAL**: Runtime → Change runtime type → GPU → Save

#### Step 3: Execute Cells

**Cell 1: Verify GPU**
```python
!nvidia-smi
```
Expected: Tesla T4/P100/V100 info

---

**Cell 2: Clone Repository**
```python
!git clone https://github.com/arti1117/RealTimeSeg.git
%cd RealTimeSeg
```

---

**Cell 3: Install Dependencies** (3-5 minutes)
```python
!pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install -r backend/requirements.txt
!pip install pyngrok
```

---

**Cell 4: Download Models** (2-3 minutes, OPTIONAL)
```python
import torch
import torchvision.models.segmentation as models
from transformers import SegformerForSemanticSegmentation

print("Downloading models...")
_ = models.deeplabv3_mobilenet_v3_large(pretrained=True)
_ = models.deeplabv3_resnet50(pretrained=True)
_ = SegformerForSemanticSegmentation.from_pretrained(
    "nvidia/segformer-b3-finetuned-ade-512-512"
)
print("✓ All models cached")
```

---

**Cell 5: Setup ngrok** (PASTE YOUR TOKEN!)
```python
from pyngrok import ngrok, conf

# Get token from: https://ngrok.com/dashboard
NGROK_TOKEN = "YOUR_TOKEN_HERE"  # ⚠️ Replace this!

conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(8000)

print(f"\n{'='*60}")
print(f"🌐 PUBLIC URL: {public_url}")
print(f"{'='*60}\n")
print("📋 COPY THIS URL - You'll paste it in the frontend!")
```

**⚠️ IMPORTANT**: Copy the URL shown!

---

**Cell 6: Start Backend Server**
```python
import sys, os

# Configure Python paths
sys.path.insert(0, '/content/RealTimeSeg/backend')
os.chdir('/content/RealTimeSeg/backend')
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

print("✓ Starting backend server...")
print("✓ Frontend should connect to the ngrok URL from Cell 5\n")

# Start server
!python app.py
```

**Expected output:**
```
Initializing server...
Loading default model: balanced
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**⚠️ Keep this cell running!**

---

### Step-by-Step Frontend Setup (Local)

#### Option 1: Using Helper Scripts

**Linux/Mac:**
```bash
cd /home/arti/Documents/RealTimeSeg
chmod +x start_frontend.sh
./start_frontend.sh
```

**Windows:**
```cmd
cd C:\Users\YourName\Documents\RealTimeSeg
start_frontend.bat
```

---

#### Option 2: Manual Start

```bash
cd RealTimeSeg/frontend
python3 -m http.server 8080
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

---

### Connecting Frontend to Backend

1. **Open browser**: http://localhost:8080
2. **Find "Backend Server URL" field** in the connection panel
3. **Paste your ngrok URL**: `https://abc123.ngrok.io`
4. **Click "Connect"**
5. **Allow webcam access**

✅ **You're connected!**

---

## 🎮 Testing Your Setup

Once connected:

### 1. Verify Connection
- Status should show "Connected" (green dot)
- FPS counter starts updating
- Webcam feed with overlay appears

### 2. Test Model Modes
- **Fast Mode**: 30-40 FPS
- **Balanced Mode**: 20-25 FPS (default)
- **Accurate Mode**: 10-12 FPS

### 3. Test Visualization Modes
- **Filled Overlay**: Colored transparent mask
- **Contours**: Edge detection only
- **Side-by-Side**: Split view
- **Blend**: Artistic mode

### 4. Test Controls
- Adjust opacity slider (0-100%)
- Watch detected classes update
- Monitor performance stats

---

## 🐛 Troubleshooting

### Backend Issues (Colab)

**Problem**: No GPU available
**Solution**: Runtime → Change runtime type → GPU → Save, then restart

**Problem**: ngrok connection failed
**Solution**: Verify token is correct, regenerate at https://ngrok.com

**Problem**: Import errors
**Solution**: Verify Cell 2 cloned correctly, check Cell 6 has path setup

**Problem**: Models downloading slowly
**Solution**: Normal for first run (~2-3GB), subsequent runs use cache

---

### Frontend Issues (Local)

**Problem**: Port 8080 already in use
**Solution**:
```bash
# Use different port
python3 -m http.server 8081
# Then open http://localhost:8081
```

**Problem**: Can't access localhost:8080
**Solution**: Check firewall, try http://127.0.0.1:8080

---

### Connection Issues

**Problem**: WebSocket connection failed
**Solution**:
1. Verify ngrok URL is correct (copy from Cell 5)
2. Ensure URL starts with `https://`
3. Check backend server is running (Cell 6)
4. Try without `https://` prefix, just `abc123.ngrok.io`

**Problem**: "TypeError: Failed to fetch"
**Solution**: CORS issue, backend should allow all origins (already configured)

**Problem**: Webcam not working
**Solution**:
1. Check browser permissions (allow camera)
2. Close other apps using webcam
3. Try different browser (Chrome recommended)
4. Check webcam is detected: Settings → Privacy → Camera

---

## 📝 Tips & Best Practices

### Development Workflow

1. **Start backend first** (takes longer to setup)
2. **Start frontend** (instant)
3. **Develop locally** (edit frontend files)
4. **Refresh browser** to see changes
5. **Backend stays running** on Colab

### Session Management

**Colab Limits:**
- 12-hour maximum session
- 90-minute idle disconnect
- Free GPU subject to availability

**Tips:**
- Save ngrok URL if you need to reconnect
- Run Cell 7 (keep-alive) to prevent disconnect
- Models are cached, faster on subsequent runs

### Performance Tips

1. **Start with Balanced mode** (best trade-off)
2. **Use Fast mode** if laggy
3. **Accurate mode** for best quality (slower)
4. **Check GPU usage**: Cell 1 (`!nvidia-smi`) periodically

---

## 🎥 Recording Your Demo

**For Portfolio:**

1. **Screen record** your local browser (http://localhost:8080)
2. **Show**:
   - Connecting to backend (paste ngrok URL)
   - All 3 model modes (FPS changes)
   - All 4 visualization styles
   - Opacity adjustment
   - Different scenes/objects
   - Performance metrics

3. **Duration**: 2-3 minutes ideal

4. **Tools**:
   - OBS Studio (free, powerful)
   - QuickTime (Mac)
   - Built-in screen recorder

---

## 🔄 Stopping Everything

**Stop Frontend (Local):**
- Press `Ctrl+C` in terminal

**Stop Backend (Colab):**
- Click "Stop" button on Cell 6
- Or Runtime → Restart runtime

---

## 📊 Architecture Benefits

| Aspect | Split Architecture | All-in-Colab |
|--------|-------------------|--------------|
| Frontend Speed | ⚡ Fast (local) | 🐌 Slower (ngrok latency) |
| Development | ✅ Easy (live reload) | ❌ Need re-upload |
| Stability | ✅ Local control | ⚠️ Colab limits |
| GPU Access | ✅ Free Colab | ✅ Free Colab |
| Setup Time | ⚡ Quick | 🐌 Upload needed |

---

## 📚 Next Steps

- ✅ Architecture changed successfully
- ✅ Test the split setup
- ✅ Record demo video
- ✅ Push changes to GitHub
- ✅ Update portfolio documentation

---

## 🆘 Getting Help

**If you encounter issues:**

1. Check this guide's troubleshooting section
2. Verify both frontend and backend are running
3. Check browser console (F12) for errors
4. Check Colab cell outputs for backend errors

**Files to reference:**
- `QUICKSTART.md` - Quick reference
- `SETUP.md` - Detailed setup
- `DEPLOYMENT_TEST_REPORT.md` - Validation results

---

**Status**: ✅ Split Architecture Ready
**Frontend**: Local (http://localhost:8080)
**Backend**: Colab + ngrok (https://xxx.ngrok.io)
**Connection**: WebSocket with configurable URL
