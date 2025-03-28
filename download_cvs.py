import pandas as pd
import gdown
import os
import re
import time
import random
from urllib.parse import urlparse, parse_qs

# Create cvs directory if it doesn't exist
if not os.path.exists('cvs'):
    os.makedirs('cvs')

# Check if there's an updated Excel file to continue from
if os.path.exists('aplication_updated.xlsx'):
    print("Found existing aplication_updated.xlsx. Continuing from where it stopped...")
    df = pd.read_excel('aplication_updated.xlsx')
    # Ensure required columns exist even in previously saved files
    if 'PDF_Filename' not in df.columns:
        df['PDF_Filename'] = None
    if 'Download_Status' not in df.columns:
        df['Download_Status'] = None
    if 'Error_Message' not in df.columns:
        df['Error_Message'] = None
    if 'Retry_Count' not in df.columns:
        df['Retry_Count'] = 0
else:
    # Start from the original file
    print("Starting new download process...")
    df = pd.read_excel('aplication.xlsx')
    # Add a new column for the saved PDF filenames if it doesn't exist
    if 'PDF_Filename' not in df.columns:
        df['PDF_Filename'] = None
    # Add a column for download status if it doesn't exist
    if 'Download_Status' not in df.columns:
        df['Download_Status'] = None
    # Add a column for error messages if it doesn't exist
    if 'Error_Message' not in df.columns:
        df['Error_Message'] = None
    # Add a column for retry count
    if 'Retry_Count' not in df.columns:
        df['Retry_Count'] = 0

# Define max retries and delay settings
MAX_RETRIES = 2  # Maximum number of retry attempts per file
MIN_DELAY = 8    # Minimum delay between downloads in seconds
MAX_DELAY = 19   # Maximum delay between downloads in seconds

# Count how many are already downloaded
already_downloaded = df['PDF_Filename'].notna().sum()
failed_downloads = (df['Download_Status'] == 'FAILED').sum() if 'Download_Status' in df.columns else 0
to_download = len(df) - already_downloaded - failed_downloads
print(f"Already downloaded: {already_downloaded}")
print(f"Failed downloads: {failed_downloads}")
print(f"Remaining to download: {to_download}")

# Add a daily limit to avoid excessive downloads
daily_limit = 100  # Adjust this based on your needs
today_downloads = 0

# Process each row
processed_count = 0
for index, row in df.iterrows():
    # Check if we've hit the daily download limit
    if today_downloads >= daily_limit:
        print(f"\nReached daily download limit of {daily_limit} files.")
        print("Please run the script again tomorrow to continue downloads.")
        break
    
    # Skip rows that already have PDF filenames (successful downloads)
    if pd.notna(row['PDF_Filename']):
        continue
    
    # Skip rows that are marked as failed downloads and have reached max retries
    if pd.notna(row['Download_Status']) and row['Download_Status'] == 'FAILED' and row['Retry_Count'] >= MAX_RETRIES:
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
            # Get the person's name, convert to string in case it's a number
            person_name = str(row['Nome Completo']) if pd.notna(row['Nome Completo']) else f"unnamed_{index}"
            
            # Create a filename using the sanitized name and index
            sanitized_name = re.sub(r'[^\w\s]', '', person_name).replace(' ', '_').lower()
            pdf_filename = f"{sanitized_name}_{index}.pdf"
            output_path = os.path.join('cvs', pdf_filename)
            
            # Get current retry count or initialize to 0
            retry_count = row['Retry_Count'] if pd.notna(row['Retry_Count']) else 0
            
            # Add a random delay between downloads to avoid rate limiting
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"Waiting {delay:.1f} seconds before next download...")
            time.sleep(delay)
            
            try:
                # Download the file
                download_url = f'https://drive.google.com/uc?id={file_id}'
                processed_count += 1
                print(f"Downloading CV for {person_name} ({processed_count}/{to_download}) - Attempt {retry_count + 1}/{MAX_RETRIES + 1}...")
                success = gdown.download(download_url, output_path, quiet=False)
                
                if success:
                    # Update the dataframe with the filename
                    df.at[index, 'PDF_Filename'] = pdf_filename
                    df.at[index, 'Download_Status'] = 'SUCCESS'
                    df.at[index, 'Error_Message'] = None
                    print(f"Successfully downloaded: {pdf_filename}")
                    today_downloads += 1
                else:
                    # Increment retry count
                    retry_count += 1
                    df.at[index, 'Retry_Count'] = retry_count
                    
                    if retry_count > MAX_RETRIES:
                        # Mark as failed download if max retries reached
                        df.at[index, 'Download_Status'] = 'FAILED'
                        df.at[index, 'PDF_Filename'] = None
                        df.at[index, 'Error_Message'] = "Download failed after multiple attempts - file might be inaccessible or requires permission"
                        print(f"Failed to download file for {person_name} after {MAX_RETRIES + 1} attempts")
                    else:
                        df.at[index, 'Download_Status'] = 'RETRY'
                        print(f"Failed attempt {retry_count}/{MAX_RETRIES + 1} for {person_name} - will retry later")
                
                # Save the Excel file after each download attempt
                df.to_excel('aplication_updated.xlsx', index=False)
                print("Progress saved to aplication_updated.xlsx")
                
            except Exception as e:
                error_message = str(e)
                print(f"Error downloading file for {person_name}: {error_message}")
                
                # Increment retry count
                retry_count += 1
                df.at[index, 'Retry_Count'] = retry_count
                
                if retry_count > MAX_RETRIES or "Cannot retrieve the public link" in error_message:
                    # Mark as failed download if max retries reached or specific error
                    df.at[index, 'Download_Status'] = 'FAILED'
                    df.at[index, 'PDF_Filename'] = None
                    df.at[index, 'Error_Message'] = error_message
                    print(f"Failed to download file for {person_name} after {retry_count} attempts")
                else:
                    df.at[index, 'Download_Status'] = 'RETRY'
                    df.at[index, 'Error_Message'] = error_message
                    print(f"Failed attempt {retry_count}/{MAX_RETRIES + 1} for {person_name} - will retry later")
                
                # Save the Excel file after each error
                df.to_excel('aplication_updated.xlsx', index=False)
                print("Progress saved to aplication_updated.xlsx")

# Make sure the final updated Excel file is saved
df.to_excel('aplication_updated.xlsx', index=False)

# Print summary statistics
successful_downloads = df['PDF_Filename'].notna().sum()
failed_downloads = (df['Download_Status'] == 'FAILED').sum() if 'Download_Status' in df.columns else 0
retry_downloads = (df['Download_Status'] == 'RETRY').sum() if 'Download_Status' in df.columns else 0

print("\nDownload process completed.")
print(f"Total CVs successfully downloaded: {successful_downloads}")
print(f"Total CVs failed to download: {failed_downloads}")
print(f"Total CVs pending retry: {retry_downloads}")
print(f"Total downloads today: {today_downloads}")

if retry_downloads > 0:
    print("\nThere are files pending retry. Run the script again tomorrow to attempt downloading these files.")

print("Updated Excel file saved as 'aplication_updated.xlsx'") 