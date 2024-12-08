FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask flask_sqlalchemy flask-jwt-extended 

EXPOSE 6000

CMD ["python", "sales_app.py"]
