import requests
import os

def test_upload():
    file_path = r"c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\Stock data\indexData.csv"
    url = "http://localhost:8081/upload/csv"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': ('indexData.csv', f, 'text/csv')}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
        else:
            print("❌ Upload failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()
