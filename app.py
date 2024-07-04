from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__)

recording_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recording():
    global recording_process
    if recording_process is None:
        ffmpeg_cmd = [
            'ffmpeg', '-rtsp_transport', 'tcp', '-y', '-timeout', '1000000',
            '-i', os.environ['RTSP_URL'], '-c:v', 'copy', '-an', '-f', 'segment',
            '-segment_time', os.environ['SEGMENT_TIME'], '-segment_atclocktime', '1',
            '-strftime', '1', f"{os.environ['DEST_FOLDER']}/%Y-%m-%d_%H-%M-%S.{os.environ['VIDEO_FORMAT']}",
            '-loglevel', 'info'
        ]
        recording_process = subprocess.Popen(ffmpeg_cmd)
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording_process
    if recording_process is not None:
        recording_process.terminate()
        recording_process = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8217)
