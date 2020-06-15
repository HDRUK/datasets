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
from pprint import pprint

API_BASE_URL="https://metadata-catalogue.org/hdruk/api"
DATA_MODELS = API_BASE_URL + "/dataModels"
DATA_MODEL_ID = API_BASE_URL + "/facets/{MODEL_ID}/profile/uk.ac.hdrukgateway/HdrUkProfilePluginService"
DATA_MODEL_CLASSES = DATA_MODELS + "/{MODEL_ID}/dataClasses"
DATA_MODEL_CLASSES_ELEMENTS = DATA_MODEL_CLASSES + "/{CLASS_ID}/dataElements"
DATA_MODEL_SEMANTIC_LINKS = API_BASE_URL + "/catalogueItems/{MODEL_ID}/semanticLinks"

def request_url(URL):
  """HTTP GET request and load into data_model"""
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

def export_json(data, filename, indent=2):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=indent)

def get_data_elements(data_model_id, data_class_id):
  print("Processing Data Elemenets...")
  data = []
  URL = DATA_MODEL_CLASSES_ELEMENTS.format(MODEL_ID=data_model_id, CLASS_ID=data_class_id)
  de_row = request_url(URL)
  data_element_count = int(de_row.get('count', 0))
  if data_element_count > 0:
    for d in de_row['items']:
      print("Processing Data Element: ", d['id'], " : ", d['label'])
      del d['breadcrumbs']
      del d['dataModel']
      del d['dataClass']
      del d['dataType']['dataModel']
      del d['dataType']['breadcrumbs']
      data.append(d)
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
      dc_row['dataElementsCount'] = len(data_elements)
      dc_row['dataElements'] = data_elements
      data_classes.append(dc_row)
  data['dataClasses'] = data_classes
  return data

def get_semantic_links(data_model_id):
  print("Processing Semantic Links...")
  data = {}
  URL = DATA_MODEL_SEMANTIC_LINKS.format(MODEL_ID=data_model_id)
  ret = request_url(URL)
  if ret['count'] > 0:
    for links in ret['items']:
      src_ver = links['source']['documentationVersion']
      src_id = links['source']['id']
      data[src_ver] = src_id

      tar_ver = links['target']['documentationVersion']
      tar_id = links['target']['id']
      data[tar_ver] = tar_id
    data['latest'] = data_model_id
  return { 'versions': data }

def process_data_models(data_models_list):
  print("Processing Data Models...")
  headers = []
  data = {}
  data['count'] = data_models_list['count']
  data_models = []
  for d in data_models_list['items']:
    print("Processing Data Model: ", d['id'])
    URL = DATA_MODELS + "/{ID}".format(ID=d['id'])
    row = request_url(URL)
    # Collect HDR UK Profile information
    URL = DATA_MODEL_ID.format(MODEL_ID=d['id'])
    dm = request_url(URL)
    row.update(dm)

    # Collecting Data Classes
    data_classes = get_data_classes(d['id'])
    row.update(data_classes)

    # Collect SemanticLinks
    semantic_links = get_semantic_links(d['id'])
    row.update(semantic_links)

    headers.extend(list(row.keys()))
    data_models.append(row)
  data['dataModels'] = data_models
  print("Retrieved ", data['count'], " records.")
  return data, list(set(headers))

def format_csv_tables(data):
  tables = {
    'dataModels': {'data': [], 'headers': []},
    'dataClasses': {'data': [], 'headers': []},
    'dataElements': {'data': [], 'headers': []},
  }
  for dm in data['dataModels']:
    for dc in dm['dataClasses']:
      for de in dc['dataElements']:
        de['dataTypeLabel'] = de['dataType']['label']
        de['dataType'] = de['dataType']['domainType']
        de['dataModel'] = dm['id']
        de['dataClass'] = dc['id']
        # Append dataElement to tables
        tables['dataElements']['data'].append(de)
        tables['dataElements']['headers'].extend(de.keys())
      # Add dataElement IDs to dataClass
      data_elements = [de['id'] for de in dc['dataElements']]
      dc['dataElements'] = ", ".join(data_elements)
      # Append dataClass to tables
      tables['dataClasses']['data'].append(dc)
      tables['dataClasses']['headers'].extend(dc.keys())
    # Add dataClasses to dataModel
    data_classes = [dc['id'] for dc in dm['dataClasses']]
    data['dataClasses'] = ", ".join(data_classes)
    tables['dataModels']['data'].append(dm)
    tables['dataModels']['headers'].extend(dm.keys())
  tables['dataModels']['headers'] = list(set(tables['dataModels']['headers']))
  tables['dataClasses']['headers'] = list(set(tables['dataClasses']['headers']))
  tables['dataElements']['headers'] = list(set(tables['dataElements']['headers']))
  print("Count: DM ", data['count'], len(data['dataModels']), len(tables['dataModels']['data']))
  print("Count: DC ", len(tables['dataClasses']['data']))
  print("Count: DE ", len(tables['dataElements']['data']))
  return tables

def main():
  data_models_list = request_url(DATA_MODELS)
  data, headers = process_data_models(data_models_list)
  export_json(data, 'datasets.json')
  tables = format_csv_tables(data)
  export_csv(tables['dataModels']['data'], 'datasets.csv', tables['dataModels']['headers'])
  export_csv(tables['dataClasses']['data'], 'dataclasses.csv', tables['dataClasses']['headers'])
  export_csv(tables['dataElements']['data'], 'dataelements.csv', tables['dataElements']['headers'])


if __name__ == "__main__":
    main()
