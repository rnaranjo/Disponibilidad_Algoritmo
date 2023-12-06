from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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