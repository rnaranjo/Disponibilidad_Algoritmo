from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

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

  def json(self):
    return {
      'id': self.id,
      'name': self.name,
      'Inicio_Turno': self.Inicio_Turno,
      'Fin_Turno': self.Fin_Turno,
      'Tipo_Turno': self.Tipo_Turno
    }


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
  forecasts_query = Forecast.query.all()
  shifts_query = Shift.query.all()

  # Convert data to JSON format
  forecasts_json = []
  for forecast in forecasts_query:
    forecasts_json.append(forecast.json())

  shifts_json = []
  for shift in shifts_query:
    shifts_json.append(shift.json())

  # Convert the SQLAlchemy query json results to pandas DataFrame
  forecast_by_day = pd.DataFrame(forecasts_json)
  shifts = pd.DataFrame(shifts_json)

  # Perform calculations before sending it to model microservice
  forecast_by_day['fecha'] = forecast_by_day['fecha'].astype('datetime64[ns]')
  dates = forecast_by_day['fecha'].dt.date.unique()
  forecast_by_day['week'] = forecast_by_day['fecha'].dt.isocalendar().week
  forecast_by_day['day'] = forecast_by_day['fecha'].dt.isocalendar().day

  shifts['Inicio_Turno'] = shifts['Inicio_Turno'].astype('datetime64[ns]')
  shifts['Fin_Turno'] = shifts['Fin_Turno'].astype('datetime64[ns]')
  periodos = 24
  tiempo = [(timedelta(hours=0, minutes=15*i * 96/periodos)) for i in range(int(periodos))]
  shifts['in'] = shifts['Inicio_Turno'].apply(lambda x: tiempo.index(timedelta(hours=x.hour, minutes=x.minute)))
  shifts['out'] = shifts['Fin_Turno'].apply(lambda x: len(tiempo) if x.hour==0 and x.minute==0 else tiempo.index(timedelta(hours=x.hour, minutes=x.minute)))
  shifts['Lenght'] = shifts['out'] -shifts['in']

  # Convert pandas dataframe to json before sending it to model microservice
  forecast_json = forecast_by_day.to_json(orient="records")
  shift_json = shifts.to_json(orient="records")

  return make_response(jsonify({
    "forecasts": forecast_json,
    "shifts": shift_json
  }), 200)