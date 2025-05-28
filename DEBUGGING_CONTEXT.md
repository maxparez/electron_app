# Debugging Context - InvVzd 400 Error

## Current Status (2025-05-28 20:08)

### ✅ Completed Features:
- **ZorSpec tool enhancements** - fully implemented and working:
  - Auto-scan for files with "Úvod a postup vyplňování" sheet
  - Version detection (16h/32h) from B1 cell
  - Version display for each file
  - Warning for mixed versions
  - Auto-save to source folder
  - Clickable file links in results

### 🐛 Current Issue:
**InvVzd tool returns 400 BAD REQUEST error**

**Symptoms:**
- Frontend console shows: `POST http://localhost:5000/api/process/inv-vzd-paths 400 (BAD REQUEST)`
- Error message: "Zpracování selhalo"
- Python server log shows no detailed information about the request

**What we've tried:**
1. Added comprehensive logging to server.py
2. Added print statements to InvVzd endpoint
3. Added console.log to frontend requests

**Current debug state:**
- Added `print("=== InvVzd Processing Started ===")` at start of endpoint
- Added `print(f"Received data: {data}")` to see request data
- Added exception handling with traceback printing

### 🔧 Next Steps:
1. **Restart Python server** to apply debug changes
2. **Test InvVzd tool** and check Python console output
3. **Identify root cause** from debug output:
   - Does request reach the endpoint?
   - What data is received?
   - Where exactly does it fail?
4. **Fix the underlying issue**

### 📁 Files Modified:
- `src/python/server.py` - Added debug prints to InvVzd endpoint
- `src/electron/renderer/renderer.js` - ZorSpec enhancements (auto-save, links)
- `src/python/tools/zor_spec_dat_processor.py` - Enhanced info messages
- `src/electron/renderer/styles.css` - New UI styles for output sections

### 🎯 Expected Debug Output:
When testing InvVzd, Python console should show:
```
=== InvVzd Processing Started ===
Received data: {'filePaths': [...], 'templatePath': '...', 'options': {...}}
```

If this doesn't appear, the request isn't reaching the endpoint.
If it appears but then fails, we'll see the exact error and traceback.

### 💾 Git Status:
- Last commit: `de83509` - Debug print statements added
- Branch: `master`
- All changes pushed to GitHub