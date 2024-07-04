# Use Alpine Linux as the base image
FROM alpine:latest

# Install necessary packages
RUN apk update && apk add --no-cache ffmpeg bash

# Copy the script and .env file into the container
COPY record.sh /usr/local/bin/record.sh
COPY .env /usr/local/bin/.env

# Make the script executable
RUN chmod +x /usr/local/bin/record.sh

# Set the working directory
WORKDIR /usr/local/bin

# Run the script
CMD ["./record.sh"]
