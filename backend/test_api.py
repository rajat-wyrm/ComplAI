import asyncio
import httpx
import sys

async def test_api():
    print("🧪 Testing API endpoints...")
    
    # Test root endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            print(f"✅ Root endpoint: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test health endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            print(f"✅ Health endpoint: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test detailed health
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health/detailed")
            print(f"✅ Detailed health: {response.status_code}")
            data = response.json()
            print(f"   Status: {data['status']}")
            for component, status in data['components'].items():
                print(f"   - {component}: {status['status']}")
    except Exception as e:
        print(f"❌ Detailed health failed: {e}")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_api())
    sys.exit(0 if result else 1)
