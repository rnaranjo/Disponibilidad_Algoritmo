from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'

db = SQLAlchemy(app)

# Database models
class Forecast(db.Model):
  __tablename__ = 'forecasts'

  id = db.Column(db.Integer, primary_key=True)
  fecha = db.Column(db.Date, nullable=False)
  demanda = db.Column(db.Integer, nullable=False)

  def json(self):
    return {
      'id': self.id,
      'fecha': self.fecha,
      'demanda': self.demanda
    }

class Shift(db.Model):
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

# Test route, see if service is running by connecting to host:port/test
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

# Route for storage of availability calculations
@app.route('/write_availability', methods=['GET'])
def write_availability():
  # Query all forecasts for availability calculations
  forecasts_query = Forecast.query.all()

  # Convert data to JSON format
  forecasts_json = []
  for forecast in forecasts_query:
    forecasts_json.append(forecast.json())

  # Convert the SQLAlchemy query json results to pandas DataFrame
  forecast_by_day = pd.DataFrame(forecasts_json)

  # Perform calculations before sending it to model microservice
  forecast_by_day['fecha'] = forecast_by_day['fecha'].astype('datetime64[ns]')
  forecast_by_day['week'] = forecast_by_day['fecha'].dt.isocalendar().week
  forecast_by_day['day'] = forecast_by_day['fecha'].dt.isocalendar().day

  # Convert pandas dataframe to json before sending it to model microservice
  forecast_json = forecast_by_day.to_json(orient="records")

  response = requests.post(
    "http://model_service:4002/calculate_availability",
    headers={"Content-Type": "application/json"},
    json={"forecasts": forecast_json}
  )
  
  # Check if response from the model service is positive. If so, store results to the database.
  if response.status_code == 200:
  	# Parse JSON returned from model service
    text = json.loads(response.text)
    availability_json = json.loads(text)
    availabilities = []
    for availability in availability_json:
      # Convert JSON data to a model object
      availabilities.append(Availability(
        collaborator=availability["collaborator"],
        date=datetime.fromtimestamp(availability["date"]/1000),
        availability=availability["availability"],
        week=availability["week"],
        day=availability["day"] 
      ))

    # Add all the objects to the database session
    db.session.add_all(availabilities)
    # Commit the changes to the database
    db.session.commit()
    return make_response(jsonify(availability_json), 200)
  else:
    return make_response(jsonify({"error": "There was a problem processing the data."}), 400)