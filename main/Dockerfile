FROM python:3.10-slim

WORKDIR /app

COPY main/requirements_main.txt .

RUN pip install --no-cache-dir -r requirements_main.txt

COPY main/main.py .
COPY utils ./utils

EXPOSE 8080

ENTRYPOINT ["python3", "main.py"]
