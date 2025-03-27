import pandas as pd
from config import COLUMN_NAMES

class SheetAgent:
    """Agent responsible for reading and writing to Excel sheets"""
    
    def __init__(self, excel_path):
        """Initialize the sheet agent with the Excel file path"""
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path)
        self._validate_columns()
    
    def _validate_columns(self):
        """Validate that the Excel file has the required columns"""
        required_columns = [
            COLUMN_NAMES["timestamp"], 
            COLUMN_NAMES["resume_link"], 
            COLUMN_NAMES["name"],
            COLUMN_NAMES["result"]
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Excel file is missing required columns: {', '.join(missing_columns)}")
    
    def get_candidates(self):
        """Returns the dataframe with all candidates"""
        return self.df

    def save_results(self):
        """Saves the updated dataframe back to Excel"""
        self.df.to_excel(self.excel_path, index=False)
        print(f"Results saved to {self.excel_path}")
        
    def update_candidate_status(self, index, status):
        """Updates a specific candidate's status in the 'Primeira Fase' column"""
        self.df.at[index, COLUMN_NAMES["result"]] = status
        
    def get_unprocessed_candidates(self):
        """Returns only the candidates that haven't been processed yet"""
        return self.df[self.df[COLUMN_NAMES["result"]].isna()]
    
    def get_summary(self):
        """Returns a summary of the processing results"""
        total = len(self.df)
        processed = sum(~self.df[COLUMN_NAMES["result"]].isna())
        approved = sum(self.df[COLUMN_NAMES["result"]] == "Sim")
        rejected = sum(self.df[COLUMN_NAMES["result"]] == "Não")
        errors = sum(self.df[COLUMN_NAMES["result"]] == "Erro")
        
        return {
            "total": total,
            "processed": processed,
            "approved": approved,
            "rejected": rejected,
            "errors": errors,
            "remaining": total - processed
        } 