"""
Configuration settings for the resume screening application
"""

# Gemini model settings
GEMINI_MODEL = 'gemini-2.0-flash'  # Use 'gemini-1.5-pro' for more accuracy if available

# Resume screening criteria
CRITERIA = {
    "university_type": ["federal", "estadual", "state", "fed"],
    "excluded_university_type": ["particular", "private", "privada"],
    "research_keywords": ["iniciação científica", "scientific initiation", "research", "pesquisa científica"],
    "company_quality_threshold": 0.7  # Confidence threshold for recognizing a "good" company
}

# File handling settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_FILE_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# API settings
API_RATE_LIMIT_DELAY = 0.1  # Seconds to wait between API calls
MAX_RETRIES = 3  # Maximum number of retries for API calls

# Excel column names
COLUMN_NAMES = {
    "timestamp": "Carimbo de data/hora",
    "resume_link": "Adicione seu Currículo",
    "name": "Nome Completo",
    "email": "Email",
    "phone": "Telefone",
    "linkedin": "Link do LinkedIn", 
    "result": "Primeira Fase"
} 