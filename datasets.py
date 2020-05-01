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
DATA_MODEL_ID = API_BASE_URL + "/facets/{ID}/profile/uk.ac.hdrukgateway/HdrUkProfilePluginService"

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

def process_data_models(data_models):
  count = data_models['count']
  headers = []
  data = []
  for d in data_models['items']:
    URL = DATA_MODEL_ID.format(ID=d['id'])
    row = request_url(URL)
    headers.extend(list(row.keys()))
    data.append(row)
  print("Retrieved ", count, " records.")
  return data, list(set(headers))

def main():
  data_models = request_url(DATA_MODELS)
  data, headers = process_data_models(data_models)
  export_csv(data, 'datasets.csv', headers)

if __name__ == "__main__":
    main()
