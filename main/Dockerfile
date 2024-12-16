FROM python:3.10-slim

WORKDIR /app

COPY main/requirements_main.txt .

RUN pip install --no-cache-dir -r requirements_main.txt

COPY main/main.py .
COPY utils ./utils

# If you're running a Flask server or some HTTP service in main.py,
# ensure the port it runs on is exposed. Adjust the port as needed.
EXPOSE 8080

# Set the default command to run your main script
# If your script takes arguments like --file_path, you can set them here or pass them at runtime.
ENTRYPOINT ["python3", "main.py"]
