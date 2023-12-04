from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'

db = SQLAlchemy(app)

# Database models
class Forecast(db.Model):
  __tablename__ = 'forecasts'

  id = db.Column(db.Integer, primary_key=True)
  fecha = db.Column(db.Date, nullable=False)
  demanda = db.Column(db.Integer, nullable=False)

class Shifts(db.Model):
  __tablename__ = 'shifts'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  Inicio_Turno = db.Column(db.DateTime, nullable=False)
  Fin_Turno = db.Column(db.DateTime, nullable=False)
  Tipo_Turno = db.Column(db.String(50), nullable=False)


class Availability(db.Model):
  __tablename__ = 'availabilities'

  id = db.Column(db.Integer, primary_key=True)
  collaborator = db.Column(db.String(255), nullable=False)
  date = db.Column(db.Date, nullable=False)
  availability = db.Column(db.Integer, nullable=False)
  week = db.Column(db.Integer, nullable=False)
  day = db.Column(db.Integer, nullable=False)

# Test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

# Route for storage of availability calculations
@app.route('/write_availability', methods=['GET'])
def write_availability():
  forecasts = Forecast.query.all()
  # Convert data to JSON format
  json_data = []
  for forecast in forecasts:
    json_data.append({
      "id": forecast.id,
      "fecha": forecast.fecha,
      "demanda": forecast.demanda
    })

  return make_response(jsonify(json_data), 200)