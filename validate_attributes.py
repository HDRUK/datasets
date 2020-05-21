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
import pandas as pd
import numpy as np


DATASET_SCHEMA = 'https://raw.githubusercontent.com/HMrz/datasets/MDW/schema/dataset.schema.json'
DATASETS_JSON = 'https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.json'
#DATASETS_CSV = 'https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.csv'
DATACLASSES = 'https://raw.githubusercontent.com/HDRUK/datasets/master/dataclasses.csv'
DATAELEMENTS = 'https://raw.githubusercontent.com/HDRUK/datasets/master/dataelements.csv'
TM_NAME_LEN = 2
TM_DESC_LEN = 6
DATATYPES = ''

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


def process_technical_metadata(data_classes):
    """

    @param data_classes:
    @return:
    """
    technical_md = {}
    technical_md['tableCount'] = len(data_classes)
    technical_md['tableNames'] = 0
    technical_md['tableDescriptions'] = 0
    technical_md['columnCount'] = 0
    technical_md['columnNames'] = 0
    technical_md['columnDescriptions'] = 0
    technical_md['dataTypes'] = 0
    technical_md['sensitive'] = 0
    technical_md['tables'] = []
    for dc in data_classes:
        table_md = {}
        table_md['table'] = dc.get('label', dc.get('id', '0'))
        table_md['columnCount'] = len(dc.get('dataElements', []))
        table_md['columnNames'] = 0
        table_md['columnDescriptions'] = 0
        table_md['dataTypes'] = 0
        if len(str(dc.get('label', ''))) >= TM_NAME_LEN:
            table_md['tableName'] = 1
            technical_md['tableNames'] += 1
        else:
            table_md['tableNames'] = 0
        if len(str(dc.get('description', ''))) >= TM_DESC_LEN:
            table_md['tableDescription'] = 1
            technical_md['tableDescriptions'] += 1
        else:
            table_md['tableDescription'] = 0

        for de in dc.get('dataElements', []):
            technical_md['columnCount'] += 1
            if len(str(de.get('label', ''))) >= TM_NAME_LEN:
                table_md['columnNames'] += 1
                technical_md['columnNames'] += 1
            if len(str(de.get('description', ''))) >= TM_DESC_LEN:
                table_md['columnDescriptions'] += 1
                technical_md['columnDescriptions'] += 1
            if len(list(de.get('dataType', []))) > 0:
                table_md['dataTypes'] += 1
                technical_md['dataTypes'] += 1
        technical_md['tables'].append(table_md)

    return technical_md


def import_datamodels(datamodel_uri):
    """
    @param dataset_uri: dataset URI or file path
    @return: all datasets as a list of JSON/dicts
    """
    data_models = get_json(datamodel_uri)

    models_with_metadata = 0
    for dm in data_models['dataModels']:
        if dm.get('dataClassesCount', 0) > 0:
            #dm['technicalMetaDataValidation'] = process_technical_metadata(dm.get('dataClasses', []))
            technicalMetaDataValidation = process_technical_metadata(dm.get('dataClasses', []))
            dm['technicalMetaDataValidation'] = technicalMetaDataValidation
            models_with_metadata += 1

    return data_models

def check_completeness(data_models):
    """

    @return:
    """
    # schema = get_json(BASELINE_SAMPLE)
    schema = generate_baseline_from_sections(METADATA_SECTIONS, REPORTING_LEVELS)
    data = []
    header = []
    for data_model in data_models['dataModels']:
        dm = copy.deepcopy(data_model)
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

def populated_attributes(d):
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
    # read in datasets
    data_models = import_datamodels(DATASETS_JSON)

    # Compile Metadata Completeness Score
    completeness_score, headers = check_completeness(data_models)
    # export_json(completeness_score,'reports/completeness.json')
    # export_csv(completeness_score, 'reports/completeness.csv', headers)

    # Complie Schema Validation Error Score
    schema_errors, headers = schema_validation_check()
    # export_json(schema_errors,'reports/schema_errors.json')
    # export_csv(schema_errors, 'reports/schema_errors.csv', headers)

    # Summarise Average Quality Score
    summary_score, headers = generate_quality_score()
    # export_json(summary_score,'reports/metadata_quality.json')
    # export_csv(summary_score, 'reports/metadata_quality.csv', headers)


if __name__ == "__main__":
    main()