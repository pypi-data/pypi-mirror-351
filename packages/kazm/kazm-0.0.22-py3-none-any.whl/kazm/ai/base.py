class BaseAIProvider:
    def generate_text(self, prompt: str, system_prompt: str|None = None, **kwargs) -> str:
        raise NotImplementedError("Must be implemented by subclass.")
    