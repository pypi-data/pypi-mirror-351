import os
import requests
from dotenv import load_dotenv
from typing import Optional

import vectorshift

load_dotenv()

class RequestClient:
    def __init__(self):
        self.api_key = os.environ.get('VECTORSHIFT_API_KEY')
        self.base_url = 'https://api.vectorshift.ai/v1'

    def request(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None):
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, json=json, params=query)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.text}")
        return response.json()

    def stream_request(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None):
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, json=json, params=query, stream=True)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.text}")
        # Return a generator for streaming response
        for line in response.iter_lines():
            if line:
                yield line

request_client = RequestClient()
