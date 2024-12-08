import cProfile
import pstats
import io
import requests
from flask import Flask
from multiprocessing import Process


def start_flask_app():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from reviews_service.reviews_app import app 
    app.run(port=7000)

def profile_api_calls():
    profiler = cProfile.Profile()

    token = None
    endpoints = [
        {"method": "POST", "url": "http://127.0.0.1:7000/login", "data": {
            "username": "janedoe",  # Replace with an actual user
            "password": "password123"
        }, "authenticate": True},

        {"method": "POST", "url": "http://127.0.0.1:7000/reviews", "data": {
            "product_name": "SampleProduct",
            "rating": 5,
            "comment": "Amazing product!"
        }, "auth": True},

        {"method": "PUT", "url": "http://127.0.0.1:7000/reviews/update/1", "data": {
            "rating": 4,
            "comment": "Good product, but not perfect."
        }, "auth": True},

        {"method": "DELETE", "url": "http://127.0.0.1:7000/reviews/delete/1", "auth": True},

        {"method": "GET", "url": "http://127.0.0.1:7000/reviews/product/SampleProduct"},

        {"method": "GET", "url": "http://127.0.0.1:7000/reviews/customer/janedoe", "auth": True, "admin": True},

        {"method": "PUT", "url": "http://127.0.0.1:7000/reviews/flag/1", "auth": True, "admin": True},
    ]

    headers = {}

    for endpoint in endpoints:
        profiler.enable()
        try:
            if endpoint.get("authenticate"):
                response = requests.post(endpoint["url"], json=endpoint.get("data"))
                token = response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}


            elif endpoint.get("auth"):
                requests.request(endpoint["method"], endpoint["url"], json=endpoint.get("data"), headers=headers)
            else:
                requests.request(endpoint["method"], endpoint["url"], json=endpoint.get("data"))
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint['url']}: {e}")
        profiler.disable()

    output_file = 'reviews_profiler_results.txt'
    with open(output_file, 'w') as f:
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats("time")
        ps.print_stats()
        f.write(s.getvalue())
    print(f"Profiling results saved to: {output_file}")


if __name__ == "__main__":
    flask_process = Process(target=start_flask_app)
    flask_process.start()

    try:
        profile_api_calls()
    finally:
        flask_process.terminate()
