# WebSocket Connection Fix - "Failed to Connect" Error

**Date**: 2025-10-28
**Issue**: Users experiencing "Failed to connect" error message repeatedly when connecting to backend
**Status**: ✅ Fixed

---

## Problem Summary

Users were experiencing recurring "Failed to connect" errors when attempting to connect to the backend server, particularly when using ngrok tunnels from Google Colab.

### Root Causes Identified

1. **Async Connection Handling Issue**
   - The `connect()` method created a WebSocket but returned immediately
   - The frontend code waited only 1 second before checking connection status
   - Over slow networks (especially ngrok), connections took longer than 1 second
   - Result: False "Failed to connect" errors even when connection would eventually succeed

2. **Auto-Reconnect on Initial Failure**
   - The WebSocket auto-reconnect logic didn't distinguish between:
     - Initial connection failures (shouldn't auto-retry)
     - Dropped connections after success (should auto-retry)
   - Result: Repeated connection attempts flooding the console

3. **No Connection Timeout**
   - Connections could hang indefinitely without feedback
   - No clear timeout or error message for stuck connections

---

## Fixes Applied

### Fix 1: Promise-Based Connection ✅

**File**: `frontend/js/websocket_client.js`

**Changes**:
- Made `connect()` return a proper Promise
- Promise resolves when connection opens successfully
- Promise rejects when connection fails or times out
- Added 10-second connection timeout

**Before**:
```javascript
async connect(customUrl = null) {
    this.ws = new WebSocket(this.serverUrl);
    this.ws.onopen = () => this.handleOpen();
    // Returns immediately, doesn't wait for connection
}
```

**After**:
```javascript
async connect(customUrl = null) {
    return new Promise((resolve, reject) => {
        this.ws = new WebSocket(this.serverUrl);

        // 10-second timeout
        timeoutId = setTimeout(() => {
            this.ws.close();
            reject(new Error('Connection timeout'));
        }, 10000);

        this.ws.onopen = () => {
            clearTimeout(timeoutId);
            this.handleOpen();
            resolve(); // Promise resolves when connected
        };

        this.ws.onerror = (error) => {
            clearTimeout(timeoutId);
            reject(new Error('Connection failed'));
        };
    });
}
```

### Fix 2: Proper Error Handling ✅

**File**: `frontend/js/controls.js`

**Changes**:
- Used try-catch to handle connection errors properly
- No more arbitrary 1-second wait
- Connection waits for actual WebSocket open event
- Better error messages to user

**Before**:
```javascript
await this.wsClient.connect(backendUrl || null);
await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
if (this.wsClient.isConnected) {
    // Success
} else {
    this.showError('Failed to connect to server'); // Generic error
}
```

**After**:
```javascript
try {
    await this.wsClient.connect(backendUrl || null);
    // Connection successful - start capturing
    this.webcam.startCapture(...);
} catch (error) {
    this.showError(`Failed to connect: ${error.message}`);
}
```

### Fix 3: Smart Auto-Reconnect ✅

**File**: `frontend/js/websocket_client.js`

**Changes**:
- Added `wasConnected` flag to track if connection ever succeeded
- Auto-reconnect only triggers for dropped connections, not initial failures
- Prevents connection attempt spam on initial failure

**Before**:
```javascript
handleClose() {
    // Always tries to reconnect, even on initial failure
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), 2000);
    }
}
```

**After**:
```javascript
handleClose() {
    // Only auto-reconnect if we were previously connected
    if (this.wasConnected && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), 2000);
    } else if (!this.wasConnected) {
        console.log('Initial connection failed - not attempting auto-reconnect');
    }
}
```

### Fix 4: Enhanced Error Messages ✅

**File**: `frontend/js/websocket_client.js`

**Changes**:
- Added comprehensive troubleshooting checklist to console
- Context-aware error messages (ngrok vs localhost vs other)
- Clear actionable steps for users

**Error Output**:
```
❌ WebSocket error: Error: Connection timeout
❌ Failed to connect to: wss://prepotent-unexperientially-homer.ngrok-free.dev/ws

💡 Troubleshooting Checklist:
   1. ✓ Backend Running: Check Colab Cell 6 shows "Uvicorn running"
   2. ✓ ngrok Active: Verify ngrok URL matches what you entered
   3. ✓ URL Format: Should be https://xxx.ngrok-free.dev (no /ws suffix)
   4. ✓ Network: Check your internet connection
   5. ✓ Browser Console: Look for CORS or mixed content errors
```

---

## How to Verify the Fix

### Test Case 1: Successful Connection
1. Start backend in Colab (Cell 6)
2. Get ngrok URL (Cell 7)
3. Enter ngrok URL in frontend
4. Click "Connect"
5. **Expected**: Connection succeeds within 2-5 seconds
6. **Console Output**: "✅ WebSocket connected successfully"

### Test Case 2: Backend Not Running
1. Don't start backend
2. Try to connect
3. **Expected**: Error after 10 seconds with clear message
4. **No spam**: Only one error, no repeated connection attempts
5. **Console Output**: Troubleshooting checklist

### Test Case 3: Wrong URL
1. Start backend
2. Enter incorrect ngrok URL
3. Click "Connect"
4. **Expected**: Error after timeout or immediate failure
5. **Message**: "Check that ngrok tunnel is active"

### Test Case 4: Connection Drop
1. Connect successfully
2. Stop backend while connected
3. **Expected**: Auto-reconnect attempts (up to 5)
4. **Console Output**: "🔄 Reconnecting (attempt 1/5)..."

---

## Common Connection Issues & Solutions

### Issue: "Connection timeout - server did not respond within 10 seconds"

**Causes**:
- Backend not running
- ngrok tunnel inactive or expired
- Firewall blocking connection
- Wrong URL

**Solutions**:
1. ✅ Verify backend shows "Uvicorn running on http://0.0.0.0:8000"
2. ✅ Check ngrok tunnel is active (Cell 7 should show URL)
3. ✅ Try clicking "Reconnect" in ngrok tunnel cell
4. ✅ Verify URL format: `https://xxx.ngrok-free.dev` (no trailing slash or /ws)

### Issue: "WebSocket connection failed" (immediate)

**Causes**:
- URL format error
- CORS issue
- Mixed content (http frontend trying wss backend)

**Solutions**:
1. ✅ Check URL format - should start with `https://` or `wss://`
2. ✅ Don't add `/ws` suffix (frontend adds it automatically)
3. ✅ Open browser console (F12) and check for detailed error
4. ✅ Try opening backend URL in browser first to verify it's accessible

### Issue: Connection succeeds but no segmentation

**Causes**:
- Model not loaded
- GPU out of memory
- Webcam permission denied

**Solutions**:
1. ✅ Check Colab output for model loading errors
2. ✅ Verify GPU is available: `!nvidia-smi` in Colab
3. ✅ Check browser console for webcam permission errors
4. ✅ Try refreshing frontend page and reconnecting

### Issue: "Failed to initialize webcam"

**Causes**:
- Browser permission denied
- Webcam in use by another app
- Browser doesn't support getUserMedia

**Solutions**:
1. ✅ Click "Allow" when browser asks for webcam permission
2. ✅ Close other apps using webcam (Zoom, Teams, etc.)
3. ✅ Try different browser (Chrome/Edge recommended)
4. ✅ Check browser settings → Site settings → Camera

---

## URL Format Reference

### Correct URL Formats

✅ **ngrok (Colab)**:
- Enter: `https://prepotent-unexperientially-homer.ngrok-free.dev`
- Becomes: `wss://prepotent-unexperientially-homer.ngrok-free.dev/ws`

✅ **Localhost**:
- Leave empty or enter: `http://localhost:8000`
- Becomes: `ws://localhost:8000/ws`

✅ **Custom domain**:
- Enter: `https://myserver.com`
- Becomes: `wss://myserver.com/ws`

### Incorrect Formats (DON'T USE)

❌ **With /ws suffix**: `https://xxx.ngrok-free.dev/ws`
   - Frontend adds `/ws` automatically

❌ **Trailing slash**: `https://xxx.ngrok-free.dev/`
   - Can cause path issues

❌ **Mixed protocols**: `http://xxx.ngrok-free.dev`
   - ngrok uses HTTPS, should use WSS

---

## Testing Checklist

Before reporting connection issues, verify:

- [ ] Backend is running (Colab Cell 6)
- [ ] ngrok tunnel is active (Colab Cell 7)
- [ ] URL format is correct (no /ws, no trailing slash)
- [ ] Webcam permission granted
- [ ] Browser console shows no errors
- [ ] Internet connection is stable
- [ ] GPU is available in Colab (if using GPU models)
- [ ] No firewall blocking WebSocket connections

---

## Performance Expectations

### Connection Times

| Deployment | Expected Time | Max Timeout |
|------------|---------------|-------------|
| **Localhost** | 100-500ms | 2 seconds |
| **ngrok (Colab)** | 2-5 seconds | 10 seconds |
| **Cloud Server** | 1-3 seconds | 10 seconds |

### What's Normal

- ✅ First connection takes longer (model loading)
- ✅ Subsequent connections faster (model cached)
- ✅ ngrok connections slower than localhost
- ✅ "Connecting..." message for 2-5 seconds on ngrok
- ✅ Auto-reconnect after connection drop

### What's NOT Normal

- ❌ Connection hanging indefinitely (timeout after 10s)
- ❌ Repeated "Failed to connect" without user action
- ❌ Connection succeeding but no video
- ❌ Errors after every frame
- ❌ Browser freezing during connection

---

## Files Modified

1. **`frontend/js/websocket_client.js`**
   - Line 11: Added `wasConnected` flag
   - Line 71-126: Rewrote `connect()` with Promise and timeout
   - Line 132-140: Updated `handleOpen()` to set `wasConnected`
   - Line 194-235: Enhanced `handleError()` with troubleshooting
   - Line 240-262: Updated `handleClose()` with smart auto-reconnect
   - Line 267-277: Updated `disconnect()` to reset `wasConnected`

2. **`frontend/js/controls.js`**
   - Line 107-144: Rewrote `handleConnect()` with try-catch

---

## Summary

**Before**: Connection handling was unreliable with arbitrary timeouts and confusing error messages

**After**:
- ✅ Proper async/await with real WebSocket state
- ✅ 10-second timeout prevents hanging
- ✅ Smart auto-reconnect only on dropped connections
- ✅ Clear, actionable error messages
- ✅ Comprehensive troubleshooting guidance

**User Experience Impact**:
- No more false "Failed to connect" errors
- Clear feedback on connection progress
- Helpful error messages with specific troubleshooting steps
- Reliable connection over slow networks (ngrok)

---

**Status**: ✅ Complete and Tested
**Deployment**: Safe for Production
**Breaking Changes**: None - backward compatible

---

**End of Connection Fix Documentation**
