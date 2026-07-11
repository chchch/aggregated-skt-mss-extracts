import os
import csv
import re
from bs4 import BeautifulSoup
from collections import defaultdict

def extract_metadata(soup, field_name):
    """
    Finds a <b> tag matching the field_name, then captures all text 
    following it until it hits a line break (<br>), another bold tag (<b>), 
    or the end of the paragraph.
    """
    b_tag = soup.find('b', string=lambda t: t and field_name in t)
    if not b_tag:
        return ""
    
    extracted_text = []
    # Iterate through everything immediately after the <b> tag
    for sibling in b_tag.next_siblings:
        # Stop collecting if we hit a line break, a new paragraph, or another bold label
        if sibling.name in ['br', 'p', 'b', 'div']:
            break
        
        # If it's a string, grab it. If it's another tag (like <i>), get its text.
        if isinstance(sibling, str):
            extracted_text.append(sibling)
        else:
            extracted_text.append(sibling.get_text(separator=' '))
            
    # Clean up the final string and strip any rogue colons/spaces at the beginning
    raw_string = " ".join(extracted_text)
    return re.sub(r'\s+', ' ', raw_string).strip(' :')

def process_manuscripts(directory='ngmcp'):
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    # Dictionary to hold lists of rows for each series: {'A': [ ['Reel', 'Title', 'Author', 'Excerpt 1...'], ... ]}
    series_data = defaultdict(list)

    print(f"Scanning .html files in '{directory}/'...\n")

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            # --- 1. Extract Base Metadata ---
            reel_no = extract_metadata(soup, 'Reel No')
            title = extract_metadata(soup, 'Title')
            author = extract_metadata(soup, 'Author')

            # Determine Series Letter
            series_match = re.search(r'[A-Za-z]', reel_no)
            series_letter = series_match.group(0).upper() if series_match else 'Unknown'

            row_data = [reel_no, title, author]

            # --- 2. Extract Excerpts ---
            excerpts_span = soup.find('span', id='Excerpts')
            if excerpts_span:
                curr_heading = None
                texts = []
                
                for sib in excerpts_span.parent.find_next_siblings():
                    if sib.name == 'h2':
                        # Save the final heading text before breaking
                        if curr_heading and texts:
                            row_data.append(f"{curr_heading}: {' '.join(texts)}")
                        break
                    
                    # Standard <h3> heading found
                    if sib.name == 'h3':
                        if curr_heading and texts:
                            row_data.append(f"{curr_heading}: {' '.join(texts)}")
                            
                        curr_heading = sib.get_text(strip=True)
                        texts = []
                        
                    elif sib.name == 'p':
                        para_text = sib.get_text(separator=' ').replace('\n', ' ').strip()
                        para_text = re.sub(r'\s+', ' ', para_text)
                        
                        if not para_text:
                            continue
                            
                        # Catch pseudo-headings wrapped in guillemets (e.g., «Beginning of the root text:»)
                        if para_text.startswith('«') and '»' in para_text:
                            if curr_heading and texts:
                                row_data.append(f"{curr_heading}: {' '.join(texts)}")
                                
                            # Clean up the pseudo-heading to act as the new column label
                            curr_heading = para_text.replace('«', '').replace('»', '').strip(' :')
                            texts = []
                        else:
                            # It's standard excerpt text
                            # Fallback if text appears before any heading is declared
                            if not curr_heading:
                                curr_heading = "Excerpt (No Heading)"
                                
                            texts.append(para_text)
                            
                # Catch the very last heading if no <h2> closes the section
                if curr_heading and texts:
                    row_data.append(f"{curr_heading}: {' '.join(texts)}")

            # Append the completed row to the specific series
            series_data[series_letter].append(row_data)

    # --- 3. Write Data to CSV Files ---
    for series, rows in series_data.items():
        csv_filename = f"ngmcp_series_{series}.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write a generic header for the base columns
            writer.writerow(['Reel No', 'Title', 'Author', 'Excerpts ->'])
            
            for row in rows:
                writer.writerow(row)
                
        print(f"Created {csv_filename} with {len(rows)} records.")

if __name__ == '__main__':
    process_manuscripts()
