from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__, static_folder='static')
recording_process = None

@app.route('/')
def index():
    # Compile Tailwind CSS
    # subprocess.run(['tailwindcss', '-i', 'static/input.css', '-o', 'static/output.css', '--minify'])
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recording():
    global recording_process

    rtsp_url = os.environ['RTSP_URL']
    segment_time = os.environ['SEGMENT_TIME']
    dest_folder = os.environ['DEST_FOLDER']
    video_format = os.environ['VIDEO_FORMAT']
    if recording_process is None:
        # Construct the ffmpeg command
        ffmpeg_cmd = f"ffmpeg -rtsp_transport tcp -y -timeout 1000000 -i '{rtsp_url}' -c:v copy -an -f segment -segment_time {segment_time} -segment_atclocktime 1 -strftime 1 '{dest_folder}/%Y-%m-%d_%H-%M-%S.{video_format}' -loglevel info"
        # Start the ffmpeg process
        recording_process = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording_process
    if recording_process is not None:
        recording_process.terminate()
        recording_process.wait()
        recording_process = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8217, debug=os.environ['DEBUG'])
