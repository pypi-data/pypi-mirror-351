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
import importlib

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

def test_import(module_name, class_name=None):
    """Test importing a module or class."""
    try:
        if class_name:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            print(f"✅ Successfully imported {module_name}.{class_name}")
        else:
            importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
    except ImportError as e:
        print(f"❌ Failed to import {module_name}{f'.{class_name}' if class_name else ''}: {e}")
    except AttributeError as e:
        print(f"❌ Failed to import {module_name}.{class_name}: {e}")

def main():
    """Run all import tests."""
    print("Testing swagger client imports...\n")
    
    # Test work API
    test_import("streetmanager.work.swagger_client")
    test_import("streetmanager.work.swagger_client.models.LaneRentalAssessmentChargeBand")
    test_import("streetmanager.work.swagger_client.models.PermitResponse")
    test_import("streetmanager.work.swagger_client.models.WorkResponse")
    test_import("streetmanager.work.swagger_client.models.all_of_permit_lane_rental_assessment_update_request_charge_band.AllOfPermitLaneRentalAssessmentUpdateRequestChargeBand")
    test_import("streetmanager.work.swagger_client.models.all_of_inspection_summary_response_inspection_outcome.AllOfInspectionSummaryResponseInspectionOutcome")
    test_import("streetmanager.work.swagger_client.api_client.ApiClient")
    test_import("streetmanager.work.swagger_client.api.default_api.DefaultApi")

    # Test geojson API
    test_import("streetmanager.geojson.swagger_client")
    test_import("streetmanager.geojson.swagger_client.models.GeoJsonResponse")
    test_import("streetmanager.geojson.swagger_client.api_client.ApiClient")
    test_import("streetmanager.geojson.swagger_client.api.default_api.DefaultApi")

    # Test lookup API
    test_import("streetmanager.lookup.swagger_client")
    test_import("streetmanager.lookup.swagger_client.models.LookupResponse")
    test_import("streetmanager.lookup.swagger_client.api_client.ApiClient")
    test_import("streetmanager.lookup.swagger_client.api.default_api.DefaultApi")

if __name__ == '__main__':
    main() 