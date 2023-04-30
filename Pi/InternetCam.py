from flask import Flask, render_template, Response
import threading
import sys

app = Flask(__name__)

frame = None
running = True
needs_frame = True
has_run = False

def receive_frame(in_frame):
    global frame
    frame = in_frame

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():
    global running, needs_frame
    while (running == True):
        global frame
        needs_frame = True
        frame = None
        # waits for a frame from camera
        while (frame == None ):
            if running == False:
                break
        needs_frame = False
        if running:
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

t = None
def run():
    global t
    global has_run 
    if (has_run):
        return
    has_run = True
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0',port='5000'))
    t.setDaemon(True)
    t.start()

def exit():
    global t, running
    sys.exit(0)
    t.join()
    #running = False
    print(t)
    t.stop()
    print(5)