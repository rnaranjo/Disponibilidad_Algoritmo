from flask import Flask, request, jsonify, make_response
import pandas as pd
from math import ceil
from datetime import timedelta

app = Flask(__name__)

def two_highest_keyvalue(dicc):
  dicc_copy = dict(dicc)
  key1 = max(dicc_copy, key=dicc_copy.get)
  del dicc_copy[key1]
  key2 = max(dicc_copy, key=dicc_copy.get)
  return [key1, key2]

# Test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

# Route for availability calculation
@app.route('/calculate_availability', methods=['POST'])
def calculate_availability():
  # Retrieve the JSON data from the request body
  try:
    json_data = request.get_json()
  except:
    response = jsonify({"error": "Invalid JSON input"})
    response.status_code = 400
    return response

  forecast_json = json_data["forecasts"]
  shift_json = json_data["shifts"]
  forecast_by_day = pd.read_json(forecast_json)
  shifts = pd.read_json(shift_json)

  k1= 1
  k2 = 2
  W_real = 9
  
  forecast_by_day['fecha'] = pd.to_datetime(forecast_by_day['fecha'], unit='ms')
  dates = forecast_by_day['fecha'].dt.date.unique()
  max_wf_wk = forecast_by_day.query('day==7 or day==6')['demanda'].max()
  b1 = ceil((k2 * max_wf_wk) / (k2-k1))
  D_week=0
  for w in forecast_by_day['week'].unique():
    d = forecast_by_day[forecast_by_day['week']==w]['demanda'].to_list()
    D=0
    for i in d:
      D += i
    if D > D_week:
      D_week = D
  b2 = ceil(D/5)
  b3 = forecast_by_day['demanda'].max()

  W = max(b1,b2,b3)
  print(f"Minimum workforce: {W}")
  if W_real > W:
    print("Workforce is enough, surplus: ", W_real-W)
    free_wf_wk = ceil(W_real*k1/k2)
  else:
    print("Workforce is not enough, deficit: ", W-W_real)
    free_wf_wk = ceil(W_real*k1/k2)

  print(f"Workforce free by Weekend: {free_wf_wk}")

  max_demanda_per_weekend = {w:forecast_by_day[forecast_by_day['week']==w].query('day==7 or day==6')['demanda'].max() for w in forecast_by_day['week'].unique()}
  forecast_by_day['surplus'] = forecast_by_day.apply(lambda row: W_real - row['demanda'] if row['day'] not in [6, 7] else W_real - max_demanda_per_weekend[row['week']], axis=1)
  max_dda_wk = forecast_by_day[(forecast_by_day['day']==7) | (forecast_by_day['day']==6)]['demanda'].max()

  # Caso 1:2
  collab_list = [i for i in range(W_real)]
  collab_list_wknd = [collab_list[:int(len(collab_list)/2)], collab_list[int(len(collab_list)/2):]]
  collab_list_wknd = collab_list_wknd*2

  free_wknd_collab = {}
  for w, cs in zip(max_demanda_per_weekend, collab_list_wknd):
    free_wknd_collab[w] = cs

  data = []
  for c in collab_list:
    for fecha in dates:
      data.append([c, fecha])

  df_availability = pd.DataFrame(data, columns=['collaborator', 'date'])
  df_availability['availability'] = 1
  df_availability['date'] = df_availability['date'].astype('datetime64[ns]')
  df_availability['week'] = df_availability['date'].dt.isocalendar().week
  df_availability['day'] = df_availability['date'].dt.isocalendar().day

  for w in free_wknd_collab: # Dar domingo libres
    for c in free_wknd_collab[w]:
      filtro = (df_availability["collaborator"] == c) & (df_availability["day"] == 7) & (df_availability["week"] == w)
      df_availability.loc[filtro, "availability"] = 0

  day_off_by_week = {}
  for wk in  free_wknd_collab: # Pares días libres
    surplus_week = forecast_by_day[(forecast_by_day['week']==wk) & (forecast_by_day['day']!=7)][['day','surplus']].set_index('day').to_dict()['surplus']
    day_off_pairs = []
    for j in range(len(collab_list) - len(free_wknd_collab[wk])):
      keys = two_highest_keyvalue(surplus_week)
      surplus_week[keys[0]] -= 1
      surplus_week[keys[1]] -= 1
      day_off_pairs.append(keys)

    day_off_by_week[wk] = day_off_pairs

  for wk in day_off_by_week: # Dar libres entre semana
    j = 0
    for c in collab_list:
      if df_availability[(df_availability['collaborator']==c) & (df_availability['week']==wk)]['availability'].sum() == 7:
        days_off = day_off_by_week[wk][j]
        filter1 = (df_availability['collaborator']==c) & (df_availability['week']==wk) & (df_availability['day']==days_off[0])
        filter2 = (df_availability['collaborator']==c) & (df_availability['week']==wk) & (df_availability['day']==days_off[1])
        df_availability.loc[filter1, "availability"] = 0
        df_availability.loc[filter2, "availability"] = 0
        j+=1

  availability_json = df_availability.to_json(orient="records")
  
  return make_response(jsonify(availability_json), 200)