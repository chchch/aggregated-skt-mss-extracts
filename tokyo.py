import os
import json
import csv
import re

# --- Configuration ---
INPUT_DIR = 'tokyo'
OUTPUT_FILE = 'tokyo.csv'

# The dynamic extract fields we are looking for
EXTRACT_LABELS = ['rubric', 'finalRubric', 'explicit']

def clean_json_text(text):
    """
    Cleans the JSON text values:
    1. Removes any stray HTML tags (like <b> or <i>)
    2. Cleans up excess whitespace and newlines
    """
    if not text:
        return ""
        
    # Remove HTML tags using a regular expression
    text_no_tags = re.sub(r'<.*?>', '', text)
    
    # Strip excess whitespace
    cleaned_text = re.sub(r'\s+', ' ', text_no_tags).strip()
    
    return cleaned_text

def process_tokyo_json():
    # Ensure input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Error: The directory '{INPUT_DIR}' does not exist.")
        return

    # Prepare the CSV file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write a header for the fixed columns
        writer.writerow(['ID No.', 'Title', 'Author', 'Extracts...'])

        # Iterate through all json files in the directory
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(INPUT_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading JSON in {filename}. Skipping.")
                    continue
            
            # The metadata is stored as a list of dictionaries
            metadata_list = data.get('metadata', [])
            
            # Convert the list of dictionaries into a single, flat dictionary for easy lookup
            metadata_dict = {}
            for item in metadata_list:
                label = item.get('label')
                value = item.get('value')
                if label and value:
                    metadata_dict[label] = clean_json_text(value)
                    
            # Extract the fixed columns (with defaults if they are missing)
            id_no = metadata_dict.get('msIdentifier_idno', 'Unknown ID')
            title = metadata_dict.get('title', 'Unknown Title')
            author = metadata_dict.get('author', 'Unknown Author')
            
            row_data = [id_no, title, author]
            
            # Extract the dynamic sections for the jagged CSV
            for extract_label in EXTRACT_LABELS:
                if extract_label in metadata_dict:
                    formatted_extract = f"{extract_label}: {metadata_dict[extract_label]}"
                    row_data.append(formatted_extract)
                    
            # Write the jagged row to the CSV
            writer.writerow(row_data)
            print(f"Processed: {id_no} - {title}")

    print(f"\nFinished processing. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_tokyo_json()
