#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: .env file not found!" | tee -a script.log
    exit 1
fi

# Set default values if not defined in the .env file
DEST_FOLDER=${DEST_FOLDER:-"/recordings"}
VIDEO_FORMAT=${VIDEO_FORMAT:-"mp4"}
SEGMENT_TIME=${SEGMENT_TIME:-900} #15mins
RTSP_URL=${RTSP_URL:-""}

# Check for essential variables
if [ -z "$RTSP_URL" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: RTSP_URL is not set in the .env file!" | tee -a script.log
    exit 1
fi

# Ensure destination folder exists
mkdir -p "$DEST_FOLDER"

# Construct the ffmpeg command
ffmpeg_cmd="ffmpeg -rtsp_transport tcp -y -timeout 1000000 -i '$RTSP_URL' -c:v copy -an -f segment -segment_time $SEGMENT_TIME -segment_atclocktime 1 -strftime 1 '$DEST_FOLDER/%Y-%m-%d_%H-%M-%S.$VIDEO_FORMAT' -loglevel info"

# Execute the ffmpeg command and capture the output
{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: Starting ffmpeg command"
    eval $ffmpeg_cmd
    if [ $? -ne 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: ffmpeg command failed!" | tee -a script.log
        exit 1
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: ffmpeg command completed successfully" | tee -a script.log
    fi
} 2>&1 | tee -a script.log
