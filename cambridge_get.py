import json
import os
import requests
import time

# --- Configuration ---
JSON_FILE = 'cambridge_sanskrit.json'
OUTPUT_DIR = 'cambridge'
BASE_URL = 'https://services.cudl.lib.cam.ac.uk/v1/metadata/tei/'

def download_tei_metadata():
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # Load the JSON data
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{JSON_FILE}'. Please ensure it is in the same directory.")
        return

    manifests = data.get('manifests', [])
    total_mss = len(manifests)
    print(f"Found {total_mss} manuscripts in the JSON file. Starting download...\n")

    # Iterate through each manifest and download the TEI file
    for index, item in enumerate(manifests, start=1):
        label = item.get('label')
        
        if not label:
            print(f"[{index}/{total_mss}] Skipping item with missing label.")
            continue
            
        file_path = os.path.join(OUTPUT_DIR, f"{label}.xml")
        
        # Skip download if we already have the file (useful if the script is interrupted)
        if os.path.exists(file_path):
            print(f"[{index}/{total_mss}] Already exists: {label}.xml. Skipping.")
            continue

        url = f"{BASE_URL}{label}"
        
        try:
            print(f"[{index}/{total_mss}] Downloading {label}...", end=" ", flush=True)
            response = requests.get(url, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                with open(file_path, 'w', encoding='utf-8') as xml_file:
                    xml_file.write(response.text)
                print("Success.")
            else:
                print(f"Failed (Status Code: {response.status_code})")
                
        except requests.RequestException as e:
            print(f"Error: {e}")
            
        # Be polite to the server: add a small delay between requests
        time.sleep(1)

    print("\nFinished downloading TEI metadata.")

if __name__ == "__main__":
    download_tei_metadata()
