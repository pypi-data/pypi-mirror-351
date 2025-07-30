
from langchain_groq import ChatGroq

class LLM_Config:
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature  
    def llm(self):
        return ChatGroq(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature
        )


