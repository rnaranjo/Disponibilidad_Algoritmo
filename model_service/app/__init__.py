from flask import Flask
from .config import Config
from .routes import bp

app = Flask(__name__)

# Load the configuration from the config.py file
app.config.from_object(Config)

# Register the routes blueprint with the Flask application
app.register_blueprint(bp)