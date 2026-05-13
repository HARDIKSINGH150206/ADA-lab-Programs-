"""
Test examples for Case Management API
Run these examples to validate the API endpoints
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api"
# Replace with actual JWT token from authentication
AUTH_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}


async def test_create_case():
    """Test creating a new case"""
    print("\n=== Test: Create Case ===")
    
    payload = {
        "case_type": "unpaid_wages",
        "employer_name": "ABC Manufacturing",
        "amount_owed": 50000.00,
        "period_start": "2025-01-01",
        "period_end": "2026-05-13",
        "contract_type": "written",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/cases",
            headers=headers,
            json=payload,
        )
    
    print(f"Status: {response.status_code}")
    case_data = response.json()
    print(f"Case ID: {case_data.get('id')}")
    print(json.dumps(case_data, indent=2))
    
    return case_data.get('id')


async def test_list_cases():
    """Test listing cases with filters"""
    print("\n=== Test: List Cases ===")
    
    async with httpx.AsyncClient() as client:
        # List all cases
        response = await client.get(
            f"{BASE_URL}/cases?skip=0&limit=10",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total cases: {data.get('total')}")
    print(json.dumps(data, indent=2))


async def test_get_case(case_id):
    """Test getting a specific case"""
    print("\n=== Test: Get Case ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cases/{case_id}",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


async def test_update_case(case_id):
    """Test updating a case"""
    print("\n=== Test: Update Case ===")
    
    payload = {
        "status": "intake_complete",
        "amount_owed": 75000.00,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{BASE_URL}/cases/{case_id}",
            headers=headers,
            json=payload,
        )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


async def test_analyze_case(case_id):
    """Test AI analysis of a case"""
    print("\n=== Test: Analyze Case (AI) ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/cases/{case_id}/analyze",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    case_data = response.json()
    print(f"Case Summary: {case_data.get('case_summary')}")
    print(f"Applicable Laws: {case_data.get('applicable_laws')}")
    print(f"What Should Happen: {case_data.get('what_should_happen')}")
    print(f"Next Steps: {case_data.get('next_steps')}")


async def test_filter_cases():
    """Test filtering cases by type and status"""
    print("\n=== Test: Filter Cases ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cases?case_type=unpaid_wages&status=draft",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total matching cases: {data.get('total')}")


async def test_search_cases():
    """Test searching cases by employer name"""
    print("\n=== Test: Search Cases ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cases?search=ABC",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Search results: {data.get('total')}")


async def test_delete_case(case_id):
    """Test deleting a case"""
    print("\n=== Test: Delete Case ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/cases/{case_id}",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


async def test_case_steps(case_id):
    """Test getting case steps"""
    print("\n=== Test: Get Case Steps ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cases/{case_id}/steps",
            headers=headers,
        )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


async def main():
    """Run all tests"""
    print("Starting Case Management API Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:20]}...")
    
    # Create a case
    case_id = await test_create_case()
    
    if case_id:
        # Get the case
        await test_get_case(case_id)
        
        # Update the case
        await test_update_case(case_id)
        
        # Analyze the case (requires ANTHROPIC_API_KEY)
        await test_analyze_case(case_id)
        
        # Get case steps
        await test_case_steps(case_id)
        
        # List all cases
        await test_list_cases()
        
        # Filter cases
        await test_filter_cases()
        
        # Search cases
        await test_search_cases()
        
        # Uncomment to delete the case
        # await test_delete_case(case_id)


if __name__ == "__main__":
    asyncio.run(main())
