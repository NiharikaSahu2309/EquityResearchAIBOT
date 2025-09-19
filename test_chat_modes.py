import requests
import json

def test_chat_modes():
    base_url = 'http://localhost:8085'
    
    # Test agentic mode
    print("Testing Agentic Mode...")
    try:
        response = requests.post(f'{base_url}/chat', json={
            'message': 'What is Suzlon revenue in Q1 FY26?',
            'mode': 'agentic'
        })
        print(f"Agentic Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Agentic Response: {data['message'][:200]}...")
        else:
            print(f"Agentic Error: {response.text}")
    except Exception as e:
        print(f"Agentic Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test search mode  
    print("Testing Search Mode...")
    try:
        response = requests.post(f'{base_url}/chat', json={
            'message': 'Suzlon revenue',
            'mode': 'search'
        })
        print(f"Search Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Search Response: {data['message'][:300]}...")
        else:
            print(f"Search Error: {response.text}")
    except Exception as e:
        print(f"Search Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test standard mode
    print("Testing Standard Mode...")
    try:
        response = requests.post(f'{base_url}/chat', json={
            'message': 'Hello, how are you?',
            'mode': 'standard'
        })
        print(f"Standard Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Standard Response: {data['message'][:200]}...")
        else:
            print(f"Standard Error: {response.text}")
    except Exception as e:
        print(f"Standard Exception: {e}")

if __name__ == "__main__":
    test_chat_modes()
