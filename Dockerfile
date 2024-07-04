# Use Alpine Linux as the base image
FROM alpine:latest

# Install necessary packages
RUN apk update && apk add --no-cache ffmpeg python3 py3-pip py3-virtualenv curl

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and install Flask
RUN /opt/venv/bin/pip install flask

# Set the working directory
WORKDIR /app

# Copy the script and .env file into the container
COPY app.py /app/
COPY templates /app/templates/
COPY .env /app/.env
COPY tailwind.config.js /app/
COPY static /app/static/

# Download and install Tailwind CSS standalone executable
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss 

# compile tailwind css output
RUN /usr/local/bin/tailwindcss -i /app/static/input.css -o /app/static/output.css --minify
# Set the environment variable to use the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Make the app.py executable
RUN chmod +x /app/app.py

# Expose the web UI port
EXPOSE 8217

# Run the Flask app
CMD ["python3", "app.py"]
