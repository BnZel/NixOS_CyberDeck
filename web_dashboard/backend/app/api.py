# REFERENCE/: https://testdriven.io/blog/flask-svelte/
import json, time

from flask import Flask, Response, jsonify
from flask_cors import CORS

from .sensor import Sensor

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"http://10.0.0.241:5173"}})
sensor = Sensor()

@app.route("/")
def root():
    return jsonify({"message":"Welcome to NixOS Cyberdeck Dashboard API"})

@app.route("/all")
def stream_all():
    def generate():
        while True:
            data = sensor.all_output
            yield f"event: all_sensor_update\ndata: {json.dumps(data)}\n\n"
            time.sleep(2)
    return Response(generate(), mimetype="text/event-stream")

@app.route("/gps")
def stream_gps():
    def generate():
        while True:
            data = sensor.gps_output
            yield f"event: gps_sensor_update\ndata: {json.dumps(data)}\n\n"
            time.sleep(2)
    return Response(generate(), mimetype="text/event-stream")

@app.route("/baro")
def stream_baro():
    def generate():
        while True:
            data = sensor.baro_output
            yield f"event: baro_sensor_update\ndata: {json.dumps(data)}\n\n"
            time.sleep(2)
    return Response(generate(), mimetype="text/event-stream")

@app.route("/cpu")
def stream_cpu():
    def generate():
        while True:
            data = sensor.cpu_output
            yield f"event: cpu_sensor_update\ndata: {json.dumps(data)}\n\n"
            time.sleep(2)
    return Response(generate(), mimetype="text/event-stream")