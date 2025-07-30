class LLMConfig:
    """
    Configuration for an LLM service.
    """
    def __init__(self, url: str, model_name: str, temperature: float = 0.6, max_tokens: int = 2500, api_token: str = None):
        """
        Initialize a new LLMConfig.

        Args:
            url: The base URL of the LLM service.
            model_name: The name of the model to use.
            temperature: The temperature to use for generation (higher = more creative, lower = more deterministic).
            max_tokens: The maximum number of tokens to generate.
            api_token: Optional API token for authentication.
        """
        self.url = url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_token = api_token