import requests
import json

def test_rag_search():
    print("Testing RAG Search...")
    try:
        response = requests.post('http://localhost:8085/chat', 
            json={
                'message': 'Suzlon revenue',
                'mode': 'search'
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message', '')[:500]}...")
            print(f"Mode: {data.get('metadata', {}).get('mode')}")
            print(f"Sources: {data.get('metadata', {}).get('sources', [])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_agentic_rag():
    print("\nTesting Agentic RAG...")
    try:
        response = requests.post('http://localhost:8085/chat',
            json={
                'message': 'What is Suzlon revenue in Q1 FY26?',
                'mode': 'agentic'
            },
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message', '')[:500]}...")
            print(f"Mode: {data.get('metadata', {}).get('mode')}")
            print(f"Sources: {data.get('metadata', {}).get('sources', [])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_rag_search()
    test_agentic_rag()
