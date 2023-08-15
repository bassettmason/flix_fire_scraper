# Use an official Python runtime as the parent image
FROM python:3.11-slim


# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install poetry
RUN pip install poetry

# Set poetry configurations (not to create a virtual env and install dependencies directly)
RUN poetry config virtualenvs.create false

# Install the application dependencies using poetry
RUN poetry install --only main

# Make port 8000 available to the world outside the container
EXPOSE 8000

# Define the command to run the application using Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
