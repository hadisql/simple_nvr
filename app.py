from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
from dotenv import load_dotenv
import psutil

load_dotenv()

app = Flask(__name__, static_folder='static')
recording_process = None
is_recording = False

DEBUG = os.getenv('DEBUG', 'False') == 'True'
RUNNING_IN_DOCKER = os.getenv('RUNNING_IN_DOCKER', 'False') == 'True'

def is_ffmpeg_running():
    """Check if there is any FFmpeg process running on the system."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'ffmpeg' in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

@app.route('/')
def index():
    print(f'debug ? -> {DEBUG}')
    print(f'running in docker ? -> {RUNNING_IN_DOCKER}')
    print(f'is_recording ? -> {is_recording}')
    return render_template('index.html', is_recording=is_recording, process_running=is_ffmpeg_running(), debug=DEBUG)

@app.route('/start', methods=['POST'])
def start_recording():
    global recording_process, is_recording

    if is_ffmpeg_running():
        # FFmpeg is already running, do not start another instance
        print("An FFmpeg process is already running. Cannot start a new recording.")
        return redirect(url_for('index', already_running=True))

    rtsp_url = request.form.get('rtsp_url')
    segment_time = request.form.get('segment_time')
    subfolder = request.form.get('subfolder')
    video_format = request.form.get('video_format')
    remove_recordings = request.form.get('remove_recordings')
    hours = request.form.get('hours_input')
    audio = request.form.get('audio')

    print(f'rtsp_url -> {rtsp_url}\nsegment_time -> {segment_time}\nsubfolder -> {subfolder}\nvideo_format -> {video_format}')

    # Set the base destination folder
    dest_folder = '/recordings' if RUNNING_IN_DOCKER else 'recordings'

    # If subfolder is provided, append it to the destination folder
    if subfolder:
        dest_folder = os.path.join(dest_folder, subfolder)

    if not is_recording:
        # Ensure the directory exists
        os.makedirs(dest_folder, exist_ok=True)

        # Construct the ffmpeg command
        audio_option = '-c:a copy' if audio == 'True' else '-an'
        ffmpeg_cmd = f"ffmpeg -rtsp_transport tcp -y -timeout 1000000 -i '{rtsp_url}' -c:v copy {audio_option} -f segment -segment_time {segment_time} -strftime 1 '{dest_folder}/%Y-%m-%d_%H-%M-%S.{video_format}' -loglevel info"
        # Start the ffmpeg process
        recording_process = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        is_recording = True
        print(f'FFmpeg command: {ffmpeg_cmd}')
        print('Recording process started')

    # Set up cron job if remove_recordings is specified and greater than 0
    if remove_recordings and (int(remove_recordings) or int(hours)) > 0:
        days = int(remove_recordings)
        hours = int(hours)
        print(f'Removing recordings older than {days} days')
        if not DEBUG:
            schedule_cleanup(dest_folder, video_format, days, hours)

    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording_process, is_recording

    if is_recording and recording_process:
        # Kill the recording process
        recording_process.terminate()
        recording_process.wait()
        recording_process = None
        is_recording = False
        print('Recording process stopped')

    return redirect(url_for('index'))

def schedule_cleanup(dest_folder, video_format, days, hours):
    # Path to the cleanup script
    cleanup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cleanup_old_recordings.sh')

     # Calculate the total minutes
    total_minutes = days * 24 * 60 + hours * 60

    # Create the cleanup script
    with open(cleanup_script_path, 'w') as f:
        f.write(f"#!/bin/bash\nfind {dest_folder} -type f -name '*.{video_format}' -mmin +{total_minutes} -exec rm {{}} \\;")

    # Make the script executable
    os.chmod(cleanup_script_path, 0o755)

    # Schedule the cron job
    cron_job = f"0 0 * * * {cleanup_script_path}\n"
    with open("/etc/crontabs/root", "a") as cron_file:
        cron_file.write(cron_job)

    # Reload the cron daemon to apply the changes
    subprocess.run(["crontab", "/etc/crontabs/root"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8217, debug=os.getenv('DEBUG'))
