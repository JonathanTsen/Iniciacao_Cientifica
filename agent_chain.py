import time
import pandas as pd
import os
from agents import SheetAgent, TextExtractionAgent, CriteriaAnalysisAgent
from config import API_RATE_LIMIT_DELAY, COLUMN_NAMES

class AgentChain:
    """
    Main class that orchestrates the resume screening process by coordinating the agents
    """
    
    def __init__(self, excel_path):
        """Initialize the agent chain with the path to the Excel file"""
        self.sheet_agent = SheetAgent(excel_path)
        self.extraction_agent = TextExtractionAgent()
        self.analysis_agent = CriteriaAnalysisAgent()
        self.checkpoint_interval = 5  # Save every 5 candidates
        self.cv_folder = "cvs"  # Folder containing CV files
    
    def run(self):
        """Run the complete agent chain to process all candidates"""
        print("Starting resume screening process...")
        
        # Get candidates from sheet
        df = self.sheet_agent.get_candidates()
        
        # Get initial stats
        summary = self.sheet_agent.get_summary()
        print(f"Found {summary['total']} candidates total")
        print(f"Already processed: {summary['processed']} candidates")
        print(f"Remaining to process: {summary['remaining']} candidates")
        
        # Get list of CV files from the folder
        cv_files = [f for f in os.listdir(self.cv_folder) if os.path.isfile(os.path.join(self.cv_folder, f))]
        print(f"Found {len(cv_files)} CV files in '{self.cv_folder}' folder")
        
        # Create checkpoint counter
        candidates_since_save = 0
        
        # Process each candidate
        for index, row in df.iterrows():
            try:
                # Skip if already processed
                if pd.notna(row[COLUMN_NAMES["result"]]):
                    continue
                
                # Update progress
                current = index + 1
                print(f"\nProcessing candidate {current}/{summary['total']}: {row[COLUMN_NAMES['name']]}")
                
                # Find the matching CV file for this candidate
                candidate_name = row[COLUMN_NAMES['name']].strip().lower()
                matching_file = None
                
                for file in cv_files:
                    # Check if filename contains candidate name or vice versa
                    if candidate_name in file.lower() or any(name_part in file.lower() 
                                                      for name_part in candidate_name.split() if len(name_part) > 3):
                        matching_file = file
                        break
                
                if not matching_file:
                    print(f"Error: No matching CV file found for {row[COLUMN_NAMES['name']]}")
                    self.sheet_agent.update_candidate_status(index, "Erro")
                    # Increment the candidates processed counter
                    candidates_since_save += 1
                    # Save immediately after errors
                    self.sheet_agent.save_results()
                    candidates_since_save = 0
                    continue
                
                # Extract text from CV file
                cv_path = os.path.join(self.cv_folder, matching_file)
                print(f"Extracting resume from: {cv_path}")
                resume_text = self.extraction_agent.extract_text_from_local_file(cv_path)
                
                if resume_text.startswith("Error"):
                    print(f"Error extracting resume: {resume_text}")
                    self.sheet_agent.update_candidate_status(index, "Erro")
                    # Increment the candidates processed counter
                    candidates_since_save += 1
                    # Save immediately after errors
                    self.sheet_agent.save_results()
                    candidates_since_save = 0
                    continue
                
                # Analyze resume against criteria
                print("Analyzing resume against criteria...")
                result = self.analysis_agent.analyze_resume(resume_text)
                
                # Update sheet with result
                self.sheet_agent.update_candidate_status(index, result)
                print(f"Result for {row[COLUMN_NAMES['name']]}: {result}")
                
                # Increment the candidates processed counter
                candidates_since_save += 1
                
                # Save progress periodically or after each candidate based on checkpoint_interval
                if candidates_since_save >= self.checkpoint_interval:
                    print(f"Saving progress after processing {candidates_since_save} candidates...")
                    self.sheet_agent.save_results()
                    candidates_since_save = 0
                
                # Rate limiting to avoid API throttling
                time.sleep(API_RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"Error processing candidate {row[COLUMN_NAMES['name']]}: {str(e)}")
                self.sheet_agent.update_candidate_status(index, "Erro")
                # Save immediately after errors
                self.sheet_agent.save_results()
                candidates_since_save = 0
        
        # Save final results if any unsaved changes
        if candidates_since_save > 0:
            print(f"Saving final progress...")
            self.sheet_agent.save_results()
        
        # Get final stats
        final_summary = self.sheet_agent.get_summary()
        
        # Print summary
        print("\n===== Resume Screening Complete =====")
        print(f"Total candidates: {final_summary['total']}")
        print(f"Processed: {final_summary['processed']}")
        print(f"Approved ('Sim'): {final_summary['approved']}")
        print(f"Rejected ('Não'): {final_summary['rejected']}")
        print(f"Errors: {final_summary['errors']}")
        print("=====================================")
        
        return final_summary 

class AgentPDFProcessor:
    """
    Class to process PDF files using the extraction and analysis agents
    """
    
    def __init__(self):
        """Initialize the PDF processor with the necessary agents"""
        self.extraction_agent = TextExtractionAgent()
        self.analysis_agent = CriteriaAnalysisAgent()
    
    def process_pdf(self, pdf_path, person_name=None, email=None):
        """
        Process a PDF file and extract/analyze its content
        
        Args:
            pdf_path (str): Path to the PDF file
            person_name (str, optional): Name of the person associated with the PDF
            email (str, optional): Email of the person associated with the PDF
            
        Returns:
            str: Analysis result or error message
        """
        try:
            # Extract text from PDF file
            if person_name:
                print(f"Extracting resume for {person_name} from: {pdf_path}")
            else:
                print(f"Extracting resume from: {pdf_path}")
                
            resume_text = self.extraction_agent.extract_text_from_local_file(pdf_path)
            
            if resume_text.startswith("Error"):
                print(f"Error extracting resume: {resume_text}")
                return f"Error: {resume_text}"
            
            # Analyze resume against criteria
            print("Analyzing resume against criteria...")
            result = self.analysis_agent.analyze_resume(resume_text)
            
            # Return the result
            return result
            
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            print(error_msg)
            return error_msg 