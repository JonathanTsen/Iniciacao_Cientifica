import time
import pandas as pd
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
                
                # Extract text from resume
                resume_link = row[COLUMN_NAMES["resume_link"]]
                print(f"Extracting resume from: {resume_link}")
                resume_text = self.extraction_agent.extract_text_from_gdrive(resume_link)
                
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