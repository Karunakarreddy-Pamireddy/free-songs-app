import os
import requests

# Point this to your FastAPI local or server instance address
API_URL = "http://127.0.0.1:8000"

def execute_automated_upload(file_path: str):
    """
    Simulates an automated AI agent workflow:
    1. Authenticates using administration credentials
    2. Secures a signed JWT access token
    3. Streams the target audio track directly into the FastAPI backend
    """
    if not os.path.exists(file_path):
        print(f"[-] Automation Error: Target file '{file_path}' does not exist.")
        return

    filename = os.path.basename(file_path)
    session = requests.Session()

    print("[*] Initiating Automation Sequence...")
    print("[*] Authenticating with backend identity systems...")
    
    # Form data required by OAuth2PasswordRequestForm in FastAPI
    login_payload = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        # Step 1 & 2: Authenticate and retrieve token
        response = session.post(f"{API_URL}/token", data=login_payload)
        
        if response.status_code != 200:
            print(f"[-] Authentication Failed. Server returned status code: {response.status_code}")
            print(f"[-] Server Response: {response.text}")
            return
            
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("[+] Authentication Successful! Token retrieved.")

        # Step 3: Configure Authorization headers and upload file stream
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print(f"[*] Extracting raw binary from: {filename}...")
        with open(file_path, "rb") as audio_binary:
            # Prepare files payload for multipart/form-data encoding
            files = {
                "file": (filename, audio_binary, "audio/mpeg")
            }
            
            print("[*] Streaming payload data directly to secure storage tier...")
            upload_response = session.post(
                f"{API_URL}/upload-song/", 
                headers=headers, 
                files=files
            )
            
        if upload_response.status_code in [200, 201]:
            print("[+] Automation Cycle Completed Successfully!")
            print(f"[+] Server Response Metadata: {upload_response.json()}")
        else:
            print(f"[-] Upload Pipeline Rejected. Status Code: {upload_response.status_code}")
            print(f"[-] Error Logs: {upload_response.text}")

    except requests.exceptions.ConnectionError:
        print("[-] System Error: Could not connect to FastAPI server. Ensure uvicorn is running on port 8000.")
    except Exception as e:
        print(f"[-] Unexpected Exception occurred: {str(e)}")

if __name__ == "__main__":
    # Placeholder path for structural local script verification
    print("[!] Automation script compiled successfully.")
    print("[!] To run execution pass an explicit mp3 path string to execute_automated_upload().")