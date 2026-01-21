"""
Test SuccessFactors Connection and Data Fetch
Run this to verify your SF connection and see actual data structure
"""

import asyncio
import json
from app.services.successfactors_client import SuccessFactorsClient
from app.services.sf_data_transformer import SFDataTransformer

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================

COMPANY_ID = "YOUR_COMPANY_ID"  # e.g., "SFPART123456"
USERNAME = "YOUR_USERNAME"       # e.g., "apiuser" (do NOT include @COMPANY_ID here)
PASSWORD = "YOUR_PASSWORD"
API_URL = "https://api.successfactors.eu"  # or .com for US data center

# ============================================

async def test_connection():
    """Test connection to SuccessFactors"""
    print("="*80)
    print("TESTING SUCCESSFACTORS CONNECTION")
    print("="*80)

    client = SuccessFactorsClient(
        company_id=COMPANY_ID,
        username=USERNAME,
        password=PASSWORD,
        api_url=API_URL
    )

    # Test connection
    print("\n1. Testing connection...")
    result = await client.test_connection()

    if result["success"]:
        print(f"✅ SUCCESS: {result['message']}")
        print(f"   API Version: {result.get('api_version', 'N/A')}")
        return client
    else:
        print(f"❌ FAILED: {result['message']}")
        print("\nTroubleshooting:")
        print("1. Check Company ID is correct")
        print("2. Verify username (should NOT include @COMPANYID)")
        print("3. Verify password")
        print("4. Check API URL matches your data center:")
        print("   - EU: https://api.successfactors.eu")
        print("   - US: https://api.successfactors.com")
        return None

async def fetch_entity_sample(client: SuccessFactorsClient, entity_name: str, limit: int = 5):
    """Fetch sample data from an entity"""
    print(f"\n--- Fetching {entity_name} (limit {limit}) ---")
    try:
        result = await client._make_request(entity_name, params={"$top": limit})

        # Extract results from OData response
        results = []
        if "d" in result:
            d_value = result["d"]
            if "results" in d_value:
                results = d_value["results"]
            elif isinstance(d_value, list):
                results = d_value
            elif isinstance(d_value, dict):
                results = [d_value]

        print(f"✅ Fetched {len(results)} records from {entity_name}")

        if results:
            print(f"\nSample {entity_name} record (first one):")
            print(json.dumps(results[0], indent=2, default=str))

        return results

    except Exception as e:
        print(f"❌ Error fetching {entity_name}: {str(e)}")
        return []

async def test_all_entities(client: SuccessFactorsClient):
    """Test fetching all common entities"""
    print("\n" + "="*80)
    print("FETCHING DATA FROM SUCCESSFACTORS")
    print("="*80)

    entities_to_test = [
        ("User", "Employees"),
        ("Position", "Positions"),
        ("FOBusinessUnit", "Business Units"),
        ("FODepartment", "Departments"),
        ("FODivision", "Divisions"),
        ("FOCostCenter", "Cost Centers"),
        ("FOLegalEntity", "Legal Entities"),
        ("FOLocation", "Locations"),
    ]

    results = {}

    for entity_name, display_name in entities_to_test:
        data = await fetch_entity_sample(client, entity_name, limit=3)
        results[entity_name] = data

        if not data:
            print(f"⚠️  No data or entity not available: {entity_name}")

    return results

async def test_transformation(results: dict):
    """Test data transformation"""
    print("\n" + "="*80)
    print("TESTING DATA TRANSFORMATION")
    print("="*80)

    transformer = SFDataTransformer()

    # Transform FOBusinessUnit
    if "FOBusinessUnit" in results and results["FOBusinessUnit"]:
        print("\n--- Transforming FOBusinessUnit ---")
        bu_data = results["FOBusinessUnit"][0]
        print("Original SF data:")
        print(json.dumps(bu_data, indent=2, default=str))

        transformed = transformer.transform_fo_business_unit(bu_data)
        print("\nTransformed to OrgChartAI format:")
        print(json.dumps(transformed, indent=2, default=str))

    # Transform User
    if "User" in results and results["User"]:
        print("\n--- Transforming User ---")
        user_data = results["User"][0]
        print("Original SF data:")
        print(json.dumps(user_data, indent=2, default=str))

        transformed = transformer.transform_user(user_data)
        print("\nTransformed to OrgChartAI format:")
        print(json.dumps(transformed, indent=2, default=str))

    # Transform Position
    if "Position" in results and results["Position"]:
        print("\n--- Transforming Position ---")
        position_data = results["Position"][0]
        print("Original SF data:")
        print(json.dumps(position_data, indent=2, default=str))

        transformed = transformer.transform_position(position_data)
        print("\nTransformed to OrgChartAI format:")
        print(json.dumps(transformed, indent=2, default=str))

async def test_field_availability():
    """Test which fields are available in your SF instance"""
    print("\n" + "="*80)
    print("CHECKING FIELD AVAILABILITY")
    print("="*80)

    client = SuccessFactorsClient(
        company_id=COMPANY_ID,
        username=USERNAME,
        password=PASSWORD,
        api_url=API_URL
    )

    # Fetch metadata
    print("\nFetching metadata to see available entities and fields...")
    try:
        metadata = await client._make_request("$metadata")
        print("✅ Metadata retrieved successfully")
        print("   You can inspect the metadata XML to see all available fields")

        # Save metadata to file
        with open("sf_metadata.xml", "w", encoding="utf-8") as f:
            if isinstance(metadata, dict):
                f.write(json.dumps(metadata, indent=2))
            else:
                f.write(str(metadata))

        print("   Saved to: sf_metadata.xml")

    except Exception as e:
        print(f"❌ Error fetching metadata: {e}")

async def generate_field_mapping_report(results: dict):
    """Generate a report of available fields for mapping"""
    print("\n" + "="*80)
    print("FIELD MAPPING REPORT")
    print("="*80)

    for entity_name, data_list in results.items():
        if data_list:
            print(f"\n--- {entity_name} Fields ---")
            sample_record = data_list[0]
            fields = list(sample_record.keys())
            print(f"Available fields ({len(fields)}):")
            for field in sorted(fields):
                value = sample_record[field]
                value_type = type(value).__name__
                print(f"  - {field} ({value_type})")

async def main():
    """Main test function"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "      SuccessFactors Integration Test Script".center(78) + "║")
    print("║" + "      OrgChartAI".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Test connection
    client = await test_connection()

    if not client:
        print("\n❌ Connection failed. Please check your credentials and try again.")
        return

    # Fetch data from all entities
    results = await test_all_entities(client)

    # Test transformation
    await test_transformation(results)

    # Generate field mapping report
    await generate_field_mapping_report(results)

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the field mapping report above")
    print("2. Update field mappings in app/models_successfactors.py if needed")
    print("3. Configure field mappings in the UI")
    print("4. Run full sync to import all data")
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
