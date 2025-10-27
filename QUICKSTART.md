# Quick Start Guide

Get running in 5 minutes with Google Colab.

## Google Colab (Fastest)

### 1. Open Notebook
Open [`notebooks/colab_deployment.ipynb`](notebooks/colab_deployment.ipynb) in Google Colab

### 2. Enable GPU
`Runtime` → `Change runtime type` → `GPU` → Save

### 3. Get ngrok Token
1. Go to https://ngrok.com
2. Sign up (free)
3. Copy your auth token

### 4. Run Cells
Execute each cell in order:
- Cell 1: Check GPU
- Cell 2: Clone repo
- Cell 3: Install dependencies (3-5 min)
- Cell 4: Download models (2-3 min, optional but recommended)
- Cell 5: Setup ngrok (paste your token)
- Cell 6: Start server

### 5. Access App
Open the ngrok URL from Cell 5 in your browser

### 6. Use App
1. Click **Connect** button
2. Allow webcam access
3. Watch real-time segmentation!
4. Try different modes and visualization styles

**Total Time**: ~5 minutes (after downloads)

---

## Local (More Control)

### Prerequisites
- Python 3.10+
- CUDA GPU
- Webcam

### Commands
```bash
# Clone and setup
git clone https://github.com/yourusername/RealTimeSeg.git
cd RealTimeSeg
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install
cd backend
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# Run
python app.py
```

Open `http://localhost:8000`

---

## Quick Test

### Verify GPU
```python
import torch
print(torch.cuda.is_available())  # Should be True
```

### Check Server
```bash
curl http://localhost:8000/health
```

### Test Webcam
Browser console (F12):
```javascript
navigator.mediaDevices.getUserMedia({video: true})
  .then(() => console.log("OK"))
```

---

## Controls

| Control | Action |
|---------|--------|
| Connect | Start webcam + inference |
| Model Mode | Switch Fast/Balanced/Accurate |
| Viz Buttons | Change overlay style |
| Opacity | Adjust transparency |

---

## Troubleshooting

**Webcam not working?**
- Check browser permissions
- Close other apps using camera

**Low FPS?**
- Switch to Fast Mode
- Check GPU: `nvidia-smi`

**Connection failed?**
- Verify server running
- Check firewall

See [SETUP.md](SETUP.md) for details.

---

## What Next?

- Read [README.md](README.md) for full documentation
- See [SETUP.md](SETUP.md) for detailed guide
- Check [TECHNICAL_SPECIFICATION.md](claudedocs/TECHNICAL_SPECIFICATION.md) for architecture

**Ready to demo!** 🚀
