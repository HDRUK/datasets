#!/usr/bin/env python
# usage: completeness_check.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import copy
import csv
import json
import urllib
import requests
from pprint import pprint
from validate_schema import get_json, validate_schema
from datasets import export_csv, export_json

DATASET_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/schema/dataset.schema.json'
BASELINE_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/examples/dataset.sample.json'
DATASETS_JSON = "datasets.json"

METADATA_SECTIONS = {
    "A: Summary": ['identifier', 'title', 'abstract', 'publisher', 'contactPoint', 'accessRights', 'group'],
    "B: Business": ["description", "releaseDate", "accessRequestCost", "accessRequestDuration", "dataController", "dataProcessor", "license", "derivedDatasets", "linkedDataset"],
    "C: Coverage & Detail": ["geographicCoverage", "periodicity", "datasetEndDate", "datasetStartDate", "jurisdiction", "populationType", "statisticalPopulation", "ageBand", "physcicalSampleAvailability", "keywords"],
    "D: Format & Structure": ["conformsTo", "controlledVocabulary", "language", "format", "fileSize"],
    "E:Atrribution": ["creator", "citations", "doi"],
    "F: Technical Metadata": ["dataClassesCount"],
    "G: Other Metadata": ["usageResrictions", "purpose", "source", "setting", "accessEnvironment", "linkageOpportunity", "disabmiguatingDescription"]
}

def nullScore(d):
    count = 0
    nulls = 0
    data = {
        "A: Summary Missing Count": 0,
        "B: Business Missing Count": 0,
        "C: Coverage & Detail Missing Count": 0,
        "D: Format & Structure Missing Count": 0,
        "E:Atrribution Missing Count": 0,
        "F: Technical Metadata Missing Count": 0,
        "G: Other Metadata Missing Count": 0
    }
    for k,v in d.items():
        count = count + 1
        for section, attributes in METADATA_SECTIONS.items():
            # Process metadata sections
            if k in attributes:
                if v is None:
                    data[section + " Missing Count"] = data[section + " Missing Count"] + 1
                if k == "dataClassesCount" and v == 0:
                    data[section + " Missing Count"] = data[section + " Missing Count"] + 1
            data[section + " Total Attributes"] = len(attributes)
        # Process total counts
        if v is None:
            nulls = nulls + 1
            d[k] = False
        else:
            if k not in ["id", "publisher", "title"]:
                d[k] = True
        # data.update(d)
    data['missing_attributes'] = nulls
    data['total_attributes'] = count
    return data

def completeness_check():
    schema = get_json(BASELINE_SCHEMA)
    data_models = get_json(DATASETS_JSON)
    data = []
    header = []
    for dm in data_models['dataModels']:
        print("Processing:", dm['id'])
        d = {
            'id': dm['id'],
            'publisher': dm['publisher'],
            'title': dm['title']
        }
        dm.pop('dataClasses', None)
        s = copy.deepcopy(schema)
        s.update(dm)
        score = nullScore(s)
        score.update(d)
        header.extend(score.keys())
        data.append(score)
    return data, list(set(header))

def schema_validation_check():
    schema = get_json(DATASET_SCHEMA)
    data_models = get_json(DATASETS_JSON)
    data = []
    headers = []
    for dm in data_models['dataModels']:
        errors = validate_schema(schema, dm)
        d = {
            'id': dm['id'],
            'publisher': dm['publisher'],
            'title': dm['title'],
            'schema_error_count': len(errors),
            'errors': errors
        }
        headers.extend(d.keys())
        data.append(d)
    return data, list(set(headers))


def main():
    completeness_score, headers = completeness_check()
    export_json(completeness_score,'reports/completeness.json')
    export_csv(completeness_score, 'reports/completeness.csv', headers)
    schema_errors, headers = schema_validation_check()
    export_json(schema_errors,'reports/schema_errors.json')
    export_csv(schema_errors, 'reports/schema_errors.csv', headers)


if __name__ == "__main__":
    main()