import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def query(self, prompt: str, system_prompt: str = "You are an expert DevSecOps and security engineering AI.") -> str:
        if not self.client:
            return "Mock LLM response: def secure_function(): pass"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error querying LLM: {e}"
