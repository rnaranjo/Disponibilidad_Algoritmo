from flask import Blueprint, jsonify, make_response
from .models import db, Forecast, Availability
import pandas as pd
from datetime import datetime
import requests
import json

bp = Blueprint('routes', __name__)

# Test route, see if service is running by connecting to host:port/test
@bp.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

# Route for storage of availability calculations
@bp.route('/write_availability', methods=['GET'])
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