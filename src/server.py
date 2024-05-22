# Import necessary modules
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, stream_with_context

from aiortc import RTCPeerConnection, RTCSessionDescription
import cv2
import json
import uuid
import asyncio
import logging
import time
from pybraille import convertText
import pytesseract 

# Create a Flask app instance
app = Flask(__name__, static_url_path='/static')

# Set to keep track of RTCPeerConnection instances
pcs = set()

text = ''
braille_text=''

camera = cv2.VideoCapture(0)
#camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
#cv2.waitKey(500)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Function to generate video frames from the camera
def generate_frames():
    global text, braille_text
    while True:
        start_time = time.time()
        success, frame = camera.read()
        if not success:
            break
        else:
            #print("Converting to gray scale")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #print("Running tesseract on the image")
            text = pytesseract.image_to_string(gray)
            #print(f"English text: {text}")
            braille_text = convertText(text)
            #print(f"Braille text: {braille_text}")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Concatenate frame and yield for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            elapsed_time = time.time() - start_time
            logging.debug(f"Frame generation time: {elapsed_time} seconds")
            time.sleep(0.5)

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')
    # return redirect(url_for('video_feed')) #to render live stream directly

# Asynchronous function to handle offer exchange
async def offer_async():
    params = await request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Create an RTCPeerConnection instance
    pc = RTCPeerConnection()

    # Generate a unique ID for the RTCPeerConnection
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pc_id = pc_id[:8]

    # Create a data channel named "chat"
    # pc.createDataChannel("chat")

    # Create and set the local description
    await pc.createOffer(offer)
    await pc.setLocalDescription(offer)

    # Prepare the response data with local SDP and type
    response_data = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    return jsonify(response_data)

# Wrapper function for running the asynchronous offer function
def offer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    future = asyncio.run_coroutine_threadsafe(offer_async(), loop)
    return future.result()

# Route to handle the offer request
@app.route('/offer', methods=['POST'])
def offer_route():
    return offer()

# Route to stream video frames
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream_braille():
    global text, braille_text
    while True:
        if len(text):
            yield "<p> <b>English:</b>"
            yield f"{text}"
            yield "<br/>"
            yield "<p> <b>Braille:</b>"
            yield f"{braille_text}"
            yield "!</p>"
        time.sleep(0.5)

@app.route('/text_feed')
def text_feed():
    return Response (stream_braille(), mimetype='text')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
