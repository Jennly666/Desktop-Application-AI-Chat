import requests
import os
from dotenv import load_dotenv
from utils.logger import AppLogger

load_dotenv()


class OpenRouterClient:

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.logger = AppLogger()
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL") or "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            self.logger.error("OpenRouter API key not provided")
            raise ValueError("OpenRouter API key not provided")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.logger.info("OpenRouterClient initialized successfully")
        self.available_models = self.get_models()

    def get_models(self):
        self.logger.debug("Fetching available models")
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            models_data = response.json()
            
            self.logger.info(f"Retrieved {len(models_data['data'])} models")
            
            return [
                {
                    "id": model["id"],
                    "name": model.get("name", model["id"])
                }
                for model in models_data["data"]
            ]
        except Exception as e:
            models_default = [
                {"id": "deepseek-coder", "name": "DeepSeek"},
                {"id": "claude-3-sonnet", "name": "Claude 3.5 Sonnet"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            ]
            self.logger.info(f"Retrieved {len(models_default)} models with error: {e}")
            return models_default

    def send_message(self, message: str, model: str):
        self.logger.debug(f"Sending message to model: {model}")
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}]
        }
        
        try:
            self.logger.debug("Making API request")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60,
            )
            response.raise_for_status()
            
            self.logger.info("Successfully received response from API")
            return response.json()

        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {"error": str(e)}

    def get_balance(self):
        try:
            response = requests.get(
                f"{self.base_url}/credits",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return "Ошибка"
            data = data.get('data') or {}
            available = (data.get('total_credits', 0) - data.get('total_usage', 0))
            return f"${available:.2f}"
        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return "Ошибка"
