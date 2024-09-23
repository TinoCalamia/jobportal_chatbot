# Use an official Python runtime as a parent image
FROM python:3.11.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the service account key JSON into the container
COPY .credentials/service_account.json /app/service_account.json

# Set the environment variable for Google credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json"

RUN python fetch_secrets.py

# Make port 8080 available to the world outside this container
EXPOSE 8080

# # Set environment variables
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     STREAMLIT_SERVER_PORT=8501 \
#     STREAMLIT_SERVER_HEADLESS=true

# Run streamlit when the container launches
CMD ["streamlit", "run", "streamlit_app.py", "–server.port=8080", "–server.address=0.0.0.0"]