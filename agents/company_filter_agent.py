import google.generativeai as genai
from config import GEMINI_MODEL, CRITERIA
from utils import rate_limited_request

class CompanyFilterAgent:
    """Agent responsible for analyzing if a candidate meets company/research criteria"""
    
    def __init__(self):
        """Initialize the company filter agent with the Gemini model"""
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def check_experience_criteria(self, resume_text):
        """
        Check if the candidate has either research experience or works at a recognized company
        """
        # Create the prompt with clear instructions
        prompt = self._create_analysis_prompt(resume_text)
        
        try:
            # Generate the analysis with Gemini using rate limiting
            response = rate_limited_request(self.model.generate_content, prompt)
            result = response.text.strip().lower()
            
            # Determine the result
            if "sim" in result:
                return True, "Candidato atende aos critérios de experiência"
            else:
                return False, "Candidato não atende aos critérios de experiência"
                
        except Exception as e:
            print(f"Error analyzing experience criteria: {str(e)}")
            return False, f"Erro na análise: {str(e)}"
    
    def _create_analysis_prompt(self, resume_text):
        """Create a clear prompt for analyzing experience criteria"""
        # Get criteria from config
        research_keywords = ", ".join(CRITERIA["research_keywords"])
        top_companies = ", ".join(CRITERIA.get("top_companies", ["Google", "Microsoft", "Amazon", "Meta", "Apple", "IBM", "Oracle", "SAP", "Intel", "Cisco", "Dell", "HP", "NVIDIA", "Samsung", "Sony", "Siemens", "LG", "Huawei", "Accenture", "Capgemini", "Deloitte", "Ernst & Young", "KPMG", "PwC", "BCG", "McKinsey", "Bain", "Globo", "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa", "Vale", "Petrobras", "Embraer", "Ambev", "Natura"]))
        
        return f"""
        Analise o currículo a seguir e determine se o candidato atende a pelo menos UM dos critérios:
        
        1. O candidato tem experiência em pesquisa científica ou iniciação científica
           Palavras-chave para experiência em pesquisa: {research_keywords}
           
        2. O candidato trabalha ou trabalhou em uma empresa reconhecida no mercado
           Exemplos de empresas reconhecidas: {top_companies}
           Considere também outras empresas de grande porte ou com boa reputação que não estejam nesta lista.
        
        Analise cuidadosamente o currículo do candidato, verificando tanto experiências atuais quanto anteriores.
        Se encontrar menção clara de participação em iniciação científica OU trabalho em empresa reconhecida, o candidato atende aos critérios.
        
        Responda apenas com 'Sim' se pelo menos UM dos critérios for atendido, ou 'Não' se nenhum critério for atendido.
        
        Texto do currículo:
        {resume_text}""" 