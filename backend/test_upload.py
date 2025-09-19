import requests

# Test the backend upload endpoint
def test_upload():
    url = "http://localhost:8000/upload/csv"
    
    # Read a sample CSV file
    with open("../Stock data/indexData.csv", "rb") as f:
        files = {"file": ("indexData.csv", f, "text/csv")}
        response = requests.post(url, files=files)
        
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_upload()
