import os
import openai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY") # acts as proxy key if using OpenAI-compatible proxy
        self.model = os.getenv("LLM_MODEL", "aiml/claude-3-5-sonnet")
        self.client = openai.OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.aimlapi.com/v1" # or standard proxy base url if applicable, or generic openai client
        ) if self.api_key else None

    def query(self, prompt: str, system_prompt: str = "You are an expert DevSecOps and security engineering AI.") -> str:
        if not self.client:
            raise ValueError("API key is not set or client is not initialized.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying LLM: {e}"
