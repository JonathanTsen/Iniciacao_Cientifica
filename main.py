import os
import google.generativeai as genai
from dotenv import load_dotenv
from agent_chain import AgentChain

def main():
    """Main entry point for the resume screening application"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Validate API key
    if not api_key or api_key == "your_api_key_here":
        print("Error: Valid GEMINI_API_KEY not found in .env file")
        print("Please edit the .env file and add your Gemini API key as GEMINI_API_KEY=your_key_here")
        return
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Welcome message
    print("=" * 50)
    print("Resume Screening Application using Gemini 2.0 Flash")
    print("=" * 50)
    print("This application will:")
    print("1. Read candidate information from an Excel file")
    print("2. Read CVs from the local 'cvs' folder")
    print("3. Analyze if candidates meet the specified criteria")
    print("4. Update the 'Primeira Fase' column with results\n")
    
    # Use a relative path for the Excel file in the same directory
    excel_path = "aplication.xlsx"
    
    # Check if the file exists
    if not os.path.exists(excel_path) or not excel_path.endswith(('.xlsx', '.xls')):
        print(f"Error: File '{excel_path}' does not exist or is not an Excel file.")
        return
    
    # Check if the cvs folder exists
    if not os.path.exists("cvs") or not os.path.isdir("cvs"):
        print("Error: 'cvs' folder does not exist. Please create a folder named 'cvs' and place all CVs there.")
        return
    
    # Create and run the agent chain
    try:
        agent_chain = AgentChain(excel_path)
        agent_chain.run()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user! Saving progress...")
        # Try to save progress if the agent_chain was created
        if 'agent_chain' in locals():
            agent_chain.sheet_agent.save_results()
        print("Progress saved. You can restart the application to continue from where you left off.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Try to save progress if the agent_chain was created
        if 'agent_chain' in locals():
            print("Attempting to save progress...")
            try:
                agent_chain.sheet_agent.save_results()
                print("Progress saved successfully.")
            except Exception as save_error:
                print(f"Error saving progress: {str(save_error)}")
        
    print("\nThank you for using the Resume Screening Application!")

if __name__ == "__main__":
    main() 