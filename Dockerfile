# Use an official Python runtime as a parent image
FROM python:3.11

RUN mkdir -p /app/

# Copy the current directory contents into the container at /usr/src/app
COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV TELETHON_API_ID=<your-api-id>
ENV TELETHON_API_HASH=<your-api-hash>

# Run the command to start the server
CMD ["python", "main.py"]
