import pandas as pd
import os
import sys
from agent_chain import AgentPDFProcessor

def main():
    # Check if the updated Excel file exists
    if not os.path.exists('aplication_updated.xlsx'):
        print("Error: aplication_updated.xlsx not found.")
        print("Please run download_cvs.py first to download PDFs and create the updated Excel file.")
        sys.exit(1)
    
    # Check if the cvs directory exists
    if not os.path.exists('cvs'):
        print("Error: cvs directory not found.")
        print("Please run download_cvs.py first to download PDFs.")
        sys.exit(1)
    
    # Check if there's an already processed file to continue from
    if os.path.exists('aplication_processed.xlsx'):
        print("Found existing aplication_processed.xlsx. Continuing from where it stopped...")
        df = pd.read_excel('aplication_processed.xlsx')
    else:
        # Start from the updated file (after downloads)
        print("Starting new processing...")
        df = pd.read_excel('aplication_updated.xlsx')
        # Create a new column for processed results if it doesn't exist
        if 'Processed_Result' not in df.columns:
            df['Processed_Result'] = None
    
    # Count valid PDF filenames - only those that were successfully downloaded
    valid_pdfs = df['PDF_Filename'].notna().sum()
    if valid_pdfs == 0:
        print("No PDF files were downloaded successfully. Please run download_cvs.py first.")
        sys.exit(1)
    
    # Count failed downloads
    failed_downloads = (df['Download_Status'] == 'FAILED').sum() if 'Download_Status' in df.columns else 0
    
    # Count already processed PDFs
    already_processed = df['Processed_Result'].notna().sum()
    remaining_to_process = valid_pdfs - already_processed
    
    print(f"Found {valid_pdfs} PDFs to process.")
    print(f"Failed downloads: {failed_downloads}")
    print(f"Already processed: {already_processed}")
    print(f"Remaining to process: {remaining_to_process}")
    
    # Initialize the agent for PDF processing
    agent = AgentPDFProcessor()
    
    # Process each PDF
    processed_count = 0
    for index, row in df.iterrows():
        # Skip rows without PDF filenames - either not downloaded or failed downloads
        if pd.isna(row['PDF_Filename']):
            continue
        
        # Skip rows that have already been processed
        if pd.notna(row['Processed_Result']):
            continue
        
        pdf_path = os.path.join('cvs', row['PDF_Filename'])
        person_name = row['Nome Completo']
        
        # Check if the PDF exists
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found for {person_name}: {pdf_path}")
            df.at[index, 'Processed_Result'] = "ERROR: PDF file not found"
            df.to_excel('aplication_processed.xlsx', index=False)
            continue
        
        try:
            processed_count += 1
            print(f"Processing CV for {person_name} ({processed_count}/{remaining_to_process})...")
            
            # Process the PDF using the agent
            result = agent.process_pdf(pdf_path, person_name=person_name, email=row['Email'])
            
            # Store the result in the dataframe
            df.at[index, 'Processed_Result'] = str(result)
            
            print(f"Successfully processed: {row['PDF_Filename']}")
            
            # Save progress after each processed PDF
            df.to_excel('aplication_processed.xlsx', index=False)
            print("Progress saved to aplication_processed.xlsx")
            
        except Exception as e:
            error_msg = f"Error processing PDF for {person_name}: {e}"
            print(error_msg)
            # Record the error in the dataframe
            df.at[index, 'Processed_Result'] = f"ERROR: {str(e)}"
            # Still save progress after errors
            df.to_excel('aplication_processed.xlsx', index=False)
    
    # Make sure the final updated Excel file is saved
    df.to_excel('aplication_processed.xlsx', index=False)
    
    # Calculate final statistics
    successful_processing = df['Processed_Result'].notna().sum() - df['Processed_Result'].str.startswith('ERROR:').sum() if 'Processed_Result' in df.columns else 0
    error_processing = df['Processed_Result'].str.startswith('ERROR:').sum() if 'Processed_Result' in df.columns else 0
    
    print("\nAll PDFs processed.")
    print(f"Total CVs successfully processed: {successful_processing}")
    print(f"Total CVs with processing errors: {error_processing}")
    print(f"Total CVs that failed to download: {failed_downloads}")
    print("Updated Excel file saved as 'aplication_processed.xlsx'")

if __name__ == "__main__":
    main() 