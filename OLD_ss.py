from os import system
from flask import Flask, Response
import pyautogui
import time

resx = 320
resy = 240
app = Flask(__name__)

def generate_screenshot():
    screenshot = pyautogui.screenshot().resize((resx, resy))
    pixels = list(screenshot.getdata())
    formatted_pixels = [f"\"{pixel[0]},{pixel[1]},{pixel[2]}\"" for pixel in pixels]
    formatted_row = ",".join(formatted_pixels)
    yield f"{{\"RGB\": [{formatted_row}]}}\n"

@app.route('/')
def index():
    return Response(generate_screenshot(), mimetype='text/plain')

@app.route('/res')
def resolution():
    return Response(f"{{\"RES\": [{resx},{resy}]}}", mimetype='text/plain')

if __name__ == '__main__':
    system("title Screenshare Encoder / Made by @RebornEnder (zdir)")
    print(f"> Output Resolution: {resx}x{resy}. <\n")
    app.run(port=8080)
