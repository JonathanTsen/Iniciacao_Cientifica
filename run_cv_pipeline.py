import os
import sys
import subprocess

def print_separator():
    print("\n" + "="*50 + "\n")

def main():
    print("CV Processing Pipeline")
    print_separator()
    
    # Step 1: Download CVs
    print("Step 1: Downloading CVs from Google Drive links in Excel file")
    print("Running download_cvs.py...")
    
    try:
        result = subprocess.run(["python", "download_cvs.py"], check=True)
        if result.returncode != 0:
            print("Error: download_cvs.py failed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error running download_cvs.py: {e}")
        sys.exit(1)
    
    print_separator()
    
    # Step 2: Process CVs
    print("Step 2: Processing downloaded CVs using the agent")
    print("Running process_cvs.py...")
    
    try:
        result = subprocess.run(["python", "process_cvs.py"], check=True)
        if result.returncode != 0:
            print("Error: process_cvs.py failed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error running process_cvs.py: {e}")
        sys.exit(1)
    
    print_separator()
    print("CV Processing Pipeline completed successfully!")
    print("Results saved in 'aplication_processed.xlsx'")

if __name__ == "__main__":
    main() 