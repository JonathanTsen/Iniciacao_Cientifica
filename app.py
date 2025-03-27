import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import re
import time

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class SheetAgent:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path)
    
    def get_candidates(self):
        return self.df

    def save_results(self):
        self.df.to_excel(self.excel_path, index=False)
        print(f"Results saved to {self.excel_path}")

class TextExtractionAgent:
    def extract_text_from_gdrive(self, link):
        """Extract text from Google Drive link using Gemini API"""
        try:
            # Extract file ID from Google Drive link
            file_id = re.search(r'id=([^&]+)', link)
            if file_id:
                file_id = file_id.group(1)
            else:
                # Alternative pattern for different link formats
                file_id = re.search(r'drive\.google\.com/file/d/([^/]+)', link)
                if file_id:
                    file_id = file_id.group(1)
                else:
                    return "Error: Could not extract file ID from link"
            
            # Create a direct download link
            download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # Download the file
            response = requests.get(download_link)
            if response.status_code != 200:
                return f"Error: Failed to download file, status code: {response.status_code}"
            
            # Try to determine file type and extract text
            if "application/pdf" in response.headers.get('Content-Type', ''):
                # PDF file
                pdf_file = BytesIO(response.content)
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            else:
                # Try using Gemini for document understanding
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Since Gemini doesn't directly handle files, we might need to send content
                # For this simplified example, we'll prompt it to extract text
                prompt = f"Please extract all text from this document. The document is a resume/CV."
                
                # For simplicity in this example, use Gemini to analyze the first part of the response
                # In a real implementation, you'd handle different document types properly
                sample_content = response.content[:10000].decode('utf-8', errors='ignore')
                response = model.generate_content(prompt + "\n\nDocument content: " + sample_content)
                
                return response.text
                
        except Exception as e:
            return f"Error extracting text: {str(e)}"

class CriteriaAnalysisAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_resume(self, resume_text):
        """Analyze resume text using Gemini to check if criteria are met"""
        prompt = """
        Analyze the following resume and determine if the candidate meets BOTH of these criteria:
        1. The candidate must be studying at a Federal or State university (not a private university)
        2. The candidate must have done scientific research (iniciação científica) OR works at a recognized company
        
        Answer only with 'Sim' if BOTH criteria are met, or 'Não' if at least one criterion is not met.
        
        Resume text:
        """
        
        try:
            response = self.model.generate_content(prompt + resume_text)
            result = response.text.strip()
            
            # Clean the response to get only Sim or Não
            if "sim" in result.lower():
                return "Sim"
            else:
                return "Não"
        except Exception as e:
            print(f"Error analyzing resume: {str(e)}")
            return "Não"  # Default to No in case of errors

class AgentChain:
    def __init__(self, excel_path):
        self.sheet_agent = SheetAgent(excel_path)
        self.extraction_agent = TextExtractionAgent()
        self.analysis_agent = CriteriaAnalysisAgent()
    
    def run(self):
        """Run the complete agent chain"""
        print("Starting agent chain...")
        
        # Get candidates from sheet
        df = self.sheet_agent.get_candidates()
        
        # Process each candidate
        for index, row in df.iterrows():
            try:
                # Skip if already processed
                if pd.notna(row['Primeira Fase']):
                    print(f"Skipping {row['Nome Completo']} - already processed")
                    continue
                
                print(f"Processing candidate: {row['Nome Completo']}")
                
                # Extract text from resume
                resume_link = row['Adicione seu Currículo']
                resume_text = self.extraction_agent.extract_text_from_gdrive(resume_link)
                
                if resume_text.startswith("Error"):
                    print(f"Error extracting resume: {resume_text}")
                    df.at[index, 'Primeira Fase'] = "Erro"
                    continue
                
                # Analyze resume against criteria
                result = self.analysis_agent.analyze_resume(resume_text)
                
                # Update sheet with result
                df.at[index, 'Primeira Fase'] = result
                print(f"Result for {row['Nome Completo']}: {result}")
                
                # Save progress after each candidate
                self.sheet_agent.df = df
                self.sheet_agent.save_results()
                
                # Rate limiting to avoid API throttling
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing candidate {row['Nome Completo']}: {str(e)}")
                df.at[index, 'Primeira Fase'] = "Erro"
        
        print("Agent chain completed!")

if __name__ == "__main__":
    # Check if API key is configured
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in .env file")
        print("Please create a .env file with your Gemini API key as GEMINI_API_KEY=your_key_here")
        exit(1)
    
    # Get Excel file path from user
    excel_path = input("Enter path to Excel file: ")
    
    # Run agent chain
    agent_chain = AgentChain(excel_path)
    agent_chain.run() 