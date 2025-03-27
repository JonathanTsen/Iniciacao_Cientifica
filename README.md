# Gemini Resume Screening Agent Chain

This application uses Google's Gemini 2.0 Flash to automate the screening of resumes based on specific criteria. It reads an Excel file containing candidate information, analyzes their resumes, and updates the "Primeira Fase" column with "Sim" or "Não" based on the following criteria:

1. The candidate must be studying at a Federal or State university (not a private university)
2. The candidate must have done scientific research (iniciação científica) OR works at a recognized company

## Project Structure

```
├── agents/
│   ├── __init__.py         # Package initialization
│   ├── sheet_agent.py      # Agent for reading/writing Excel files
│   ├── extraction_agent.py # Agent for extracting text from resumes
│   └── analysis_agent.py   # Agent for analyzing resumes against criteria
├── agent_chain.py          # Orchestrates the agent chain
├── config.py               # Configuration settings
├── utils.py                # Utility functions
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (API keys)
└── README.md               # Documentation
```

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit the `.env` file in the root directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   
   To get a Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com)
   - Sign in with your Google account
   - Create an API key

## Setting up Google Drive API Credentials

To properly download resumes from Google Drive, you need to set up Google Drive API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the Google Drive API for your project
4. Go to "Credentials" and create an OAuth client ID
   - Application type: Desktop application
   - Name: Resume Extractor (or any name you prefer)
5. Download the credentials JSON file
6. Save it as `credentials.json` in the root directory of this project

When you run the application for the first time, a browser window will open asking you to authorize the application to access your Google Drive. After authorization, a token will be saved locally so you won't need to authorize again unless the token expires or is deleted.

## Usage

1. Prepare your Excel file with the following columns:
   - Carimbo de data/hora
   - Adicione seu Currículo (contains Google Drive links to resumes)
   - Nome Completo
   - Email
   - Telefone
   - Link do LinkedIn
   - Primeira Fase (this column will be updated by the application)

2. Run the application:
   ```
   python main.py
   ```

3. When prompted, enter the path to your Excel file.

4. The application will process each candidate and update the "Primeira Fase" column with:
   - "Sim" if the candidate meets both criteria
   - "Não" if the candidate fails to meet at least one criterion
   - "Erro" if there was an error processing the resume

## How It Works

The application uses a chain of agents:

1. **SheetAgent**: Reads and writes to the Excel file
2. **TextExtractionAgent**: Extracts text from the resume links (Google Drive)
3. **CriteriaAnalysisAgent**: Analyzes the resume text using Gemini 2.0 Flash to check if criteria are met
4. **AgentChain**: Orchestrates the entire process

## Customization

You can modify the screening criteria and other settings in the `config.py` file:

- `GEMINI_MODEL`: The Gemini model to use (default: 'gemini-1.5-flash')
- `CRITERIA`: Keywords for university types, research experience, etc.
- `API_RATE_LIMIT_DELAY`: Delay between API calls to avoid rate limiting

## Limitations

- The application can only process Google Drive links to resumes
- PDF files are directly processed, other formats may have limited support
- Gemini API has rate limits, so processing may take time for many candidates
- Resume analysis depends on the quality of Gemini's understanding of the text

## Troubleshooting

- If you encounter connection errors, check your internet connection
- If Gemini API errors occur, verify your API key in the `.env` file
- If resume extraction fails, check if the Google Drive link is publicly accessible 