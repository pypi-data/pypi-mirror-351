# lmstudio.py
import requests
import sqlite3

LMSTUDIO_URL = "http://localhost:1234"  # Replace with your LMStudio server URL

def get_models():
    response = requests.get(f"{LMSTUDIO_URL}/v1/models")
    models_data = response.json().get("data", [])
    return [model["id"] for model in models_data]  # Extracting model IDs

def chat_with_model(model, message):
    payload = {
        "model": model,
        "prompt": message,
        "max_tokens": 4096,
        "temperature": 0.1,
        "top_p": 0.9
    }
    response = requests.post(f"{LMSTUDIO_URL}/v1/completions", json=payload)
    return response.json().get("choices", [{}])[0].get("text", "")

def stream_chat_with_model(model, message):
    """
    Sends a prompt to the model and yields only the streaming text responses as they arrive.
    """
    payload = {
        "model": model,
        "prompt": message,
        "max_tokens": 4096,
        "temperature": 0.1,
        "top_p": 0.9,
        "stream": True
    }
    try:
        with requests.post(f"{LMSTUDIO_URL}/v1/completions", json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line and line.startswith(b"data: "):
                    try:
                        import json
                        data = json.loads(line[len(b"data: "):].decode('utf-8'))
                        text = data.get("choices", [{}])[0].get("text", "")
                        if text:
                            yield text
                    except Exception:
                        continue
    except requests.RequestException as e:
        yield f"[Error] {e}"