from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.orm import declarative_base
import os
import pandas as pd

db_url = os.environ.get('DB_URL')
engine = create_engine(db_url)

# Create the declarative base for models
Base = declarative_base()

# Database models
class Forecast(Base):
  __tablename__ = 'forecasts'

  id = Column(Integer, primary_key=True)
  fecha = Column(Date, nullable=False)
  demanda = Column(Integer, nullable=False)

class Shifts(Base):
  __tablename__ = 'shifts'

  id = Column(Integer, primary_key=True)
  name = Column(String(255), nullable=False)
  Inicio_Turno = Column(DateTime, nullable=False)
  Fin_Turno = Column(DateTime, nullable=False)
  Tipo_Turno = Column(String(50), nullable=False)


class Availability(Base):
  __tablename__ = 'availabilities'

  id = Column(Integer, primary_key=True)
  collaborator = Column(String(255), nullable=False)
  date = Column(Date, nullable=False)
  availability = Column(Integer, nullable=False)
  week = Column(Integer, nullable=False)
  day = Column(Integer, nullable=False)

# Create the tables
Base.metadata.create_all(bind=engine)

with open("forecast_by_day.csv", 'r') as file:
    data_df = pd.read_csv(file)

data_df.columns = ["fecha","demanda"]
data_df.to_sql('forecasts', con=engine, index=True, index_label='id', if_exists='replace')

with open("shifts.csv", 'r') as file:
    data_df = pd.read_csv(file)

data_df.to_sql('shifts', con=engine, index=True, index_label='id', if_exists='replace')