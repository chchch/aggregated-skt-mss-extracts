import os
import csv
import re
from bs4 import BeautifulSoup

# --- Configuration ---
INPUT_DIR = 'pandit_html'
OUTPUT_FILE = 'pandit.csv'

def clean_html_text(text):
    """
    Cleans up extracted text by replacing multiple spaces, 
    newlines, and tabs with a single space.
    """
    if not text:
        return "N/A"
    return re.sub(r'\s+', ' ', text).strip()

def process_pandit_html():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: The directory '{INPUT_DIR}' does not exist.")
        return

    # Prepare the CSV file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write the exact header columns you requested
        writer.writerow(['Manuscript', 'Work', 'Extract kind', 'Extract text'])

        # Keep track of how many items we process
        total_items_extracted = 0

        # Iterate through all html files in the directory
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith('.html'):
                continue

            filepath = os.path.join(INPUT_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
            # Find all search result articles in the file
            # Based on the HTML, each item is in an <article> tag with the class "quick-search-results-item"
            articles = soup.find_all('article', class_='quick-search-results-item')
            
            for article in articles:
                # 1. Extract Manuscript
                ms_container = article.find('div', class_='field--name-field-extract-manuscript')
                ms_text = ms_container.find('div', class_='field__item').get_text(separator=' ') if ms_container else ""
                
                # 2. Extract Work
                work_container = article.find('div', class_='field--name-field-extract-work')
                work_text = work_container.find('div', class_='field__item').get_text(separator=' ') if work_container else ""
                
                # 3. Extract kind
                kind_container = article.find('div', class_='field--name-field-extract-kind')
                kind_text = kind_container.find('div', class_='field__item').get_text(separator=' ') if kind_container else ""
                
                # 4. Extract text
                # We use separator=' ' to ensure <br> or <p> tags turn into spaces rather than squishing words together
                text_container = article.find('div', class_='field--name-field-extract-text')
                extract_text = text_container.find('div', class_='field__item').get_text(separator=' ') if text_container else ""
                
                # Clean the extracted strings
                row_data = [
                    clean_html_text(ms_text),
                    clean_html_text(work_text),
                    clean_html_text(kind_text),
                    clean_html_text(extract_text)
                ]
                
                writer.writerow(row_data)
                total_items_extracted += 1
                
            print(f"Processed {filename}: Extracted {len(articles)} items.")

    print(f"\nFinished! Extracted a total of {total_items_extracted} items into {OUTPUT_FILE}.")

if __name__ == "__main__":
    process_pandit_html()
