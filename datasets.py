#!/usr/bin/env python
# usage: datasets.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import sys
import csv
import json
import urllib
import codecs
import uuid
import itertools
import requests
from pprint import pprint

API_BASE_URL="https://metadata-catalogue.org/hdruk/api"
DATA_MODELS = API_BASE_URL + "/dataModels"
DATA_MODEL_ID = API_BASE_URL + "/facets/{MODEL_ID}/profile/uk.ac.hdrukgateway/HdrUkProfilePluginService"
DATA_MODEL_METADATA = API_BASE_URL + "/facets/{MODEL_ID}/metadata?all=true"
DATA_MODEL_CLASSES = DATA_MODELS + "/{MODEL_ID}/dataClasses"
DATA_MODEL_CLASS = DATA_MODELS + "/{MODEL_ID}/dataClasses/{CLASS_ID}"
DATA_MODEL_CLASSES_ELEMENTS = DATA_MODELS + "/{MODEL_ID}/dataClasses/{CLASS_ID}/dataElements?all=true"
DATA_MODEL_SEMANTIC_LINKS = API_BASE_URL + "/catalogueItems/{MODEL_ID}/semanticLinks?all=true"
DATA_MODEL_PIDS = "https://api.uatbeta.healthdatagateway.org/api/v1/datasets/pidList"

def request_url(URL):
  """HTTP GET request and load into data_model"""
  r = requests.get(URL)
  if r.status_code == requests.codes.unauthorized:
    return {}
  elif r.status_code == requests.codes.not_found:
    return {}
  elif r.status_code != requests.codes.ok:
    r.raise_for_status()
  return json.loads(r.text)

def read_json(filename):
  with open(filename, 'r') as file:
    return json.load(file)

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
  print("Processing Data Elements...")
  data = []
  URL = DATA_MODEL_CLASSES_ELEMENTS.format(MODEL_ID=data_model_id, CLASS_ID=data_class_id)
  de_row = request_url(URL)
  data_element_count = int(de_row.get('count', 0))
  if data_element_count > 0:
    for d in de_row['items']:
      print("Processing Data Element: ", d['id'], " : ", d['label'])
      d.pop('breadcrumbs', None)
      d.pop('dataModel', None)
      d.pop('dataClass', None)
      if d.get('dataType', None) is not None:
        d['dataType'].pop('dataModel', None)
        d['dataType'].pop('breadcrumbs', None)
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
      URL = DATA_MODEL_CLASS.format(MODEL_ID=data_model_id, CLASS_ID=d['id'])
      dc_row = request_url(URL)
      dc_row.pop('breadcrumbs', None)
      dc_row.pop('dataModel', None)
      dc_row.pop('editable', None)
      # Collecting DataElements
      data_elements = get_data_elements(data_model_id, d['id'])
      dc_row['dataElementsCount'] = len(data_elements)
      dc_row['dataElements'] = data_elements
      data_classes.append(dc_row)
  data['dataClasses'] = data_classes
  return data

def get_semantic_links(data_model_id, data=None, seen_ids=[], latest=None):
  print("Processing Semantic Links...", data_model_id)
  if data is None:
    data = {}
  URL = DATA_MODEL_SEMANTIC_LINKS.format(MODEL_ID=data_model_id)
  ret = request_url(URL)
  if ret.get('count', None) is None:
    return { 'revisions': data }
  if ret['count'] > 0:
    for links in ret['items']:
      src_ver = links['source']['documentationVersion']
      src_id = links['source']['id']
      data[src_ver] = src_id

      tar_ver = links['target']['documentationVersion']
      tar_id = links['target']['id']
      data[tar_ver] = tar_id
  seen_ids.append(data_model_id)
  revision_ids = list(set(list(data.values())) - set(seen_ids))
  for id in revision_ids:
    new_data = get_semantic_links(id, data, seen_ids, latest)
    data.update(new_data['revisions'])
  data['latest'] = latest
  return { 'revisions': data }

def fix_dates(revisions):
  print("Fixing Dates...")
  from datetime import datetime
  data = {}
  last_updated = []
  date_finalised = []
  for version, id in revisions.items():
    URL = DATA_MODELS + "/" + id
    ret = request_url(URL)
    if ret.get("lastUpdated", None) is not None:
      try:
        lu = datetime.strptime(ret["lastUpdated"], "%Y-%m-%dT%H:%M:%S.%fZ")
      except ValueError:
        lu = datetime.strptime(ret["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
    else:
      lu = None
    if ret.get("dateFinalised", None) is not None:
      try:
        du = datetime.strptime(ret["dateFinalised"], "%Y-%m-%dT%H:%M:%S.%fZ")
      except ValueError:
        du = datetime.strptime(ret["dateFinalised"], "%Y-%m-%dT%H:%M:%SZ")
    else:
      du = lu
    if lu is not None: last_updated.append(lu)
    if du is not None: date_finalised.append(du)
  if len(last_updated) > 0:
    data['modified'] = max(last_updated).strftime("%Y-%m-%dT%H:%M:%SZ")
  else:
    data['modified'] = None
  if len(date_finalised) > 0:
    data['issued'] = min(date_finalised).strftime("%Y-%m-%dT%H:%M:%SZ")
  else:
    data['issued'] = None
  return data

def process_data_models(data_models_list):
  print("Processing Data Models...")
  headers = []
  data = {}
  data['count'] = data_models_list['count']
  data_models = []
  i = 0
  for d in data_models_list['items']:
    i += 1
    print("{}/{}: Processing Data Model: {}".format(i, data['count'], d['id']))
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
    semantic_links = get_semantic_links(d['id'], latest=d['id'])
    row.update(semantic_links)

    # Fix Dates
    dates = fix_dates(row['revisions'])
    row.update(dates)

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

def migrate_v1_to_v2(data):
  new_data = []
  count = data['count']
  data = data['dataModels']
  for d in data:
    new_d = {}
    map_data(d, new_d)
    new_data.append(new_d)
  return {
    'count': len(new_data),
    'dataModels': new_data
  }

def lookup_pids(data):
  pid_list = request_url(DATA_MODEL_PIDS)
  for d in data['dataModels']:
    id = d['id']
    for p in pid_list['data']:
      if id in p['datasetIds']:
        d['pid'] = p['pid']
  return data


def generate_sitemap(data, filename):
  BASE_URL = "https://www.healthdatagateway.org/"
  DATASET_BASE_URL = "https://web.www.healthdatagateway.org/dataset/{}"
  PAGES = [
    "https://www.healthdatagateway.org/pages/about",
    "https://www.healthdatagateway.org/pages/community",
    "https://www.healthdatagateway.org/pages/cookie-notice",
    "https://www.healthdatagateway.org/covid-19",
    "https://www.healthdatagateway.org/pages/frequently-asked-questions",
    "https://www.healthdatagateway.org/pages/guidelines",
    "https://www.healthdatagateway.org/pages/key-terms-glossary",
    "https://www.healthdatagateway.org/pages/latest-news",
    "https://www.healthdatagateway.org/pages/metadata-quality"
  ]

  for d in data['dataModels']:
    id = d['id']
    PAGES.append(DATASET_BASE_URL.format(id))

  with codecs.open(filename, 'w', encoding='utf8') as f:
    f.write(BASE_URL + '\n')
    f.writelines('\n'.join(PAGES))

def main():
  data_models_list = request_url(DATA_MODELS)
  data, headers = process_data_models(data_models_list)
  data = lookup_pids(data)
  export_json(data, 'datasets.json')

  # generate sitemap
  generate_sitemap(data, 'sitemap.txt')
  
  # generate CSV tables
  tables = format_csv_tables(data)
  export_csv(tables['dataModels']['data'], 'datasets.csv', tables['dataModels']['headers'])
  export_csv(tables['dataClasses']['data'], 'dataclasses.csv', tables['dataClasses']['headers'])
  export_csv(tables['dataElements']['data'], 'dataelements.csv', tables['dataElements']['headers'])


if __name__ == "__main__":
    main()
