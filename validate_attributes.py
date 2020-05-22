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
import copy
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
                    "dataProcessor", "license", "usageRestriction", "derivedDatasets", "linkedDataset"],
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


def init_reporting_dict(metadata_sections = METADATA_SECTIONS, reporting_levels = REPORTING_LEVELS, txt='attribute_reporting'):
    reporting_dict = {}
    attribute_count = 0
    for level in reporting_levels:
        level_dict = {attr: 0 for attr in metadata_sections[level]}
        level_dict[txt] = 0
        level_dict['total_attributes'] = len(metadata_sections[level])
        attribute_count += len(metadata_sections[level])
        reporting_dict[level] = level_dict

    reporting_dict[txt] = 0
    reporting_dict['total_attributes'] = attribute_count

    return reporting_dict


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


def compute_tech_md_completeness(data_model):
    """

    @param data_model:
    @return:
    """
    if data_model.get('dataClassesCount', 0) < 1:
        return
    tm = data_model.get('technicalMetaDataValidation', {})
    data_model['tableName'] = 1 if tm.get('tableNames', 0) > 0 else 0
    data_model['tableDescription'] = 1 if tm.get('tableDescriptions', 0) > 0 else 0
    data_model['columnName'] = 1 if tm.get('columnNames', 0) > 0 else 0
    data_model['columnDescription'] = 1 if tm.get('columnDescriptions', 0) > 0 else 0
    data_model['dataType'] = 1 if tm.get('dataTypes', 0) > 0 else 0
    data_model['sensitive'] = None


def compute_tech_md_validation(data_model):
    """

    @param data_model:
    @return:
    """
    if data_model.get('dataClassesCount', 0) < 1:
        return
    tm = data_model.get('technicalMetaDataValidation', {})
    table_count = tm.get('tableCount', 0)
    column_count = tm.get('columnCount', 0)
    data_model['tableName'] = 0 if tm.get('tableNames', 0) == table_count else 1
    data_model['tableDescription'] = 0 if tm.get('tableDescriptions', 0) == table_count else 1
    data_model['columnName'] = 0 if tm.get('columnNames', 0) == column_count else 1
    data_model['columnDescription'] = 0 if tm.get('columnDescriptions', 0) == column_count else 1
    data_model['dataType'] = 0 if tm.get('dataTypes', 0) == column_count else 1
    data_model['sensitive'] = 1


def check_completeness(data_models):
    """

    @return:
    """
    # schema = get_json(BASELINE_SAMPLE)
    schema = generate_baseline_from_sections()
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
        compute_tech_md_completeness(dm)
        for attribute in (set(dm.keys()) - set(schema.keys())):
            dm.pop(attribute, None) # any attribute not in the schema, drop from the data model
        s = copy.deepcopy(schema)
        s.update(dm)
        score = attribute_completeness(s)
        d.update(score)
        header.extend(d.keys())
        data.append(d)
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

def attribute_completeness(d, metadata_sections = METADATA_SECTIONS, reporting_levels = REPORTING_LEVELS):
    reporting_dict = init_reporting_dict(metadata_sections=metadata_sections,
                                         reporting_levels=reporting_levels,
                                         txt='filled_attributes')
    total_populated = 0
    for level in reporting_levels:
        level_total = 0
        for k in reporting_dict[level].keys():
            if 'filled_attributes' == k:
                continue
            elif 'total_attributes' == k:
                continue
            elif "dataClassesCount" == k:
                reporting_dict[level][k] = 0 if d.get(k, 0) == 0 else 1
                total_populated += reporting_dict[level][k]
                level_total += reporting_dict[level][k]
            else:
                reporting_dict[level][k] = 1 if d.get(k, None) is not None else 0
                total_populated += reporting_dict[level][k]
                level_total += reporting_dict[level][k]
        reporting_dict[level]['filled_attributes'] = level_total
    reporting_dict['filled_attributes'] = total_populated
    return reporting_dict

def generate_baseline_from_sections(metadata_sections=METADATA_SECTIONS, metadata_levels=None):
    '''
    generate the baseline schema from METADATA_SECTIONS, a dictionary of dictionaries

    '''
    baseline_dict = {}
    raw_attributes = generate_attribute_list(metadata_sections, metadata_levels=metadata_levels, add_id=True)

    baseline_dict = {attribute: None for attribute in raw_attributes}

    return baseline_dict

def generate_attribute_list(metadata_sections, metadata_levels=None, add_id=True):

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


def validate_schema(schema, data_model):
    schema = get_json(schema)

    v = Draft7Validator(schema, format_checker=draft7_format_checker)
    errors = sorted(v.iter_errors(data_model), key=lambda e: e.path)
    print(data_model['id'], ": Number of validation errors = ", len(errors))
    err = {}
    for error in errors:

        if len(list(error.path)):
            attribute = list(error.path)[0]
            err.setdefault(attribute, []).append(error.message)
            print(attribute, error.message, sep=": ")
            # err['attribute'] = list(error.path)[0]
            # err['message'] = ": ".join([err['attribute'], error.message])
            # for suberror in sorted(error.context, key=lambda e: e.schema_path):
            #     print("    ", list(suberror.schema_path)[1], ": ", suberror.message)
            #     err['suberrors'] = "    " + list(suberror.schema_path)[1] + ": " + suberror.message
        else:
            print(error.message)
            attribute = re.findall(r"(.*?)'", error.message)[1]
            err.setdefault(attribute,[]).append(error.message)
            # err['attribute'] = re.findall(r"(.*?)'", error.message)[1]
            # err['message'] = error.message
    return err


def generate_baseline_from_sections(metadata_sections=METADATA_SECTIONS, metadata_levels=REPORTING_LEVELS, add_id=True):
    '''
    generate the baseline schema from METADATA_SECTIONS, a dictionary of dictionaries

    '''
    baseline_dict = {}
    raw_attributes = generate_attribute_list(metadata_sections, metadata_levels, add_id)

    baseline_dict = {attribute: None for attribute in raw_attributes}

    return baseline_dict


def generate_attribute_list(metadata_sections=METADATA_SECTIONS, metadata_levels=REPORTING_LEVELS, add_id=True):
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

def schema_validation_check(data_models, metadata_sections = METADATA_SECTIONS, reporting_levels = REPORTING_LEVELS):
    schema = get_json(DATASET_SCHEMA)
    reporting_dict = init_reporting_dict(metadata_sections=metadata_sections,
                                         reporting_levels=reporting_levels,
                                         txt='attributes_with_errors')
    validation_attributes = set(generate_attribute_list(metadata_sections, reporting_levels))
    data = []
    headers = []
    for dm in data_models['dataModels']:
        total_errors, level_errors = 0, 0
        dm_validate = copy.deepcopy(dm)
        compute_tech_md_validation(dm_validate)
        for attribute in (set(dm_validate.keys()) - validation_attributes):
            dm_validate.pop(attribute, None)
        errors = validate_schema(schema, dm_validate)
        d = {
            'id': dm['id'],
            'publisher': dm['publisher'],
            'title': dm['title'],
        }
        total_errors = 0
        for level in reporting_levels:
            level_errors = 0
            if "F: Technical Metadata" == level:
                for k in reporting_dict[level].keys():
                    if 'dataClassesCount' == k:
                        i = dm_validate.get(k, 0)
                        reporting_dict[level][k] = int( 1 - (i>1))
                    elif 'attributes_with_errors' == k:
                        continue
                    elif 'total_attributes' == k:
                        continue
                    else:
                        reporting_dict[level][k] = dm_validate.get(k, 0)
                    level_errors += reporting_dict[level][k]
                    total_errors += reporting_dict[level][k]
            else:
                for k in reporting_dict[level].keys():
                    if 'attributes_with_errors' == k:
                        continue
                    elif 'total_attributes' == k:
                        continue
                    else:
                        if k in errors:
                            zzz_debug = errors[k]
                            reporting_dict[level][k] = 1
                            level_errors += 1
                            total_errors += 1
            reporting_dict[level]['attributes_with_errors'] = level_errors
        d.update(reporting_dict)
        d['attributes_with_errors'] = total_errors
        data.append(d)
    return data, headers


def export_json(data, filename, indent=2):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=indent)


def main():
    # read in datasets
    data_models = import_datamodels(DATASETS_JSON)

    # Compile Metadata Completeness Score
    completeness_score, headers = check_completeness(data_models)
    export_json(completeness_score,'reports/attribute_completeness.json')
    # export_csv(completeness_score, 'reports/completeness.csv', headers)

    # Complie Schema Validation Error Score
    schema_errors, headers = schema_validation_check(data_models)
    export_json(schema_errors,'reports/attribute_errors.json')
    # export_csv(schema_errors, 'reports/schema_errors.csv', headers)

    # Summarise Average Quality Score
    # summary_score, headers = generate_quality_score()
    # export_json(summary_score,'reports/metadata_quality.data_model')
    # export_csv(summary_score, 'reports/metadata_quality.csv', headers)


if __name__ == "__main__":
    main()
    print(f"\n\n\nDONE")