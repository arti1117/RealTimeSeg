# Connection Troubleshooting Guide

## Current Error: JSON Parse Error

**Error Message:** `❌ Connection Failed: JSON.parse: unexpected character at line 1 column 1 of the JSON data`

**What This Means:** The frontend is receiving HTML or plain text from the backend instead of JSON data.

---

## Step-by-Step Diagnosis

### Step 1: Use the Enhanced Diagnostic Tool

1. **Start the frontend:**
   ```bash
   cd /home/arti/Documents/RealTimeSeg
   ./start_frontend.sh
   ```

2. **Open the diagnostic tool in your browser:**
   ```
   http://localhost:8080/test_connection.html
   ```

3. **Enter your ngrok URL** (from Colab Cell 5) and click "1. Test HTTP"

4. **Observe the results:**
   - ✅ **If it shows valid JSON:** Great! The backend is working. Try "2. Test WebSocket"
   - ❌ **If it shows HTML/error:** This tells us what's wrong (see diagnoses below)

---

## Common Causes and Fixes

### Cause 1: ngrok Warning Page

**Symptoms:**
- Response contains "ngrok"
- HTML page with ngrok branding
- Warning about visiting site

**Fix:**
```
Option A: Click through the ngrok warning in browser first
1. Open your ngrok URL in a new browser tab
2. Click "Visit Site" if prompted
3. Try the connection test again

Option B: Use ngrok auth domain (if you have ngrok account)
1. In Colab Cell 5, use authenticated tunnel
2. This skips the warning page
```

### Cause 2: Backend Not Running

**Symptoms:**
- Response is HTML error page
- No JSON response
- "Application error" or similar messages

**Fix:**
```
1. Check Colab Cell 6 is running (should show green "running" icon)
2. Look for these success messages in Cell 6 output:
   ✓ Backend directory: /content/RealTimeSeg/backend
   ✓ Model loader created
   ✓ Default model loaded
   ✓ Frame processor created
   ✅ Server initialized successfully
   INFO: Uvicorn running on http://0.0.0.0:8000

3. If you don't see these messages, restart Cell 6
```

### Cause 3: ngrok Tunnel Not Running

**Symptoms:**
- Connection refused
- Timeout errors
- Can't reach the URL at all

**Fix:**
```
1. Check Colab Cell 5 output for the public URL
2. Should look like: 🌐 PUBLIC URL: https://abc123.ngrok.io
3. If Cell 5 isn't running or shows errors, re-run it
4. Make sure you use the EXACT URL shown (copy-paste)
```

### Cause 4: CORS Issues

**Symptoms:**
- Browser console shows CORS errors
- "Access-Control-Allow-Origin" errors
- Connection fails but backend is running

**Fix:**
```
Backend should already have CORS configured, but verify:

In backend/app.py, check for:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Verification Checklist

Before testing the connection, verify:

### ✅ Backend (Colab) Checklist:
- [ ] Runtime type is set to GPU (Runtime → Change runtime type)
- [ ] All cells 1-5 have been run successfully
- [ ] Cell 5 shows a valid ngrok URL
- [ ] Cell 6 is currently running (green running icon)
- [ ] Cell 6 output shows "✅ Server initialized successfully"
- [ ] Cell 6 output shows "INFO: Uvicorn running on http://0.0.0.0:8000"

### ✅ Frontend (Local) Checklist:
- [ ] Frontend server is running (`./start_frontend.sh`)
- [ ] Can access http://localhost:8080 in browser
- [ ] No firewall blocking port 8080
- [ ] Using Chrome or modern browser (not IE)

### ✅ Connection Checklist:
- [ ] Copied the EXACT ngrok URL from Cell 5
- [ ] URL includes https:// (e.g., https://abc123.ngrok.io)
- [ ] No typos in the URL
- [ ] Tested with test_connection.html first

---

## Testing Flow

Follow this order:

1. **Test HTTP First** (button "1. Test HTTP")
   - This verifies basic connectivity
   - Should return JSON with server info
   - If this fails, fix it before testing WebSocket

2. **Test WebSocket Second** (button "2. Test WebSocket")
   - Only try this after HTTP test passes
   - Should receive "connected" message from server
   - Confirms full bidirectional communication

3. **Use Main App** (http://localhost:8080/index.html)
   - Only try this after both tests pass
   - Enter ngrok URL in "Backend Server URL" field
   - Click "Connect" and allow webcam

---

## Quick Debug Commands

### Check if backend is reachable (from terminal):
```bash
# Replace with your ngrok URL
curl https://YOUR-NGROK-URL.ngrok.io

# Should return JSON like:
# {"name":"Real-Time Segmentation API","version":"1.0.0",...}
```

### Check backend status in Colab:
```python
# In a new Colab cell
import requests
response = requests.get("http://localhost:8000")
print(response.text)
```

---

## Still Having Issues?

If none of the above fixes work:

1. **Copy the exact error/response** from test_connection.html
2. **Take a screenshot** of Colab Cell 6 output
3. **Verify these details:**
   - What's the exact ngrok URL?
   - What does the "Raw response" section show in the test tool?
   - Are there any errors in browser console? (F12 → Console tab)
   - Are there any errors in Colab Cell 6 output?

---

## Expected Working State

When everything is working correctly, you should see:

**In test_connection.html after HTTP test:**
```
✅ HTTP Status: 200 OK
✅ Backend is responding with valid JSON!
📦 Response: {
  "name": "Real-Time Segmentation API",
  "version": "1.0.0",
  "status": "running",
  "websocket_endpoint": "/ws",
  "available_models": ["fast", "balanced", "accurate"]
}
✅ HTTP TEST PASSED - Backend is reachable!
```

**In test_connection.html after WebSocket test:**
```
✅ WebSocket Connected!
✅ Received message from server:
📦 {
  "type": "connected",
  "status": "ready",
  "available_models": ["fast", "balanced", "accurate"],
  "class_labels": [...],
  "current_model": "balanced"
}
🎉 WEBSOCKET TEST PASSED!
```

**In Colab Cell 6:**
```
✓ Backend directory: /content/RealTimeSeg/backend
✓ Python path: /content/RealTimeSeg/backend
✓ Current directory: /content/RealTimeSeg/backend

Starting server...
Initializing server components...
✓ Model loader created
Loading default model: balanced
✓ Default model loaded
✓ Frame processor created
✅ Server initialized successfully
Starting uvicorn...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Next Steps After Connection Works

Once both HTTP and WebSocket tests pass:

1. Open http://localhost:8080
2. Paste your ngrok URL in "Backend Server URL"
3. Click "Connect"
4. Allow webcam access
5. Watch the real-time segmentation! 🎉

You can then:
- Switch between Fast/Balanced/Accurate modes
- Try different visualization styles
- Adjust overlay opacity
- See detected object classes
