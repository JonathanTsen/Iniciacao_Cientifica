import google.generativeai as genai
from config import GEMINI_MODEL, CRITERIA
from utils import rate_limited_request
from agents.university_filter_agent import UniversityFilterAgent
from agents.company_filter_agent import CompanyFilterAgent

class CriteriaAnalysisAgent:
    """Agent responsible for analyzing resume text against criteria using specialized agents"""
    
    def __init__(self):
        """Initialize the analysis agent with specialized filter agents"""
        self.university_agent = UniversityFilterAgent()
        self.company_agent = CompanyFilterAgent()
    
    def analyze_resume(self, resume_text):
        """
        Analyze resume text using specialized agents to check if criteria are met:
        1. Currently enrolled in an undergraduate program at Federal/State university (UniversityFilterAgent)
        2. Has done scientific research OR works at a recognized company (CompanyFilterAgent)
        """
        # Step 1: Check university criteria
        print("Verificando critérios universitários...")
        uni_passes, uni_message = self.university_agent.check_university_criteria(resume_text)
        
        # If university criteria not met, reject immediately
        if not uni_passes:
            print(f"Reprovado: {uni_message}")
            return "Não"
        
        print(f"Universidade aprovada: {uni_message}")
        
        # Step 2: Check experience criteria
        print("Verificando critérios de experiência...")
        exp_passes, exp_message = self.company_agent.check_experience_criteria(resume_text)
        
        # Final decision
        if exp_passes:
            print(f"Experiência aprovada: {exp_message}")
            return "Sim"
        else:
            print(f"Reprovado: {exp_message}")
            return "Não" 