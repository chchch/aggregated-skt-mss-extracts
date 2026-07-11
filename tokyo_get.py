import json
import os
import requests
import time

# --- Configuration ---
JSON_FILE = 'tokyo.json'
OUTPUT_DIR = 'tokyo'

def download_tokyo_manifests():
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # Load the initial collection JSON
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{JSON_FILE}'. Please ensure it is in the same directory.")
        return

    # In IIIF API 3.0, manifests are nested under the 'items' key
    items = data.get('items', [])
    total_items = len(items)
    print(f"Found {total_items} items in the JSON file. Starting download...\n")

    for index, item in enumerate(items, start=1):
        url = item.get('id')
        
        # Ensure we are only grabbing items explicitly labeled as Manifests
        if not url or item.get('type') != 'Manifest':
            print(f"[{index}/{total_items}] Skipping non-manifest item.")
            continue

        # Extract the unique ID from the URL to use as the filename 
        # e.g., 'https://.../0001/manifest.json' -> '0001.json'
        try:
            ms_id = url.split('/')[-2]
            filename = f"{ms_id}.json"
        except IndexError:
            # Fallback just in case the URL structure changes
            filename = f"manifest_{index}.json"
            
        file_path = os.path.join(OUTPUT_DIR, filename)

        # Skip if we already have the file
        if os.path.exists(file_path):
            print(f"[{index}/{total_items}] Already exists: {filename}. Skipping.")
            continue

        try:
            print(f"[{index}/{total_items}] Downloading {filename}...", end=" ", flush=True)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse as JSON and save with indentation for readability
                manifest_data = response.json()
                with open(file_path, 'w', encoding='utf-8') as out_file:
                    json.dump(manifest_data, out_file, indent=2, ensure_ascii=False)
                print("Success.")
            else:
                print(f"Failed (Status Code: {response.status_code})")
                
        except Exception as e:
            print(f"Error: {e}")
            
        # 1-second delay to be polite to the server
        time.sleep(1)

    print("\nFinished downloading Tokyo manifests.")

if __name__ == "__main__":
    download_tokyo_manifests()
