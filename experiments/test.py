import requests
import json


def send_chat_request(url, model, messages, schema, stream=False):
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "format": schema
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")


# Example usage
url = "http://localhost:11434/api/chat"
model = "llama3.1"
messages = [{"role": "user", "content": "Tell me about Canada."}]
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "capital": {"type": "string"},
        "languages": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "capital", "languages"]
}

try:
    response = send_chat_request(url, model, messages, schema)
    print(response)
except Exception as e:
    print(e)
