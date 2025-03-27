import google.generativeai as genai
from config import GEMINI_MODEL, CRITERIA
from utils import rate_limited_request

class UniversityFilterAgent:
    """Agent responsible for analyzing if a candidate meets university criteria"""
    
    def __init__(self):
        """Initialize the university filter agent with the Gemini model"""
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def check_university_criteria(self, resume_text):
        """
        Check if the candidate is currently enrolled in a Federal/State university
        """
        # Create the prompt with clear instructions
        prompt = self._create_analysis_prompt(resume_text)
        
        try:
            # Generate the analysis with Gemini using rate limiting
            response = rate_limited_request(self.model.generate_content, prompt)
            result = response.text.strip().lower()
            
            # Determine the result
            if "sim" in result:
                return True, "Candidato atende aos critérios universitários"
            else:
                return False, "Candidato não atende aos critérios universitários"
                
        except Exception as e:
            print(f"Error analyzing university criteria: {str(e)}")
            return False, f"Erro na análise: {str(e)}"
    
    def _create_analysis_prompt(self, resume_text):
        """Create a clear prompt for analyzing university criteria"""
        # Get criteria from config
        university_types = ", ".join(CRITERIA["university_type"])
        excluded_types = ", ".join(CRITERIA["excluded_university_type"])
        education_keywords = ", ".join(CRITERIA["education_status"])
        graduation_keywords = ", ".join(CRITERIA["graduation_keywords"])
        
        return f"""
        Analise o currículo a seguir e determine se o candidato atende a AMBOS os critérios:
        
        1. O candidato deve estar ATUALMENTE CURSANDO a graduação (não ter se formado e não estar fazendo pós).
           Palavras-chave que indicam que está cursando: {education_keywords}
           REJEITE candidatos que já se formaram na graduação, indicado por palavras como: {graduation_keywords}
           
        2. A graduação deve ser APENAS em uma universidade Federal ou Estadual (NÃO PODE SER PARTICULAR).
           Palavras-chave para universidades aceitas: {university_types}
           
           REQUISITO ELIMINATÓRIO: Se identificar qualquer faculdade particular ou privada, o candidato DEVE ser rejeitado.
           Exemplos de instituições NÃO aceitas: {excluded_types}
           
           Em caso de dúvida sobre se a universidade é federal/estadual ou privada, presuma que é privada e REJEITE.
        
        Seja EXTREMAMENTE RIGOROSO na análise:
        - O candidato DEVE ser um aluno de graduação ATUAL em universidade federal ou estadual
        - Rejeite candidatos já formados (graduados)
        - Rejeite candidatos sem graduação (só ensino médio)
        - REJEITE QUALQUER candidato de universidade/faculdade particular ou privada
        
        Responda apenas com 'Sim' se AMBOS os critérios forem atendidos, ou 'Não' se pelo menos um critério não for atendido.
        
        Texto do currículo:
        {resume_text}""" 