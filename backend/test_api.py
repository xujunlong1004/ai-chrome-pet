import requests
import json

# 测试GET请求
print("Testing GET request to /")
try:
    response = requests.get('http://127.0.0.1:8888/')
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting GET request to /health")
try:
    response = requests.get('http://127.0.0.1:8888/health')
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting POST request to /api/chat")
try:
    data = {"message": "你好"}
    response = requests.post('http://127.0.0.1:8888/api/chat', json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
