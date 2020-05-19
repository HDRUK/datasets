#!/usr/bin/env python
# usage: completeness_check.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import copy
import math
from statistics import mean, stdev
import csv
import json
import urllib
import requests
from pprint import pprint
from validate_schema import get_json, validate_schema, generate_baseline_from_sections, generate_attribute_list
from datasets import export_csv, export_json

DATASET_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/schema/dataset.schema.json'
BASELINE_SAMPLE = 'https://raw.githubusercontent.com/HDRUK/schemata/master/examples/dataset.sample.json'
DATASETS_JSON = "datasets.json"

METADATA_SECTIONS = {
    "A: Summary": ['identifier', 'title', 'abstract', 'publisher', 'contactPoint', 'accessRights', 'group'],
    "B: Business": ["description", "releaseDate", "accessRequestCost", "accessRequestDuration", "dataController",
                    "dataProcessor", "license", "derivedDatasets", "linkedDataset"],
    "C: Coverage & Detail": ["geographicCoverage", "periodicity", "datasetEndDate", "datasetStartDate",
                             "jurisdiction", "populationType", "statisticalPopulation", "ageBand",
                             "physcicalSampleAvailability", "keywords"],
    "D: Format & Structure": ["conformsTo", "controlledVocabulary", "language", "format", "fileSize"],
    "E: Attribution": ["creator", "citations", "doi"],
    "F: Technical Metadata": ["dataClassesCount"],
    "G: Other Metadata": ["usageResrictions", "purpose", "source", "setting", "accessEnvironment",
                          "linkageOpportunity", "disabmiguatingDescription"],
}

REPORTING_LEVELS = ["A: Summary", "B: Business", "C: Coverage & Detail",
                    "D: Format & Structure", "E: Attribution", "F: Technical Metadata"]

def nullScore(d):
    count = 0
    nulls = 0
    data = { f"{attr_level} Missing Count": 0 for attr_level in REPORTING_LEVELS}
    reporting_dict = {key: METADATA_SECTIONS.get(key, None) for key in REPORTING_LEVELS}
    for k,v in d.items():
        count = count + 1
        for section, attributes in reporting_dict.items():
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
    # schema = get_json(BASELINE_SAMPLE)
    schema = generate_baseline_from_sections(METADATA_SECTIONS, REPORTING_LEVELS)
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
        for attribute in (set(dm.keys()) - set(schema.keys())):
            dm.pop(attribute, None)
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
    validation_attributes = set(generate_attribute_list(METADATA_SECTIONS, REPORTING_LEVELS))
    data = []
    headers = []
    for dm in data_models['dataModels']:
        dm_validate = copy.deepcopy(dm)
        for attribute in (set(dm_validate.keys()) - validation_attributes):
            dm_validate.pop(attribute, None)
        errors = validate_schema(schema, dm_validate)
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

def generate_quality_score():
    # TODO: Differentiate between section (A-G) completeness by weighting them
    scores = get_json('reports/completeness.json')
    data = {}
    for s in scores:
        data[s['id']] = {
            'id': s['id'],
            'publisher': s['publisher'],
            'title': s['title']
        }
        c_score = round((s['missing_attributes'] / s['total_attributes']) * 100, 2)
        data[s['id']]['missingness_percent'] = c_score
    
    # TODO: Differentiate between error classes (required vs format) by weighting them
    schema = get_json(DATASET_SCHEMA)
    total_attributes = len(list(schema['properties'].keys()))
    errors = get_json('reports/schema_errors.json')
    for e in errors:
        e_score = round((e['schema_error_count'] / total_attributes) * 100, 2)
        data[e['id']]['error_percent'] = e_score
    
    # # Calculate average quality score (lower the better)
    # quality_scores = [100 - round(mean([v['missingness_percent'], v['error_percent']]),2) for k, v in data.items()]
    # mean_quality_score = round(mean(quality_scores))
    # stdev_quality_score = round(stdev(quality_scores))
    # print("MEAN:", mean_quality_score)
    # print("STDEV:", stdev_quality_score)

    summary_data = []
    headers = []
    for id, d in data.items():
        avg_score = round(mean([data[id]['missingness_percent'], data[id]['error_percent']]), 2)
        d['quality_score'] = round(100 - avg_score, 2)
        if d['quality_score'] <= 50:
            d['quality_rating'] = "Not Rated"
        elif d['quality_score'] > 50 and d['quality_score'] <= 70:
            d['quality_rating'] = "Bronze"
        elif d['quality_score'] > 70 and d['quality_score'] <= 80:
            d['quality_rating'] = "Silver"
        elif d['quality_score'] > 80 and d['quality_score'] <= 90:
            d['quality_rating'] = "Gold"
        elif d['quality_score'] > 90:
            d['quality_rating'] = "Platinum"
        headers.extend(d.keys())
        summary_data.append(d)
    return summary_data, list(set(headers))


def main():
    # Compile Metadata Completeness Score
    completeness_score, headers = completeness_check()
    export_json(completeness_score,'reports/completeness.json')
    export_csv(completeness_score, 'reports/completeness.csv', headers)

    # Complie Schema Validation Error Score
    schema_errors, headers = schema_validation_check()
    export_json(schema_errors,'reports/schema_errors.json')
    export_csv(schema_errors, 'reports/schema_errors.csv', headers)

    # Summarise Average Quality Score
    summary_score, headers = generate_quality_score()
    export_json(summary_score,'reports/metadata_quality.json')
    export_csv(summary_score, 'reports/metadata_quality.csv', headers)


if __name__ == "__main__":
    main()