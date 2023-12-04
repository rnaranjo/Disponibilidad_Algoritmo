from flask import Flask, request, jsonify, make_response
import pandas as pd

app = Flask(__name__)

# Test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

# Route for availability calculation
@app.route('/calculate_availability', methods=['POST'])
def calculate_availability():
  return make_response(jsonify({'message': 'availability calculated'}), 200)