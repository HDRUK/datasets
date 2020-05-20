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

DATASET_SCHEMA = 'schema/dataset.schema.json'
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

def generate_baseline_from_sections(metadata_sections, metadata_levels=None):
    '''
    generate the baseline schema from METADATA_SECTIONS, a dictionary of dictionaries

    '''
    baseline_dict = {}
    raw_attributes = generate_attribute_list(metadata_sections, metadata_levels=metadata_levels, add_id=True)

    baseline_dict = {attribute: None for attribute in raw_attributes}

    return baseline_dict

def generate_attribute_list(metadata_sections, metadata_levels=None, add_id=True):
    '''

    '''
    raw_attributes = []

    # collect the attribute names
    if metadata_levels:
        for level in metadata_levels:
            raw_attributes.extend(metadata_sections.get(level, []))
    else:
        raw_attributes = [attribute for element in metadata_sections.values() for attribute in element]

    if add_id:
        raw_attributes.insert(0, 'id')

    return raw_attributes


def main():
    validate_schema(DATASET_SCHEMA, BASELINE_SCHEMA)

if __name__ == "__main__":
    main()