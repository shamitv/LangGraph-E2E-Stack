import requests
import json

url = "http://localhost:8000/api/v1/chat/stream"
data = {"message": "test", "agent_type": "multistep"}

try:
    print(f"Connecting to {url}...")
    with requests.post(url, json=data, stream=True) as r:
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Error content: {r.text}")
            exit(1)
            
        for line in r.iter_lines():
            if line:
                print(f"Recv: {line.decode('utf-8')}")
except Exception as e:
    print(f"Exception: {e}")
