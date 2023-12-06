import os

class Config:
  # Database configuration
  SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL')