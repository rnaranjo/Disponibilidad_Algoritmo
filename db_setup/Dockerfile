FROM python:3.11.5-slim

WORKDIR ./

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Execute script
COPY . .
EXPOSE 5432
CMD ["python", "db_setup.py"]