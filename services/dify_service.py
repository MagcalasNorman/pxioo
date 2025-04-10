# services/dify_service.py
import requests
import json

class DifyService:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
    
    def send_message(self, user_message):
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'query': user_message,
                'inputs': {},
                'response_mode': 'streaming',
                'user': 'unique-user-id'
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, stream=True)
            response.raise_for_status()  # Raises exception for 4XX/5XX responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error calling Dify API: {str(e)}")
            raise