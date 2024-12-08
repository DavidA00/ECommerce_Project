import cProfile
import pstats
import io
import requests
from flask import Flask
from multiprocessing import Process

def start_flask_app():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from customer_service.customer_app import app
    app.run(port=4000)

def profile_api_calls():
    profiler = cProfile.Profile()

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
        profiler.enable()
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
        profiler.disable()

    output_file = 'customer_profiler_results.txt'
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
