"""
Utility functions for the resume screening application
"""

import os
import re
import time
import requests
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import API_RATE_LIMIT_DELAY, MAX_RETRIES

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """
    Get an authorized Google Drive API service instance
    """
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        raise Exception(
            "credentials.json not found. Please follow the instructions in README.md to set up Google Drive API credentials. "
            "You can use credentials.json.example as a template."
        )
        
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(
            json.loads(open('token.json').read()), SCOPES)
    
    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Return an authorized Drive API service
    return build('drive', 'v3', credentials=creds)

def download_file_from_drive(file_id):
    """
    Download a file from Google Drive using the API
    """
    try:
        # Get Drive API service
        service = get_drive_service()
        
        # Get file metadata to determine file type
        file_metadata = service.files().get(fileId=file_id, fields='name,mimeType').execute()
        
        # Download file content
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Reset stream position to beginning
        file_content.seek(0)
        
        return {
            'content': file_content,
            'mime_type': file_metadata.get('mimeType', ''),
            'name': file_metadata.get('name', '')
        }
    except Exception as e:
        raise Exception(f"Failed to download file from Google Drive: {str(e)}")

def rate_limited_request(func, *args, **kwargs):
    """
    Wrapper for rate-limited API requests with retries
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = func(*args, **kwargs)
            time.sleep(API_RATE_LIMIT_DELAY)  # Rate limiting
            return result
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff
                wait_time = (2 ** attempt) + 1
                print(f"Request failed: {str(e)}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
                raise

def is_valid_file_path(path):
    """
    Check if a file path is valid and exists
    """
    return os.path.exists(path) and os.path.isfile(path)

def is_valid_excel_file(path):
    """
    Check if a file is a valid Excel file
    """
    return path.endswith(('.xlsx', '.xls'))

def download_file(url, timeout=30):
    """
    Download a file from a URL with timeout and error handling
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise error for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download file: {str(e)}")

def extract_file_extension(content_type):
    """
    Extract file extension from content type
    """
    extensions = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt"
    }
    return extensions.get(content_type, "unknown")

def sanitize_filename(filename):
    """
    Sanitize a filename to remove unsafe characters
    """
    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Limit length
    return filename[:100] 