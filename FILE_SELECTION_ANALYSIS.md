# File Selection Analysis - Individual Files vs Folder Selection

## Overview

The Electron app supports two modes of file selection:
1. **Individual file selection** - "Vybrat soubory" button
2. **Folder selection** - "Vybrat ze složky" button

## Frontend Implementation (renderer.js)

### Individual File Selection Flow

1. **Button Click Handler** (line 64):
   ```javascript
   elements.invSelectBtn.addEventListener('click', () => selectFiles('inv-vzd'));
   ```

2. **selectFiles Function** (lines 156-239):
   - Calls `window.electronAPI.openFile({ multiple: true })` to open file dialog
   - Allows multiple file selection
   - For InvVzd tool:
     - Checks if template is selected first
     - Validates each file against the template version
     - Only accepts files matching the template version (16h or 32h)
   - For ZorSpec tool:
     - Checks if files contain required "Úvod a postup vyplňování" sheet
     - Detects file version from the sheet content

3. **File Validation Process**:
   - Uses backend API endpoints to validate files:
     - `/api/detect/source-version` - for InvVzd files
     - `/api/detect/zor-spec-version` - for ZorSpec files
   - Shows warnings for incompatible files
   - Only adds valid files to the selection list

### Folder Selection Flow

1. **Button Click Handler** (line 65):
   ```javascript
   elements.invFolderBtn.addEventListener('click', selectInvFolder);
   ```

2. **selectInvFolder Function** (lines 341-366):
   - Calls `window.electronAPI.selectFolder()` to open folder dialog
   - Calls `scanFolderForAttendanceFiles()` to find suitable files

3. **scanFolderForAttendanceFiles Function** (lines 369-389):
   - Calls backend API `/api/select-folder` with folder path
   - Backend scans folder and returns list of valid attendance files
   - Automatically filters out:
     - Template files (containing "sablona" or "template")
     - Already processed output files
     - Non-attendance Excel files

## Backend Implementation (server.py & inv_vzd_processor.py)

### Individual File Processing

1. **API Endpoint** `/api/process/inv-vzd-paths` (lines 338-481 in server.py):
   - Receives list of file paths directly
   - Converts Windows paths to WSL paths if needed
   - Processes each file individually
   - Returns detailed results per file

2. **Processing Method** `process()` (lines 88-128 in inv_vzd_processor.py):
   - Validates all input files exist
   - Processes each file separately
   - Maintains per-file error/warning/info messages

### Folder Selection Processing

1. **API Endpoint** `/api/select-folder` (lines 194-239 in server.py):
   - Receives folder path
   - Calls `InvVzdProcessor.select_folder()`

2. **Folder Scanning** `select_folder()` (lines 977-1047 in inv_vzd_processor.py):
   - Lists all files in folder
   - Filters Excel files (.xlsx, .xls)
   - Excludes:
     - Temporary files (starting with ~$)
     - Output files (prefixed with version info)
     - Template files
   - Detects version for each potential attendance file
   - Returns only valid attendance files with version info

## Key Differences

### 1. File Selection Dialog
- **Individual**: Multi-select file dialog
- **Folder**: Single folder selection dialog

### 2. File Filtering
- **Individual**: User manually selects files, app validates after selection
- **Folder**: Automatic scanning and filtering by backend

### 3. Validation Timing
- **Individual**: Post-selection validation (shows warnings for invalid files)
- **Folder**: Pre-selection validation (only returns valid files)

### 4. User Experience
- **Individual**: 
  - More control over specific files
  - Can select files from different folders
  - Sees validation warnings
- **Folder**:
  - Faster for processing many files
  - Automatic detection of attendance files
  - No invalid files shown

### 5. Template Requirement
- Both modes require template selection first for InvVzd
- Template version determines which files are accepted

## File Path Handling

### Electron (main.js)
- Uses native dialog API with proper file filters
- Returns absolute file paths
- Supports both Windows and Unix paths

### Frontend (renderer.js)
- Converts WSL paths to Windows format for display
- Maintains original paths for backend processing

### Backend (Python)
- Converts Windows paths to WSL paths when running on Linux
- Handles both path formats transparently

## Error Handling

### Individual Selection
- Shows specific error messages for each invalid file
- Allows partial selection (some valid, some invalid)
- User can remove individual files from selection

### Folder Selection
- Shows summary of files found
- No individual file errors shown
- All or nothing approach

## Conclusion

The individual file selection provides more granular control and feedback, while folder selection offers convenience for batch processing. Both methods ultimately use the same backend processing logic, but differ in how files are discovered and validated.