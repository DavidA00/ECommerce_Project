from inventory_service.flask_runner import start_flask_app
from memory_profiler import profile
import requests
from multiprocessing import Process

@profile
def call_api():
    endpoints = [
        {"method": "POST", "url": "http://127.0.0.1:5000/products/new", "data": {
            "name": "Laptop",
            "description": "A high-performance laptop",
            "category": "Electronics",
            "price": 1500.00,
            "stock": 10
        }},
        {"method": "GET", "url": "http://127.0.0.1:5000/products"},
        {"method": "GET", "url": "http://127.0.0.1:5000/products/Laptop"},
        {"method": "PUT", "url": "http://127.0.0.1:5000/products/update/Laptop", "data": {
            "price": 1400.00,
            "stock": 8
        }},
        {"method": "POST", "url": "http://127.0.0.1:5000/products/stock/Laptop"},
        {"method": "DELETE", "url": "http://127.0.0.1:5000/products/Laptop"}
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
