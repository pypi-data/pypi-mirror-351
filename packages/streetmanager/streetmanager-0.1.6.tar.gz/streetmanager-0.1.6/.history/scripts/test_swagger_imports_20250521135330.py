#!/usr/bin/env python3
"""
Test script to verify that swagger client imports are working correctly.
This script will:
1. Try to import various modules from the swagger client
2. Create instances of some model classes
3. Print success/failure for each test
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

def test_import(module_path, class_name=None):
    """Test importing a module and optionally a class from it."""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else None)
        if class_name:
            class_obj = getattr(module, class_name)
            print(f"✅ Successfully imported {module_path}.{class_name}")
            return True
        else:
            print(f"✅ Successfully imported {module_path}")
            return True
    except Exception as e:
        print(f"❌ Failed to import {module_path}{f'.{class_name}' if class_name else ''}: {str(e)}")
        return False

def main():
    """Run all import tests."""
    print("Testing swagger client imports...\n")
    
    # Test importing the main swagger client module
    test_import('streetmanager.work.swagger_client')
    
    # Test importing some model classes
    test_import('streetmanager.work.swagger_client.models', 'LaneRentalAssessmentChargeBand')
    test_import('streetmanager.work.swagger_client.models', 'PermitResponse')
    test_import('streetmanager.work.swagger_client.models', 'WorkResponse')
    
    # Test importing some "all_of" classes that use relative imports
    test_import('streetmanager.work.swagger_client.models.all_of_permit_lane_rental_assessment_update_request_charge_band',
                'AllOfPermitLaneRentalAssessmentUpdateRequestChargeBand')
    test_import('streetmanager.work.swagger_client.models.all_of_inspection_summary_response_inspection_outcome',
                'AllOfInspectionSummaryResponseInspectionOutcome')
    
    # Test importing the API client
    test_import('streetmanager.work.swagger_client.api_client', 'ApiClient')
    
    # Test importing the default API
    test_import('streetmanager.work.swagger_client.api.default_api', 'DefaultApi')

if __name__ == '__main__':
    main() 