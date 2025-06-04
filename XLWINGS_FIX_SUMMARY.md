# XLWings Fix Summary - InvVzdProcessor

## Problem
The refactored InvVzdProcessor was only writing to one sheet, but it needs to write to 3 sheets like the original:
1. **Seznam účastníků** (B4) - Student names
2. **Seznam aktivit** (C3) - Activities data
3. **Přehled** (C3) - Overview (activity number + student name combinations)

## Solution Implemented

### 1. Updated `_copy_with_xlwings_invvzd` method
- Now writes to all three sheets instead of just one
- Opens Excel with `visible=True` like the original
- Properly handles all three data sections

### 2. Added `_extract_student_names` method
- Extracts student names from source file column B
- Starts from row 11 for 16h version, row 10 for 32h version
- Stops after two consecutive empty rows

### 3. Added `_create_overview` method
- Creates overview data combining students with activity numbers
- For each activity, creates entries for all students
- Format: [activity_number, student_name]

### 4. Added `_verify_sdp_sums` method
- Verifies SDP sums match total hours
- Checks activities total vs SDP forma and tema ranges
- Reports any mismatches as errors

### 5. Updated `_process_single_file` method
- Stores source file path in `_current_source_file` for xlwings to access

## Key Changes from Basic Implementation

```python
# Before (writing only activities to one sheet):
target_sheet.range('A3').value = activities_df.values

# After (writing to three sheets):
# 1. Student names
sheet.range("B4").options(ndim="expand", transpose=True).value = student_names

# 2. Activities with correct columns
sheet.range("C3").options(ndim="expand").value = activities_data.values

# 3. Overview data
sheet.range("C3").options(ndim="expand").value = overview_data
```

## Testing Notes

- On Linux: Falls back to basic Excel writing (no xlwings)
- On Windows: Will use full xlwings functionality with all 3 sheets
- Test files process successfully on Linux with basic mode
- Full functionality requires Windows with MS Excel installed

## Files Modified

1. `/root/vyvoj_sw/electron_app/src/python/tools/inv_vzd_processor.py`
   - Updated `_copy_with_xlwings_invvzd` method
   - Added helper methods for student extraction and overview creation
   - Added SDP verification
   - Added traceback import for better error handling

## Next Steps for Windows Testing

When testing on Windows:
1. Verify all 3 sheets are populated correctly
2. Check that Excel formatting is preserved
3. Confirm SDP sums verification works
4. Test with both 16h and 32h versions