import cProfile
import pstats
import io
import requests
from flask import Flask
from multiprocessing import Process


def start_flask_app():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from sales_service.sales_app import app
    app.run(port=6000)


def start_flask_app0():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from inventory_service.inventory_app import app
    app.run(port=5000)


def start_flask_app1():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from customer_service.customer_app import app
    app.run(port=4000)
    

def profile_api_calls():
    profiler = cProfile.Profile()

    # Define test data for API calls
    endpoints = [
        {"method": "POST", "url": "http://127.0.0.1:5000/products/new", "data": {
            "name": "SampleProduct",
            "description": "A sample product for testing.",
            "category": "SampleCategory",
            "price": 20.0,
            "stock": 100
        }},
        {"method": "POST", "url": "http://127.0.0.1:4000/customers/new", "data": {
            "full_name": "Jane Doe",
            "username": "janedoe",
            "password": "password123",
            "age": 28,
            "address": "123 Elm Street",
            "gender": "female",
            "marital_status": "single",
            "wallet_balance": 500.0
        }},
        {"method": "POST", "url": "http://127.0.0.1:6000/sales", "data": {
            "username": "janedoe",
            "product_name": "SampleProduct",
            "quantity": 2
        }},
        {"method": "GET", "url": "http://127.0.0.1:6000/sales/history/janedoe"},
        {"method": "GET", "url": "http://127.0.0.1:6000/sales/products"},
        {"method": "GET", "url": "http://127.0.0.1:6000/sales/products/SampleProduct"}
    ]

    for endpoint in endpoints:
        profiler.enable()
        try:
            if endpoint["method"] == "POST":
                requests.post(endpoint["url"], json=endpoint.get("data"))
            elif endpoint["method"] == "GET":
                requests.get(endpoint["url"])
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint['url']}: {e}")
        profiler.disable()

    output_file = 'sales_profiler_results.txt'
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
    flask_process0 = Process(target=start_flask_app0)
    flask_process0.start()
    flask_process1 = Process(target=start_flask_app1)
    flask_process1.start()

    try:
        profile_api_calls()
    finally:
        flask_process.terminate()
        flask_process0.terminate()
        flask_process1.terminate()

