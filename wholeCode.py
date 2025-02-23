import logging
from flask import Flask
from flask_cors import CORS

# Import the blueprint from router module
from router import router_bp

app = Flask(__name__)
CORS(app)

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app.register_blueprint(router_bp)  # Blueprint registration

if __name__ == "__main__":
    app.run(debug=True, port=5000)
