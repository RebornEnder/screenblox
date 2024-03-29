from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from PIL import Image, ImageGrab
from os import system
import subprocess
import pydirectinput

app = Flask(__name__)

# Configuration
config = {
    "robloxpath": "C:\\Users\\ender\\AppData\\Local\\Roblox\\Versions\\version-85c66b72a4fe4a74\\RobloxPlayerBeta.exe",
    "keyboard": False,
    "roblox": False,
    #"resx": 320,
    #"resy": 240
    "resx": 190,
    "resy": 90
    #"resx": 240,
    #"resy": 135
}

# Whitelisted Keys
valid_keys = {"w", "a", "s", "d", "i", "o", "left", "right", "space"}

def generate_screenshot_rgb():
    screenshot = ImageGrab.grab().resize((config["resx"], config["resy"]))
    rgb_str = ','.join([f'"{r},{g},{b}"' for r, g, b in screenshot.getdata()])
    return f'{{"RGB": [{rgb_str}]}}'

def generate_screenshot_hex():
    screenshot = ImageGrab.grab().resize((config["resx"], config["resy"]))
    hex_str = ','.join([f'"{r:02x}{g:02x}{b:02x}"' for r, g, b in screenshot.getdata()])
    return f'{{"HEX": [{hex_str}]}}'

@app.route('/')
def index():
    return Response(generate_screenshot_hex(), mimetype='application/json')

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
    print(f'> Output Resolution: {config["resx"]}x{config["resy"]}. <')
    print(f'> Keyboard Status: {str(config["keyboard"])}. <')
    print(f'> Roblox GameJoin Status: {str(config["roblox"])}. <')
    print(f'> Hosting Server On: http://127.0.0.1:8080. <\n')
    server = WSGIServer(('127.0.0.1', 8080), app)
    server.serve_forever()
