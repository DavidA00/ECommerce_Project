from sales_service.flask_runner import start_flask_app
from memory_profiler import profile
import requests
from multiprocessing import Process

@profile
def call_api():
    # Test API endpoints
    endpoints = [
        {
            "method": "POST",
            "url": "http://127.0.0.1:6000/sales",
            "data": {
                "username": "testuser",  
                "product_name": "TestDuplicateProduct",  
                "quantity": 1
            }
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:6000/sales/history/testuser"
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:6000/sales/products"
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:6000/sales/products/TestDuplicateProduct"  
        }
    ]

    for endpoint in endpoints:
        try:
            if endpoint["method"] == "POST":
                response = requests.post(endpoint["url"], json=endpoint.get("data"))
            elif endpoint["method"] == "GET":
                response = requests.get(endpoint["url"])
            print(f"Response from {endpoint['url']}: {response.status_code} - {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint['url']}: {e}")

if __name__ == "__main__":
    flask_process = Process(target=start_flask_app)
    flask_process.start()

    try:
        call_api()
    finally:
        flask_process.terminate()
