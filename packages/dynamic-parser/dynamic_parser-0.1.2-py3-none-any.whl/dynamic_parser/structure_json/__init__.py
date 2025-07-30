from .llm import LLM_Config
from .utils import robust_json_parser
class LLMParser:
    def __init__(self, api, model, temperature=0.7):
        
        self.llm=LLM_Config(api, model, temperature).llm()

    def fix_json(self, unstructured_json: str) -> dict:
        """
        Fix a JSON string using the provided LLM.
        """
        response = robust_json_parser(unstructured_json,self.llm)
        return response
    


