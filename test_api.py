import requests
import json

try:
    print("Making request to http://localhost:8085/rag/stats...")
    response = requests.get('http://localhost:8085/rag/stats')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response data:")
        print(json.dumps(data, indent=2))
        
        # Save to file for verification
        with open('rag_stats_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Response saved to rag_stats_response.json")
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error making request: {e}")
