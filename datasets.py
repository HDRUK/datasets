#!/usr/bin/env python
# usage: datasets.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import csv
import json
import urllib
import requests

API_BASE_URL="https://metadata-catalogue.org/hdruk/api"
DATA_MODELS = API_BASE_URL + "/dataModels"
DATA_MODEL_ID = API_BASE_URL + "/facets/{MODEL_ID}/profile/uk.ac.hdrukgateway/HdrUkProfilePluginService"
DATA_MODEL_CLASSES = DATA_MODELS + "/{MODEL_ID}/dataClasses"
DATA_MODEL_CLASSES_ELEMENTS = DATA_MODEL_CLASSES + "/{CLASS_ID}/dataElements"

def request_url(URL):
  """HTTP GET request and load into json"""
  r = requests.get(URL)
  if r.status_code != requests.codes.ok:
    r.raise_for_status()
  return json.loads(r.text)

def export_csv(data, filename, header=None):
  if header is None:
    header = ['id', 'name', 'publisher', 'description', 'author', 'metadata_version']
  with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)

def export_json(data, filename):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=2)

def get_data_elements(data_model_id, data_class_id):
  print("Processing Data Elemenets...")
  data = {}
  URL = DATA_MODEL_CLASSES_ELEMENTS.format(MODEL_ID=data_model_id, CLASS_ID=data_class_id)
  de_row = request_url(URL)
  data_element_count = int(de_row.get('count', 0))
  data['dataElementCount'] = data_element_count
  data_elements = []
  if data_element_count > 0:
    for d in de_row['items']:
      print("Processing Data Element: ", d['id'], " : ", d['label'])
      del d['breadcrumbs']
      del d['dataModel']
      del d['dataClass']
      del d['dataType']['dataModel']
      del d['dataType']['breadcrumbs']
      data_elements.append(d)
  data['dataElements'] = data_elements
  return data

def get_data_classes(data_model_id):
  print("Processing Data Classes...")
  data = {}
  URL = DATA_MODEL_CLASSES.format(MODEL_ID=data_model_id)
  dm_row = request_url(URL)
  data_model_count = int(dm_row.get('count', 0))
  data['dataClassesCount'] = data_model_count
  data_classes = []
  if data_model_count > 0:
    for d in dm_row['items']:
      print("Processing Data Class: ", d['id'], " : ", d['label'])
      URL = DATA_MODEL_CLASSES.format(MODEL_ID=data_model_id) + "/{CLASS_ID}".format(CLASS_ID=d['id'])
      dc_row = request_url(URL)
      del dc_row['breadcrumbs']
      del dc_row['dataModel']
      del dc_row['editable']
      # Collecting DataElements
      data_elements = get_data_elements(data_model_id, d['id'])
      dc_row['dataElements'] = data_elements
      data_classes.append(dc_row)
  data['dataClasses'] = data_classes
  return data

def process_data_models(data_models):
  print("Processing Data Models...")
  count = data_models['count']
  headers = []
  data = []
  for d in data_models['items']:
    print("Processing Data Model: ", d['id'])
    URL = DATA_MODEL_ID.format(MODEL_ID=d['id'])
    row = request_url(URL)
    # Collecting Data Classes
    data_classes = get_data_classes(d['id'])
    row.update(data_classes)

    headers.extend(list(row.keys()))
    data.append(row)
  print("Retrieved ", count, " records.")
  return data, list(set(headers))

def main():
  data_models = request_url(DATA_MODELS)
  data, headers = process_data_models(data_models)
  export_csv(data, 'datasets.csv', headers)
  export_json(data, 'datasets.json')

if __name__ == "__main__":
    main()
