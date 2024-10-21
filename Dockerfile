# Use the official Python 3.10 slim image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy your application code (if you have any)
COPY . .

# Optionally, install any required packages
# RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to launch a shell
CMD ["/bin/bash"]


# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /app

# # ARG PIP_VERSION=23.3.1
# # ARG POETRY_VERSION=1.8.4
# # ARG WHEN_CHANGED_VERSION=0.3.0

# # # Run inside poetry environment by default
# # ENTRYPOINT ["poetry", "run", "--"]

# # # Install poetry version
# # RUN pip install pip==${PIP_VERSION} \
# #     poetry==${POETRY_VERSION} \
# #     when-changed==${WHEN_CHANGED_VERSION}

# # # Copy the project files into the container
# # COPY pyproject.toml poetry.lock /app/

# # # Install project dependencies with Poetry
# # RUN poetry install --no-interaction --no-ansi

# # Copy the rest of the application files
# COPY . /app

# # # Install project dependencies with Poetry
# # RUN poetry install --no-interaction --no-ansi

# # Define the command to run the app (replace with your command)
# # CMD ["python", "-M", "automatic_interface.py"]
