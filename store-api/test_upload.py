import httpx
import os

# File to upload
FILE_PATH = "/Users/hanxiaodi/www/node/store/音乐.png"
UPLOAD_URL = "http://127.0.0.1:8000/api/v1/upload"

def test_upload():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH} to {UPLOAD_URL}...")
    
    try:
        files = {'file': open(FILE_PATH, 'rb')}
        # Note: If endpoint doesn't require auth, we don't send headers.
        # If it did, we would need to login first.
        response = httpx.post(UPLOAD_URL, files=files, timeout=30.0)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and response.json().get("code") == 200:
            print("Upload Successful!")
            print(f"URL: {response.json()['data']}")
        else:
            print("Upload Failed!")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_upload()
