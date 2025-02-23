import logging
from flask import Flask
from flask_cors import CORS

from flask_server import app  # Now importing the app with all routes integrated

CORS(app)

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
