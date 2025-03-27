import requests
from PyPDF2 import PdfReader
from io import BytesIO
import re
import google.generativeai as genai
from config import GEMINI_MODEL, MAX_FILE_SIZE, ALLOWED_FILE_TYPES
from utils import rate_limited_request, download_file, download_file_from_drive

class TextExtractionAgent:
    """Agent responsible for extracting text from Google Drive resume links"""
    
    def __init__(self):
        """Initialize the text extraction agent"""
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def extract_text_from_gdrive(self, link):
        """Extract text from Google Drive link"""
        try:
            # Extract file ID from Google Drive link
            file_id = self._extract_file_id(link)
            if not file_id:
                return "Error: Could not extract file ID from link"
            
            # Try using the direct download link method first
            try:
                # Create a direct download link with confirm=t parameter to bypass the consent screen
                download_link = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
                
                # Download the file with rate limiting
                response = rate_limited_request(download_file, download_link)
                
                # Check content type and look for Google's HTML consent page
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    # If we get HTML, it means we need to use the Google Drive API instead
                    raise Exception("Received HTML instead of file content, falling back to API method")
                
                # Check file size
                content_length = int(response.headers.get('Content-Length', 0))
                if content_length > MAX_FILE_SIZE:
                    return f"Error: File too large ({content_length} bytes)"
                
                # Process the file based on content type
                if content_type not in ALLOWED_FILE_TYPES and not "application/pdf" in content_type:
                    return f"Error: Unsupported file type: {content_type}"
                    
                return self._process_file_content(response)
                
            except Exception as e:
                print(f"Direct download failed: {str(e)}. Trying Google Drive API method...")
                
                # Fall back to using the Google Drive API
                file_data = rate_limited_request(download_file_from_drive, file_id)
                
                # Check file type
                content_type = file_data['mime_type']
                if content_type not in ALLOWED_FILE_TYPES and not "application/pdf" in content_type:
                    return f"Error: Unsupported file type: {content_type}"
                
                # Process the content
                if "application/pdf" in content_type:
                    return self._extract_pdf_text(file_data['content'].read())
                else:
                    # For other file types, use Gemini to extract text
                    return self._extract_text_with_gemini(file_data['content'].read())
                
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def _extract_file_id(self, link):
        """Extract Google Drive file ID from various link formats"""
        # Format: ?id=FILE_ID
        file_id = re.search(r'id=([^&]+)', link)
        if file_id:
            return file_id.group(1)
        
        # Format: /file/d/FILE_ID/
        file_id = re.search(r'drive\.google\.com/file/d/([^/]+)', link)
        if file_id:
            return file_id.group(1)
        
        # Format: /open?id=FILE_ID
        file_id = re.search(r'open\?id=([^&]+)', link)
        if file_id:
            return file_id.group(1)
            
        return None
    
    def _process_file_content(self, response):
        """Process file content based on type"""
        # Check if it's a PDF
        content_type = response.headers.get('Content-Type', '')
        if "application/pdf" in content_type:
            return self._extract_pdf_text(response.content)
        elif "text/html" in content_type:
            # If we still got HTML at this point, it's an error
            return f"Error: Unsupported file type: {content_type}"
        else:
            # For other file types, use Gemini to extract text
            return self._extract_text_with_gemini(response.content)
    
    def _extract_pdf_text(self, content):
        """Extract text from PDF content"""
        pdf_file = BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def _extract_text_with_gemini(self, content):
        """Use Gemini to extract text from non-PDF content"""
        # For simplicity, decode a part of the content
        sample_content = content[:10000].decode('utf-8', errors='ignore')
        
        # Create prompt for Gemini
        prompt = "Please extract all text from this document. The document is a resume/CV."
        
        # Generate text extraction using rate limiting
        response = rate_limited_request(
            self.model.generate_content,
            prompt + "\n\nDocument content: " + sample_content
        )
        
        return response.text 