import pandas as pd
import gdown
import os
import re
from urllib.parse import urlparse, parse_qs

# Create cvs directory if it doesn't exist
if not os.path.exists('cvs'):
    os.makedirs('cvs')

# Check if there's an updated Excel file to continue from
if os.path.exists('aplication_updated.xlsx'):
    print("Found existing aplication_updated.xlsx. Continuing from where it stopped...")
    df = pd.read_excel('aplication_updated.xlsx')
else:
    # Start from the original file
    print("Starting new download process...")
    df = pd.read_excel('aplication.xlsx')
    # Add a new column for the saved PDF filenames if it doesn't exist
    if 'PDF_Filename' not in df.columns:
        df['PDF_Filename'] = None

# Count how many are already downloaded
already_downloaded = df['PDF_Filename'].notna().sum()
to_download = len(df) - already_downloaded
print(f"Already downloaded: {already_downloaded}")
print(f"Remaining to download: {to_download}")

# Process each row
processed_count = 0
for index, row in df.iterrows():
    # Skip rows that already have PDF filenames
    if pd.notna(row['PDF_Filename']):
        continue
    
    # Skip rows with missing curriculum links
    if pd.isna(row['Adicione seu Currículo']):
        continue
    
    # Get the URL from the cell
    url = row['Adicione seu Currículo']
    
    # Extract the file_id from the Google Drive URL
    if 'drive.google.com' in url:
        # Parse the URL to extract the file ID
        if 'open?id=' in url:
            # For URLs like https://drive.google.com/open?id=FILE_ID
            parsed_url = urlparse(url)
            file_id = parse_qs(parsed_url.query).get('id', [None])[0]
        elif '/file/d/' in url:
            # For URLs like https://drive.google.com/file/d/FILE_ID/view
            match = re.search(r'/file/d/([^/]+)', url)
            file_id = match.group(1) if match else None
        else:
            file_id = None
        
        if file_id:
            # Create a filename using the person's name (sanitized) and index
            person_name = row['Nome Completo']
            sanitized_name = re.sub(r'[^\w\s]', '', person_name).replace(' ', '_').lower()
            pdf_filename = f"{sanitized_name}_{index}.pdf"
            output_path = os.path.join('cvs', pdf_filename)
            
            try:
                # Download the file
                download_url = f'https://drive.google.com/uc?id={file_id}'
                processed_count += 1
                print(f"Downloading CV for {person_name} ({processed_count}/{to_download})...")
                gdown.download(download_url, output_path, quiet=False)
                
                # Update the dataframe with the filename
                df.at[index, 'PDF_Filename'] = pdf_filename
                
                print(f"Successfully downloaded: {pdf_filename}")
                
                # Save the Excel file after each successful download
                df.to_excel('aplication_updated.xlsx', index=False)
                print("Progress saved to aplication_updated.xlsx")
                
            except Exception as e:
                print(f"Error downloading file for {person_name}: {e}")

# Make sure the final updated Excel file is saved
df.to_excel('aplication_updated.xlsx', index=False)

print("\nAll downloads completed.")
print(f"Total CVs processed: {df['PDF_Filename'].notna().sum()}")
print("Updated Excel file saved as 'aplication_updated.xlsx'") 