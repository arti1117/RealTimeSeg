# Google Colab - Quick Reference Card

**Project**: Real-Time Webcam Semantic Segmentation

---

## 🎯 Quick Access

**Colab URL**: https://colab.research.google.com
**ngrok URL**: https://ngrok.com
**Notebook Location**: `notebooks/colab_deployment.ipynb`

---

## 📋 Pre-Deployment Checklist

- [ ] ngrok account created
- [ ] ngrok auth token copied
- [ ] Notebook uploaded to Colab
- [ ] GPU runtime enabled

---

## 🚀 Execution Order

### 1️⃣ Check GPU
```python
!nvidia-smi
```
**Expected**: GPU info displayed (T4/P100/V100)

---

### 2️⃣ Clone Repository

**If using GitHub**:
```python
!git clone https://github.com/YOUR_USERNAME/RealTimeSeg.git
%cd RealTimeSeg
```

**If uploaded to Drive**:
```python
from google.colab import drive
drive.mount('/content/drive')
!cp -r "/content/drive/My Drive/RealTimeSeg" /content/
%cd RealTimeSeg
```

**Expected**: Directory changed to RealTimeSeg

---

### 3️⃣ Install Dependencies (~3-5 min)
```python
!pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install -r backend/requirements.txt
!pip install pyngrok
```
**Expected**: All packages installed
**Note**: Warnings are normal

---

### 4️⃣ Download Models (~2-3 min) [OPTIONAL]
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
print("✓ All models downloaded")
```
**Expected**: Download progress → Success message

---

### 5️⃣ Setup ngrok [PASTE YOUR TOKEN]
```python
from pyngrok import ngrok, conf

NGROK_TOKEN = "PASTE_YOUR_TOKEN_HERE"  # ⚠️ Replace this!

conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(8000)

print(f"\n{'='*60}")
print(f"🌐 PUBLIC URL: {public_url}")
print(f"{'='*60}\n")
```
**Expected**: URL displayed (e.g., https://abc123.ngrok.io)
**⚠️ COPY THIS URL** - You'll need it!

---

### 6️⃣ Start Server [DON'T STOP THIS CELL]
```python
import sys, os
sys.path.append('backend')
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
!cd backend && python app.py
```
**Expected**: Server running logs
**⚠️ Keep this cell running!**

---

## 🌐 Access Your App

1. **Copy the URL** from Step 5 (the ngrok URL)
2. **Open in browser** (new tab)
3. **Click "Connect"** button
4. **Allow webcam** access
5. **Enjoy!** 🎉

---

## 🎮 Testing Checklist

- [ ] Fast Mode (30-40 FPS)
- [ ] Balanced Mode (20-25 FPS)
- [ ] Accurate Mode (10-12 FPS)
- [ ] Filled Overlay visualization
- [ ] Contours visualization
- [ ] Side-by-Side visualization
- [ ] Blend visualization
- [ ] Opacity slider works
- [ ] FPS counter displays
- [ ] Classes detected and shown

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No GPU | Runtime → Change runtime → GPU |
| ngrok error | Check token is correct |
| Module error | Re-run Cell 3 |
| Webcam error | Check browser permissions |
| Low FPS | Switch to Fast Mode, check GPU |

---

## ⏱️ Expected Timeline

```
Total Time: 5-10 minutes

Cell 1: GPU check        10 sec
Cell 2: Clone           20 sec
Cell 3: Install deps    3-5 min
Cell 4: Models          2-3 min (optional)
Cell 5: ngrok           5 sec
Cell 6: Start server    30 sec
```

---

## 📸 Demo Recording Tips

**What to capture:**
- Switch between all 3 model modes
- Show all 4 visualization styles
- Adjust opacity slider
- Different scenes (face, objects, room)
- Performance stats panel
- Detected classes

**Duration**: 2-3 minutes ideal

---

## 💾 Session Info

- **Max session**: 12 hours
- **Idle timeout**: 90 minutes
- **GPU**: Free tier, subject to availability
- **Models**: Cached after first download

---

## 🆘 Help Resources

- **Detailed Guide**: SETUP.md
- **Quick Start**: QUICKSTART.md
- **Architecture**: claudedocs/TECHNICAL_SPECIFICATION.md
- **Test Report**: DEPLOYMENT_TEST_REPORT.md

---

## ✅ Success Indicators

**You know it's working when:**
- ✓ Server logs show "Application startup complete"
- ✓ ngrok URL opens the interface
- ✓ Webcam feed appears after clicking Connect
- ✓ Segmentation overlay appears on video
- ✓ FPS counter shows 10-40 FPS
- ✓ Detected classes list updates

---

## 🎯 Final Step

**Open the ngrok URL → Click Connect → Demo live!**

**Current Status**: Ready to deploy
**Next Action**: Execute cells 1-6 in order

---

**Generated**: 2025-10-27
**Project**: RealTimeSeg Portfolio Demo
