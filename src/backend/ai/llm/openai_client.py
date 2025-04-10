from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:6060/v1",
            api_key="no_api_key"  # No API key needed for local server
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the routed LLM
        """
        response = self.client.chat.completions.create(
            model="router-mf-0.11593",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content 