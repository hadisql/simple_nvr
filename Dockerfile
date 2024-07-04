# Use Alpine Linux as the base image
FROM alpine:latest

# Install necessary packages
RUN apk update && apk add --no-cache ffmpeg python3 py3-pip py3-virtualenv

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and install Flask
RUN /opt/venv/bin/pip install flask

# Copy the script and .env file into the container
COPY app.py /usr/local/bin/app.py
COPY templates /usr/local/bin/templates
COPY .env /usr/local/bin/.env

# Set the environment variable to use the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Make the app.py executable
RUN chmod +x /usr/local/bin/app.py

# Set the working directory
WORKDIR /usr/local/bin

# Expose the web UI port
EXPOSE 8217

# Run the Flask app
CMD ["python3", "app.py"]
