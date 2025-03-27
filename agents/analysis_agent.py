import google.generativeai as genai
from config import GEMINI_MODEL, CRITERIA
from utils import rate_limited_request

class CriteriaAnalysisAgent:
    """Agent responsible for analyzing resume text against criteria"""
    
    def __init__(self):
        """Initialize the analysis agent with the Gemini model"""
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def analyze_resume(self, resume_text):
        """
        Analyze resume text using Gemini to check if criteria are met:
        1. Studying at Federal/State university (not private)
        2. Has done scientific research OR works at a recognized company
        """
        # Create the prompt with clear instructions
        prompt = self._create_analysis_prompt(resume_text)
        
        try:
            # Generate the analysis with Gemini using rate limiting
            response = rate_limited_request(self.model.generate_content, prompt)
            result = response.text.strip().lower()
            
            # Determine the result
            if "sim" in result:
                return "Sim"
            else:
                return "Não"
                
        except Exception as e:
            print(f"Error analyzing resume: {str(e)}")
            return "Não"  # Default to No in case of errors
    
    def _create_analysis_prompt(self, resume_text):
        """Create a clear prompt for resume analysis"""
        # Get criteria from config
        university_types = ", ".join(CRITERIA["university_type"])
        excluded_types = ", ".join(CRITERIA["excluded_university_type"])
        research_keywords = ", ".join(CRITERIA["research_keywords"])
        
        return f"""
        Analise o currículo a seguir e determine se o candidato atende a AMBOS os critérios:
        
        1. O candidato deve estar estudando em uma universidade Federal ou Estadual (não pode ser particular).
           Palavras-chave para universidades aceitas: {university_types}
           Palavras-chave para universidades NÃO aceitas: {excluded_types}
           
        2. O candidato deve ter feito uma iniciação científica OU trabalhar em uma empresa reconhecida.
           Palavras-chave para experiência em pesquisa: {research_keywords}
           Para empresas, considere se é uma empresa de grande porte ou com boa reputação no mercado.
        
        Responda apenas com 'Sim' se AMBOS os critérios forem atendidos, ou 'Não' se pelo menos um critério não for atendido.
        Seja rigoroso na análise, verificando explicitamente se a universidade é Federal/Estadual e se há menção clara a iniciação científica ou empresa reconhecida.
        
        Texto do currículo:
        {resume_text}""" 