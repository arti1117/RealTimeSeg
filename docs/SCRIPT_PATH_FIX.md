# Script Path Fix - Frontend Startup Scripts

**Date**: 2025-10-28
**Type**: Bug Fix
**Priority**: High (blocking frontend startup)

## Problem

After reorganizing project files and moving scripts to `scripts/` directory, the frontend startup scripts failed with:

```
scripts/start_frontend.sh: line 18: cd: scripts/frontend: No such file or directory
FileNotFoundError: [Errno 2] No such file or directory: '/home/arti/Documents/RealTimeSeg/favicon.ico'
```

**Root Cause**: Scripts were trying to navigate to `scripts/frontend` instead of going up to project root and then into `frontend/`.

## Solution Applied

### 1. Fixed Linux/Mac Script (`scripts/start_frontend.sh`)

**Before**:
```bash
cd "$(dirname "$0")/frontend"
```

**After**:
```bash
cd "$(dirname "$0")/../frontend"
```

**Explanation**: When script is in `scripts/` directory, `$(dirname "$0")` resolves to `scripts/`, so we need `../` to go up one level to project root before entering `frontend/`.

### 2. Fixed Windows Script (`scripts/start_frontend.bat`)

**Before**:
```batch
cd frontend
```

**After**:
```batch
cd /d "%~dp0..\frontend"
```

**Explanation**:
- `%~dp0` = directory containing the batch file (with trailing backslash)
- `..` = go up one directory level
- `/d` = change drive letter if needed

### 3. Updated Documentation References

Updated all documentation to reference correct script paths:

#### Colab Notebook (`notebooks/colab_deployment.ipynb`)
- Cell 0 (Setup Instructions): `./start_frontend.sh` → `./scripts/start_frontend.sh`
- Cell 12 (Next Steps): `./start_frontend.sh` → `./scripts/start_frontend.sh`
- Cell 17 (Troubleshooting): `./start_frontend.sh` → `./scripts/start_frontend.sh` and `start_frontend.bat` → `scripts\start_frontend.bat`

#### CLAUDE.md
- Already correctly referenced: `./scripts/start_frontend.sh` ✓

## Verification

**Path Resolution Test**:
```bash
# From project root
cd /home/arti/Documents/RealTimeSeg
./scripts/start_frontend.sh
# ✓ Correctly navigates to: /home/arti/Documents/RealTimeSeg/frontend
# ✓ Serves files from correct location
```

**Script Syntax Validation**:
```bash
bash -n scripts/start_frontend.sh
# ✓ Script syntax is valid
```

## Files Modified

1. ✅ `scripts/start_frontend.sh` - Fixed path navigation (line 18)
2. ✅ `scripts/start_frontend.bat` - Fixed path navigation (line 18)
3. ✅ `notebooks/colab_deployment.ipynb` - Updated 3 references in cells 0, 12, 17
4. ✅ `docs/SCRIPT_PATH_FIX.md` - This documentation (created)

## Usage

Both scripts now work correctly from project root:

```bash
# Linux/Mac
./scripts/start_frontend.sh

# Windows
scripts\start_frontend.bat
```

Scripts will:
1. Navigate from `scripts/` → `../frontend/` (up one level, then into frontend)
2. Start Python HTTP server on port 8080
3. Serve frontend files correctly from `/frontend/` directory

## Related Issues Fixed

This fix resolves several cascading errors:
- ❌ Directory navigation error → ✅ Fixed
- ❌ FileNotFoundError for favicon.ico → ✅ Fixed (serves from correct directory)
- ❌ BrokenPipeError in HTTP server → ✅ Fixed (proper file serving)
- ❌ Incorrect documentation → ✅ Fixed (updated all references)

## Testing Checklist

- [x] Script syntax validation passed
- [x] Path navigation resolves correctly
- [x] Documentation updated with correct paths
- [x] Both Linux and Windows scripts fixed
- [x] Colab notebook references updated

## Status

✅ **Complete** - All script path issues resolved and documentation updated.

---

**Note**: This fix ensures the frontend startup scripts work correctly after the file organization changes that moved scripts from project root to the `scripts/` directory.
