"""
Equity Research Assistant Bot - Status Checker
Validates that all backend services are running correctly
"""
import requests
import json

def check_service_health():
    """Check if all backend services are healthy"""
    base_url = "http://localhost:8081"
    
    print("🔍 Checking Equity Research Assistant Bot Status...")
    print("=" * 50)
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   API Status: {health_data.get('api_status', 'Unknown')}")
            print(f"   GROQ Client: {'✅' if health_data.get('groq_client') else '❌'}")
            print(f"   Equity Bot: {'✅' if health_data.get('equity_bot') else '❌'}")
            print(f"   RAG Pipeline: {'✅' if health_data.get('rag_pipeline') else '❌'}")
            print(f"   Agentic RAG: {'✅' if health_data.get('agentic_rag') else '❌'}")
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: FAILED (Error: {e})")
        return False
    
    # RAG status
    try:
        response = requests.get(f"{base_url}/rag/stats", timeout=5)
        if response.status_code == 200:
            rag_data = response.json()
            print("✅ RAG Status: ACTIVE")
            print(f"   Documents: {rag_data.get('total_documents', 0)}")
            print(f"   Files: {rag_data.get('total_files', 0)}")
            print(f"   Collection: {rag_data.get('collection_name', 'None')}")
        else:
            print(f"⚠️ RAG Status: Warning (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ RAG Status: FAILED (Error: {e})")
    
    # Market overview test
    try:
        response = requests.get(f"{base_url}/analysis/market-overview", timeout=10)
        if response.status_code == 200:
            print("✅ Market Analysis: AVAILABLE")
        else:
            print(f"⚠️ Market Analysis: Warning (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Market Analysis: FAILED (Error: {e})")
    
    print("\n" + "=" * 50)
    print("🎉 Backend Status Check Complete!")
    print("\n📝 Next Steps:")
    print("   1. Install Node.js if not already installed")
    print("   2. Run: npm install in the frontend directory")
    print("   3. Run: npm start in the frontend directory")
    print("   4. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    check_service_health()
