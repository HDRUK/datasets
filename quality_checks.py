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
from validate_schema import get_json, validate_schema, \
                            generate_baseline_from_sections, generate_attribute_list, \
                            import_dm_tm, check_dm_completeness, check_attribute_validation, flatten_reporting_dict
from datasets import export_csv, export_json

DATASET_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/schema/dataset.schema.json'
BASELINE_SAMPLE = 'https://raw.githubusercontent.com/HDRUK/schemata/master/examples/dataset.sample.json'
DATASETS_JSON = "datasets.json"
WEIGHTS = "config/weights/weights.json"

METADATA_SECTIONS = {
    "A: Summary": ['identifier', 'title', 'abstract', 'publisher', 'contactPoint', 'accessRights', 'group'],
    "B: Business": ["description", "releaseDate", "accessRequestCost", "accessRequestDuration", "dataController",
                    "dataProcessor", "license", "derivedDatasets", "linkedDataset"],
    "C: Coverage & Detail": ["geographicCoverage", "periodicity", "datasetEndDate", "datasetStartDate",
                             "jurisdiction", "populationType", "statisticalPopulation", "ageBand",
                             "physicalSampleAvailability", "keywords"],
    "D: Format & Structure": ["conformsTo", "controlledVocabulary", "language", "format", "fileSize"],
    "E: Attribution": ["creator", "citations", "doi"],
    "F: Technical Metadata": ["dataClassesCount", "tableName", "tableDescription", "columnName", "columnDescription",
                              "dataType", "sensitive"],
    "G: Other Metadata": ["usageRestriction", "purpose", "source", "setting", "accessEnvironment",
                          "linkageOpportunity", "disambiguatingDescription"],
}

REPORTING_LEVELS = ["A: Summary", "B: Business", "C: Coverage & Detail",
                    "D: Format & Structure", "E: Attribution", "F: Technical Metadata"]

def nullScore(d):
    ''' CHECK WITH HEIKO: Do we need this anymore? '''
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
            dm.pop(attribute, None) # any attribute not in the schema, drop from the data model
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
    '''Reads the completeness and error json reports, and calculates the metadata quality scores.

    return summary_data, list(set(headers))
    '''

    # Generate completeness percent & weighted completeness percent
    scores = get_json('reports/attribute_completeness.json')
    completion_weightings = get_json(WEIGHTS)
    data = {}
    for s in scores:
        data[s['id']] = {
            'id': s['id'],
            'publisher': s['publisher'],
            'title': s['title']
        }
        c_score = round((s['filled_attributes'] / s['total_attributes']) * 100, 2) #completion score
        wc_score = round(attribute_weighted_score(s, completion_weightings) *100, 2) # weighted completion score
        data[s['id']]['completeness_percent'] = c_score
        data[s['id']]['weighted_completeness_percent'] = wc_score
    
    # Generate error percent and weighted error percent
    schema = get_json(DATASET_SCHEMA)
    total_attributes = len(list(schema['properties'].keys()))
    errors = get_json('reports/attribute_errors.json')
    error_weightings = get_json(WEIGHTS)
    for e in errors:
        e_score = round((e['attributes_with_errors'] / total_attributes) * 100, 2)
        we_score = round(attribute_weighted_score(e, error_weightings) * 100, 2)
        data[e['id']]['error_percent'] = e_score
        data[e['id']]['weighted_error_percent'] = we_score

    # Generate quality score, weighted quality score, quality score rating, and weighted quality score rating
    summary_data = []
    headers = []
    for id, d in data.items():
        avg_score = round(mean([data[id]['completeness_percent'], 100-data[id]['error_percent']]), 2)
        d['quality_score'] = avg_score
        d['quality_rating'] = quality_ratings(d['quality_score'])

        weighted_avg_score = round(mean([data[id]['weighted_completeness_percent'], 100-data[id]['weighted_error_percent']]), 2)
        d['weighted_quality_score'] = weighted_avg_score
        d['weighted_quality_rating'] = quality_ratings(d['weighted_quality_score'])

        headers.extend(d.keys())
        summary_data.append(d)

    return summary_data, list(set(headers))

def quality_ratings(s):
    '''Takes in a score and returns the resulting quality rating

    Keyword arguments:
    s -- score: a single score from the dictionary of metadata scores

    '''
    if s <= 50:
        return "Not Rated"
    elif s > 50 and s <= 70:
        return "Bronze"
    elif s > 70 and s <= 80:
        return "Silver"
    elif s > 80 and s <= 90:
        return "Gold"
    elif s > 90:
        return "Platinum"

def attribute_weighted_score(s, w):
    '''Applies the provided attribute weightings to the completeness and error score.

    Keyword arguments:
    s -- score: a dictionary of metadata scores
    w -- weights: a dictionary of metadata attributes and weights
    '''
    score = 0
    for section in REPORTING_LEVELS:
        section_score = s[section]
        for att_name, att_weights in w[section].items():
            score = score + (section_score[att_name]*att_weights)
    return score

def main():
    # Compile Metadata Completeness Score
    completeness_score, headers = completeness_check()
    export_json(completeness_score,'reports/completeness.json')
    export_csv(completeness_score, 'reports/completeness.csv', headers)

    # Compile Schema Validation Error Score
    schema_errors, headers = schema_validation_check()
    export_json(schema_errors,'reports/schema_errors.json')
    export_csv(schema_errors, 'reports/schema_errors.csv', headers)

    # Attribute level checks
    # read in datasets
    data_models = import_dm_tm(DATASETS_JSON)

    # Compile Attribute Completeness Score
    attribute_completeness_score = check_dm_completeness(data_models)
    export_json(attribute_completeness_score,'reports/attribute_completeness.json')
    csv_data, headers = flatten_reporting_dict(attribute_completeness_score)
    export_csv(csv_data, 'reports/attribute_completeness.csv', headers)

    # Compile Attribute Schema Validation Error Score
    attribute_schema_errors = check_attribute_validation(data_models)
    export_json(attribute_schema_errors,'reports/attribute_errors.json')
    csv_data, headers = flatten_reporting_dict(attribute_schema_errors)
    export_csv(csv_data, 'reports/attribute_errors.csv', headers)

    # Summarise Average Quality Score
    summary_score, headers = generate_quality_score()
    export_json(summary_score,'reports/metadata_quality.json')
    export_csv(summary_score, 'reports/metadata_quality.csv', headers)


if __name__ == "__main__":
    main()