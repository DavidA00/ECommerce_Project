from reviews_service.flask_runner import start_flask_app
from memory_profiler import profile
import requests
from multiprocessing import Process

@profile
def call_api():
    token = None

    response = requests.post("http://127.0.0.1:7000/login", json={
        "username": "admin1", 
        "password": "password1"
    })

    if response.status_code == 200:
        token = response.json().get("token")
    else:
        print("Error during login:", response.json())
        return

    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        {"method": "POST", "url": "http://127.0.0.1:7000/reviews", "data": {
            "product_name": "Laptop",
            "rating": 5,
            "comment": "Great product!"
        }},
        {"method": "GET", "url": "http://127.0.0.1:7000/reviews/product/Laptop"},
        {"method": "PUT", "url": "http://127.0.0.1:7000/reviews/update/1", "data": {
            "rating": 4,
            "comment": "Updated review comment."
        }},
        {"method": "DELETE", "url": "http://127.0.0.1:7000/reviews/delete/1"},
    ]

    for endpoint in endpoints:
        try:
            if endpoint["method"] == "POST":
                requests.post(endpoint["url"], headers=headers, json=endpoint.get("data"))
            elif endpoint["method"] == "GET":
                requests.get(endpoint["url"], headers=headers)
            elif endpoint["method"] == "PUT":
                requests.put(endpoint["url"], headers=headers, json=endpoint.get("data"))
            elif endpoint["method"] == "DELETE":
                requests.delete(endpoint["url"], headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint['url']}: {e}")

if __name__ == "__main__":
    flask_process = Process(target=start_flask_app)
    flask_process.start()

    try:
        call_api()
    finally:
        flask_process.terminate()
