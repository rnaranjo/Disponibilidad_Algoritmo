FROM python:3.11.5-slim

WORKDIR ./

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Execute script
COPY . .
CMD ["python", "db_setup.py"]