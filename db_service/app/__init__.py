from flask import Flask
from .config import Config
from .routes import bp
from .models import db

app = Flask(__name__)

# Load the configuration from the config.py file
app.config.from_object(Config)

# Register the routes blueprint with the Flask application
app.register_blueprint(bp)

# Initialize database on the application
db.init_app(app)

