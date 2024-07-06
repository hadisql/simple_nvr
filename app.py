from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__, static_folder='static')
recording_process = None

DEBUG = os.getenv('DEBUG', 'False') == 'True'
RUNNING_IN_DOCKER = os.getenv('RUNNING_IN_DOCKER', 'False') == 'True'

@app.route('/')
def index():
    print(f'debug ? -> {DEBUG}')
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recording():
    global recording_process

    rtsp_url = request.form.get('rtsp_url')
    segment_time = request.form.get('segment_time')
    subfolder = request.form.get('subfolder')
    video_format = request.form.get('video_format')

    print(f'rtsp_url -> {rtsp_url}\nsegment_time -> {segment_time}\nsubfolder -> {subfolder}\nvideo_format -> {video_format}')

    # Set the base destination folder
    dest_folder = '/recordings' if RUNNING_IN_DOCKER else 'recordings'

    # If subfolder is provided, append it to the destination folder
    if subfolder:
        dest_folder = os.path.join(dest_folder, subfolder)

    if recording_process is None:
        # Construct the ffmpeg command
        # ffmpeg_cmd = f"ffmpeg -rtsp_transport tcp -y -timeout 1000000 -i '{rtsp_url}' -c:v copy -an -f segment -segment_time {segment_time} -segment_atclocktime 1 -strftime 1 '{dest_folder}/%Y-%m-%d_%H-%M-%S.{video_format}' -loglevel info"
        ffmpeg_cmd = f"ffmpeg -rtsp_transport tcp -y -timeout 1000000 -i '{rtsp_url}' -c:v copy -an -f segment -segment_time {segment_time} -strftime 1 '{dest_folder}/%Y-%m-%d_%H-%M-%S.{video_format}' -loglevel info"
        # Start the ffmpeg process
        recording_process = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Recording process started')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording_process

    if recording_process is not None:
        # Kill the recording process
        recording_process.terminate()
        recording_process.wait()
        recording_process = None
        print('Recording process stopped')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8217, debug=os.environ['DEBUG'])
