from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from PIL import Image, ImageGrab
from os import system
import cv2
import subprocess
import pydirectinput

app = Flask(__name__)

# Configuration
config = {
    "robloxpath": "C:\\Users\\ender\\AppData\\Local\\Roblox\\Versions\\version-70a2467227df4077\\RobloxPlayerBeta.exe",
    "video_path": "C:\\Users\\ender\\OneDrive\\Pulpit\\Stuff\\Videos\\giftbox.mp4",
    "video_mode": False,
    "keyboard": False,
    "roblox": False,
    "resx": 190,
    "resy": 90
    #"resx": 320,
    #"resy": 240
    #"resx": 240,
    #"resy": 135
}

# Pre-process and store video frames
video_frames_hex = []

# Set needed variables for video settings
video_lenght = 0
video_fps = 0

# Whitelisted Keys
valid_keys = {"w", "a", "s", "d", "i", "o", "left", "right", "space"}

def process_video_hex():
    cap = cv2.VideoCapture(config["video_path"])
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames in the video
    vid_lenght = total_frames - 1
    vid_fps = int(cap.get(cv2.CAP_PROP_FPS))
    success, frame = cap.read()
    frames_computed = 0
    
    while success:
        frame = cv2.resize(frame, (config["resx"], config["resy"]))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hex_str = ','.join([f'"{r:02x}{g:02x}{b:02x}"' for r, g, b in rgb_frame.reshape(-1, 3)])
        video_frames_hex.append(hex_str)
        
        frames_computed += 1
        print(f'Frames Processed: {frames_computed}/{total_frames}', end='\r')  # '\r' returns the cursor to the start of the line

        success, frame = cap.read()

    print(f'\nAll frames processed: {frames_computed}/{total_frames}.')  # New line after processing is complete
    cap.release()

    return vid_lenght, vid_fps

def generate_rgb():
    screenshot = ImageGrab.grab().resize((config["resx"], config["resy"]))
    rgb_str = ','.join([f'"{r},{g},{b}"' for r, g, b in screenshot.getdata()])
    return f'{{"RGB": [{rgb_str}]}}'

def generate_hex():
    screenshot = ImageGrab.grab().resize((config["resx"], config["resy"]))
    hex_str = ','.join([f'"{r:02x}{g:02x}{b:02x}"' for r, g, b in screenshot.getdata()])
    return f'{{"HEX": [{hex_str}]}}'

if config["video_mode"]:
    @app.route('/')
    def index():
        frame_index = request.args.get('frame', default=0, type=int)
        if frame_index < len(video_frames_hex):
            return Response(f'{{"HEX": [{video_frames_hex[frame_index]}]}}', mimetype = 'application/json')
        else:
            return Response('{"Error": "Frame index out of range"}', mimetype = 'application/json', status = 404)
else:
    @app.route('/')
    def index():
        return Response(generate_hex(), mimetype='application/json')
    
@app.route('/vidsett')
def video_settings():
    print(video_lenght)
    print(video_fps)
    if config["video_mode"]:
        return {"LEN": [video_lenght, video_fps]}
    else:
        return {"LEN": [0, 0]}

@app.route('/res')
def resolution():
    return {"RES": [config["resx"], config["resy"]]}

@app.route('/key')
def keyboard_status():
    return {"KEY": config["keyboard"]}

@app.route('/keysend')
def keyboard_type():
    key = request.args.get('key', '').lower()
    if config["keyboard"] and key in valid_keys:
        pydirectinput.press(key)
        return {"KEYSEND": True}
    return {"KEYSEND": False}

@app.route('/roblox')
def roblox_status():
    return {"ROBLOX": config["roblox"]}

@app.route('/robloxjoin')
def roblox_join():
    placeid = request.args.get('placeid')
    if config["roblox"] and placeid:
        subprocess.run(["taskkill", "/f", "/im", "RobloxPlayerBeta.exe"], check=False)
        subprocess.run([config["robloxpath"], f"roblox://placeID={placeid}"], check=False)
        return {"ROBLOXJOIN": True}
    return {"ROBLOXJOIN": False}

if __name__ == '__main__':
    system("title Screenshare Encoder / Made by @RebornEnder (zdir)")
    if config["video_mode"]:
        video_lenght, video_fps = process_video_hex()
    print(f'> Output Resolution: {config["resx"]}x{config["resy"]}. <')
    print(f'> Keyboard Status: {str(config["keyboard"])}. <')
    print(f'> Roblox GameJoin Status: {str(config["roblox"])}. <')
    print(f'> Hosting Server On: http://127.0.0.1:8080. <\n')
    server = WSGIServer(('127.0.0.1', 8080), app)
    server.serve_forever()
