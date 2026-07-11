import os
import csv
import re
from bs4 import BeautifulSoup

# --- Configuration ---
INPUT_DIR = 'cambridge'
OUTPUT_FILE = 'cambridge.csv'

# Common TEI tags that contain manuscript extracts
EXTRACT_TAGS = ['incipit', 'explicit', 'finalRubric', 'colophon', 'rubric']

def clean_tei_text(tag):
    """
    Cleans a BeautifulSoup tag according to the specific TEI rules:
    1. Removes all <del> tags entirely (keeping <add> by default).
    2. Extracts the text.
    3. Removes anything inside square brackets [...].
    4. Cleans up excess whitespace and newlines.
    """
    if not tag:
        return ""

    # 1. Destroy all <del> tags within this element
    for del_tag in tag.find_all('del'):
        del_tag.decompose()
        
    # 2. Extract text (adding spaces between elements to avoid squishing words)
    raw_text = tag.get_text(separator=' ')
    
    # 3. Remove everything in square brackets (e.g., [p1, l1])
    no_brackets = re.sub(r'\[.*?\]', '', raw_text)
    
    # 4. Strip excess whitespace and newlines
    cleaned_text = re.sub(r'\s+', ' ', no_brackets).strip()
    
    return cleaned_text

def process_manuscripts():
    # Ensure input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Error: The directory '{INPUT_DIR}' does not exist.")
        return

    # Prepare the CSV file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write a header (optional, but good practice). 
        # Since it's jagged, we just label the first few fixed columns.
        writer.writerow(['ID No.', 'Title', 'Author', 'Extracts...'])

        # 1. Run through xml files in the directory
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith('.xml'):
                continue
                
            filepath = os.path.join(INPUT_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as xml_file:
                # Use 'xml' parser to handle TEI namespaces properly
                soup = BeautifulSoup(xml_file, 'xml')
                
                # Get ID no.
                ms_identifier = soup.find('msIdentifier')
                id_no = ""
                if ms_identifier and ms_identifier.find('idno'):
                    id_no = ms_identifier.find('idno').get_text(strip=True)

                # 2. Handle multi-text manuscripts (find all msItem tags)
                ms_items = soup.find_all('msItem')
                
                for item in ms_items:
                    row_data = [id_no]
                    
                    # Extract Title
                    title_tag = item.find('title')
                    title = clean_tei_text(title_tag) if title_tag else "Unknown Title"
                    row_data.append(title)
                    
                    # Extract Author
                    author_tag = item.find('author')
                    author = clean_tei_text(author_tag) if author_tag else "Unknown Author"
                    row_data.append(author)
                    
                    # 3 & 4. Extract sections (Incipit, Explicit, etc.)
                    # We look for children of the msItem that match our extract tags
                    for extract_tag_name in EXTRACT_TAGS:
                        # find_all is used in case there are multiple of the same tag
                        found_tags = item.find_all(extract_tag_name)
                        for found_tag in found_tags:
                            cleaned_extract = clean_tei_text(found_tag)
                            if cleaned_extract:
                                # Format as "tagName: extracted text"
                                formatted_extract = f"{extract_tag_name}: {cleaned_extract}"
                                row_data.append(formatted_extract)
                    
                    # Write the jagged row to the CSV
                    writer.writerow(row_data)
                    print(f"Processed: {id_no} - {title}")

    print(f"\nFinished processing. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_manuscripts()
