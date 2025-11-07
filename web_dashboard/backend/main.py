from app.api import app

if __name__ == "__main__":
    app.run(host="10.0.0.241", port=8000, debug=True, use_reloader=False, threaded=True)