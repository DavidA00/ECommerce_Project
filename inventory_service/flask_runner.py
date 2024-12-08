def start_flask_app():
    import sys
    sys.path.append('C:/Users/mkrei/OneDrive/Desktop/Fall 2024/EECE 439/EECE 439 - Final Project/ECommerce_Project')
    from inventory_service.inventory_app import app
    app.run(port=5000)
