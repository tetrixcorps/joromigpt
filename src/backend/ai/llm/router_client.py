 from routellm.controller import Controller

class LLMRouter:
    def __init__(self):
        self.client = Controller(
            routers=["mf"],  # Use the "mf" (model family) router
            strong_model="gpt-4-1106-preview",  # Your strong model
            weak_model="ollama_chat/llama3",    # Your weak model (using Ollama)
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the appropriate model based on complexity
        """
        response = self.client.chat.completions.create(
            model="router-mf-0.11593",  # The threshold determines routing percentage
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
