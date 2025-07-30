import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('VECTORSHIFT_API_KEY')
base_url = 'https://api.vectorshift.ai/v1'

def request(method: str, endpoint: str, query: dict = None, json: dict = None, api_key: str = api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, f'{base_url}{endpoint}', headers=headers, json=json, params=query)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} {response.text}")
    return response.json()

def stream_request(method: str, endpoint: str, query: dict = None, json: dict = None, api_key: str = api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, f'{base_url}{endpoint}', headers=headers, json=json, params=query, stream=True)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} {response.text}")
    # Return a generator for streaming response
    for line in response.iter_lines():
        if line:
            yield line
