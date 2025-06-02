#!/usr/bin/env python3
"""
Test script to verify that InvVzd validation errors are displayed correctly in the UI
"""

import json
import requests
import sys
import os

# Configuration
API_URL = "http://localhost:5000/api"

def test_error_display():
    """Test that validation errors are returned and displayed properly"""
    
    # Test data - file with missing dates
    test_data = {
        "filePaths": [
            "/root/vyvoj_sw/electron_app/tests/test1/32_hodin_inovativniho_vzdelavani_MS_ZS_SDP.xlsx"
        ],
        "templatePath": "/root/vyvoj_sw/electron_app/template_32_hodin.xlsx",
        "options": {
            "courseType": "32",
            "keep_filename": True,
            "optimize": False
        }
    }
    
    print("Sending test request to InvVzd processor...")
    print(f"File: {test_data['filePaths'][0]}")
    print(f"Template: {test_data['templatePath']}")
    
    try:
        response = requests.post(
            f"{API_URL}/process/inv-vzd-paths",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse status code: {response.status_code}")
        
        result = response.json()
        print(f"\nResponse JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Check if errors are in the response
        if "errors" in result:
            print(f"\n✓ Errors found in response: {len(result['errors'])} errors")
            for error in result['errors']:
                print(f"  - {error}")
        else:
            print("\n✗ No errors in response")
            
        # Check if info messages are in the response
        if "info" in result:
            print(f"\n✓ Info messages found: {len(result['info'])} messages")
            for info in result['info']:
                print(f"  - {info}")
        else:
            print("\n✗ No info messages in response")
            
        # Check if data is present
        if "data" in result:
            print(f"\n✓ Data field present")
            if "errors" in result["data"]:
                print(f"  - Data errors: {len(result['data']['errors'])}")
            if "info" in result["data"]:
                print(f"  - Data info: {len(result['data']['info'])}")
            if "files" in result["data"]:
                print(f"  - Files processed: {len(result['data']['files'])}")
        else:
            print("\n✗ No data field in response")
            
        # Check status
        print(f"\nStatus: {result.get('status', 'N/A')}")
        print(f"Message: {result.get('message', 'N/A')}")
        
        # Verify UI will display this correctly
        if result.get('status') in ['success', 'partial'] or (result.get('data') and result.get('data', {}).get('info')):
            print("\n✓ UI will display the detailed report!")
        else:
            print("\n✗ UI will show generic error message")
            
    except Exception as e:
        print(f"\nError: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(test_error_display())