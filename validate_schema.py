#!/usr/bin/env python
# usage: validate.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import os
import re
import json
import requests
from jsonschema import validate, Draft7Validator, FormatChecker, draft7_format_checker

DATASET_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/schema/dataset.schema.json'
BASELINE_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/examples/dataset.sample.json'

def get_json(json_uri):
    if isinstance(json_uri,dict):
        return json_uri
    elif os.path.isfile(json_uri):
        with open(json_uri, 'r') as json_file:
            return json.load(json_file)
    elif json_uri.startswith('http'):
        return requests.get(json_uri).json()
    else:
        raise Exception

def validate_schema(schema, json):
    schema = get_json(schema)
    json = get_json(json)
    
    v = Draft7Validator(schema, format_checker=draft7_format_checker)
    errors = sorted(v.iter_errors(json), key=lambda e: e.path)
    print(json['id'], ": Number of validation errors = ", len(errors))
    data = []
    for error in errors:
        err = {}
        if len(list(error.path)):
            err['attribute'] = list(error.path)[0]
            print(err['attribute'], error.message, sep=": ")
            err['message'] = ": ".join([err['attribute'], error.message])
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                print("    ", list(suberror.schema_path)[1], ": ", suberror.message)
                err['suberrors'] = "    " + list(suberror.schema_path)[1] + ": " + suberror.message
        else:
            print(error.message)
            err['attribute'] = re.findall(r"(.*?)'", error.message)[1]
            err['message'] = error.message
        data.append(err)
    return data

def main():
    validate_schema(DATASET_SCHEMA, BASELINE_SCHEMA)

if __name__ == "__main__":
    main()