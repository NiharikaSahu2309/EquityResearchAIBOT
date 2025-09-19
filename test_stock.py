import requests
import json

def test_stock_fetch():
    url = "http://localhost:8083/stock/fetch"
    data = {"symbol": "AAPL"}
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Stock fetch successful!")
            print(f"Symbol: {result.get('symbol')}")
            print(f"Latest Price: ${result.get('stock_data', {}).get('latest_price', 'N/A')}")
            print(f"Charts created: {len(result.get('charts', []))}")
        else:
            print("❌ Stock fetch failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stock_fetch()
