"""
Configuration settings for the resume screening application
"""

# Gemini model settings
GEMINI_MODEL = 'gemini-2.0-flash'  # Use 'gemini-1.5-pro' for more accuracy if available

# Resume screening criteria
CRITERIA = {
    "university_type": ["federal", "estadual", "state", "fed", "UFMG", "USP", "UNICAMP", "UNESP", "UFRJ", "UNB", "UFPR", "UFSC", "UFRGS", "UFC"],
    "excluded_university_type": ["particular", "private", "privada", "faculdade", "centro universitário", "universidade particular", "PUC", "UNINOVE", "UNIP", "ANHANGUERA", "ESTÁCIO", "MACKENZIE", "IBMEC", "FAAP", "FIAP", "FATEC", "SENAC", "SENAI", "UNIESQUINA", "ANHEMBI", "LAUREATE", "PITÁGORAS", "UNIVERITAS", "UNIBAN", "UNIVERSO", "UNESA", "UNISUL", "UNIFACS", "UNINASSAU", "MAURÍCIO DE NASSAU", "SÃO JUDAS", "UNICESUMAR", "NEWTON PAIVA", "UNIVERSO", "UNIASSELVI"],
    "research_keywords": ["iniciação científica", "scientific initiation", "research", "pesquisa científica", "PIBIC", "bolsista de iniciação", "projeto de pesquisa"],
    "company_quality_threshold": 0.7,  # Confidence threshold for recognizing a "good" company
    "education_status": ["cursando", "em andamento", "em curso", "atual", "previsão de conclusão", "graduando", "estudante atual", "estudante de graduação", "bacharelado em andamento", "bacharel em andamento", "sem concluir", "não-concluído", "período atual", "semestre atual"],
    "graduation_keywords": ["graduado", "graduado em", "bacharel em", "formado em", "concluído em", "diploma de", "bacharel de", "formação acadêmica", "conclusion", "completed", "concluído", "ensino superior completo", "graduação completa", "graduated"],
    "top_companies": [
        # Tech Giants
        "Google", "Microsoft", "Amazon", "Meta", "Facebook", "Apple", "IBM", "Oracle", "SAP", "Intel", 
        "Cisco", "Dell", "HP", "NVIDIA", "Samsung", "Sony", "Siemens", "LG", "Huawei", "LinkedIn",
        # Consulting
        "Accenture", "Capgemini", "Deloitte", "Ernst & Young", "EY", "KPMG", "PwC", "BCG", "McKinsey", "Bain",
        # Brazilian Top Companies
        "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa", "Vale", "Petrobras", "Embraer", 
        "Ambev", "Natura", "Magazine Luiza", "Nubank", "iFood", "Mercado Livre", "PagSeguro", "Stone", 
        "XP Investimentos", "BTG Pactual", "Magalu", "B3", "Totvs", "Movile", "Quinto Andar",
        "99", "Loft", "Creditas", "Loggi", "Gympass", "Zap", "B2W", "Via Varejo", "Grupo Pão de Açúcar",

    ]
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
    "result": "Primeira Fase",
    "pdf_filename": "PDF_Filename"
} 