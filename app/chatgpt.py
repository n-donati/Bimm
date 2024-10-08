import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatGPT:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("No API key found. Please set OPENAI_API_KEY environment variable.")
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def get_response(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(self.endpoint, headers=headers, json=data)
        response_data = response.json()
        return response_data.get('choices')[0].get('message').get('content')