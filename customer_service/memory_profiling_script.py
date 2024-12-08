from flask_runner import start_flask_app
from memory_profiler import profile
import requests
from multiprocessing import Process

@profile
def call_api():
    endpoints = [
        {"method": "POST", "url": "http://127.0.0.1:4000/customers/new", "data": {
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Elm Street",
            "gender": "male",
            "marital_status": "single"
        }},
        {"method": "GET", "url": "http://127.0.0.1:4000/customers"},
        {"method": "GET", "url": "http://127.0.0.1:4000/customers/johndoe"},
        {"method": "PUT", "url": "http://127.0.0.1:4000/customers/johndoe", "data": {
            "age": 31
        }},
        {"method": "POST", "url": "http://127.0.0.1:4000/customers/johndoe/charge", "data": {
            "amount": 50
        }},
        {"method": "POST", "url": "http://127.0.0.1:4000/customers/johndoe/deduct", "data": {
            "amount": 20
        }},
        {"method": "DELETE", "url": "http://127.0.0.1:4000/customers/johndoe"}
    ]

    for endpoint in endpoints:
        try:
            if endpoint["method"] == "POST":
                requests.post(endpoint["url"], json=endpoint.get("data"))
            elif endpoint["method"] == "GET":
                requests.get(endpoint["url"])
            elif endpoint["method"] == "PUT":
                requests.put(endpoint["url"], json=endpoint.get("data"))
            elif endpoint["method"] == "DELETE":
                requests.delete(endpoint["url"])
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint['url']}: {e}")

if __name__ == "__main__":
    flask_process = Process(target=start_flask_app)
    flask_process.start()

    try:
        call_api()
    finally:
        flask_process.terminate()
