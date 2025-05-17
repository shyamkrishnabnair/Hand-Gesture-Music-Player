from flask import Flask, Response, render_template, jsonify
import cv2
from gesture_recognizer import GestureRecognizer

app = Flask(__name__)

# Initialize gesture recognizer
recognizer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    global recognizer
    if recognizer is None or not recognizer.is_running():
        recognizer = GestureRecognizer()
        recognizer.start()
        return jsonify({'status': 'Recognition started'})
    return jsonify({'status': 'Recognition already running'})

@app.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    global recognizer
    if recognizer and recognizer.is_running():
        recognizer.stop()
        return jsonify({'status': 'Recognition stopped', 'gestures': recognizer.get_gestures()})
    return jsonify({'status': 'No recognition running'})

@app.route('/video_feed')
def video_feed():
    global recognizer
    if recognizer and recognizer.is_running():
        return Response(recognizer.generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response('No video feed available', status=400)

@app.route('/gesture_log')
def gesture_log():
    global recognizer
    if recognizer:
        return jsonify({'gestures': recognizer.get_gestures()})
    return jsonify({'gestures': []})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)