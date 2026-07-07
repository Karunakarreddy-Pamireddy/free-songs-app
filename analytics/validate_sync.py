import os
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"
DATA_PATH = "../storage/data/analytics.csv"

def authenticate_admin():
    """Retrieves access credentials to hit protected backend analytics routes."""
    try:
        res = requests.post(f"{API_URL}/token", data={"username": "admin", "password": "admin123"})
        if res.status_code == 200:
            return res.json().get("access_token")
    except Exception:
        return None
    return None

def verify_data_synchronization():
    print("[*] Initiating Data Sync Validation Checks...")
    
    # Check 1: Ensure localized CSV exists
    if not os.path.exists(DATA_PATH):
        print("[-] Skip: No data logs file accumulated locally yet. Perform streaming actions first.")
        return

    # Load local metrics framework calculations
    local_df = pd.read_csv(DATA_PATH)
    local_count = len(local_df)

    # Check 2: Ping backend REST API layer variables
    token = authenticate_admin()
    if not token:
        print("[-] System Validation Error: Backend server offline or admin login credentials failed.")
        print("[*] Please ensure 'uvicorn app.main:app' is running on port 8000.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        api_res = requests.get(f"{API_URL}/analytics/summary", headers=headers)
        if api_res.status_code != 200:
            print(f"[-] API Validation Connection Error. Status: {api_res.status_code}")
            return
            
        api_data = api_res.json()
        api_count = api_data.get("total_engagements", 0)

        # Cross-reference metrics assertion
        print("--- RUNNING DATA INTEGRITY AUDIT ---")
        print(f"[*] Local Storage Dataset Records Count: {local_count}")
        print(f"[*] FastAPI Remote Router Metric Response: {api_count}")

        if local_count == api_count:
            print("[+] PASS: Local CSV storage maps with 100% precision to FastAPI API vectors!")
            
            # Sub-vector structural integrity deep checking
            local_streams = len(local_df[local_df['action'] == 'stream'])
            api_streams = api_data.get("action_distribution", {}).get("stream", 0)
            
            if local_streams == api_streams:
                print("[+] PASS: Interaction distributions are structurally verified.")
            else:
                print("[-] FAIL: Discrepancy observed inside sub-vector action distributions.")
        else:
            print("[-] FAIL: Data sync mismatch noticed! Check file locking mechanisms.")

    except Exception as e:
        print(f"[-] Disastrous execution crash during sync auditing sequence: {str(e)}")

if __name__ == "__main__":
    verify_data_synchronization()