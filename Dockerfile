# Use an official Python runtime as a parent image
FROM python:3.11

RUN mkdir -p /app

# Copy the current directory contents into the container at /usr/src/app
COPY main.py /app
COPY requirements.txt /app
COPY session_name.session /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Run the command to start the server
CMD ["python", "main.py"]
