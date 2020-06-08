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
import copy
from jsonschema import validate, Draft7Validator, FormatChecker, draft7_format_checker

DATASET_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/schema/dataset.schema.json'
DATASETS_JSON = 'https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.json'
BASELINE_SCHEMA = 'https://raw.githubusercontent.com/HDRUK/schemata/master/examples/dataset.sample.json'

REPORTING_ATTRIBUTES = {
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

TM_NAME_LEN = 2
TM_DESC_LEN = 6

REPORTING_ATTRIBUTES = {
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


def export_json(data, filename, indent=2):
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=indent)


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


def validate_attribute_schema(schema, data_model):
    """ validate each attribute against JSON schema
    @param schema: JSON validation schema
    @param data_model: uploaded data model
    @return: dictionary with all schema errors
    """
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


def generate_baseline_from_sections(metadata_sections, metadata_levels=None):
    '''
    generate the baseline schema from METADATA_SECTIONS, a dictionary of dictionaries
    @param metadata_sections: reporting levels and attributes
    @param metadata_levels: list of reporting levels
    @return: dictionary with reporting levels and reporting attributes
    '''
    baseline_dict = {}
    raw_attributes = generate_attribute_list(metadata_sections, metadata_levels=metadata_levels, add_id=True)

    baseline_dict = {attribute: None for attribute in raw_attributes}

    return baseline_dict


def generate_attribute_list(metadata_sections=REPORTING_ATTRIBUTES, metadata_levels=REPORTING_LEVELS, add_id=True):
    '''
    Collect all attributes from all attribute levels
    @param metadata_sections: reporting levels and attributes
    @param metadata_levels: list of reporting levels
    @param add_id: add id field to list
    @return: list of all reporting attributes
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


def import_dm_tm(datamodel_uri):
    """
    Import data-models and process technical metadata
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


def process_technical_metadata(data_classes):
    """
    Process technical metadata for an uploaded data-model
    @param data_classes: uploaded data-classes for a data-model
    @return: dictionary containing technical metadata
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


def check_attribute_completeness(dm, metadata_sections=REPORTING_ATTRIBUTES, reporting_levels=REPORTING_LEVELS):
    """
    Count completed (i.e. filled or populated) data-model attributes
    @param dm: data-model
    @param metadata_sections: reporting attributes and levels
    @param reporting_levels: reporting levels
    @return: dictionary with completeness for each attribute and level
    """
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
                reporting_dict[level][k] = 0 if dm.get(k, 0) == 0 else 1
                total_populated += reporting_dict[level][k]
                level_total += reporting_dict[level][k]
            else:
                reporting_dict[level][k] = 1 if dm.get(k, None) is not None else 0
                total_populated += reporting_dict[level][k]
                level_total += reporting_dict[level][k]
        reporting_dict[level]['filled_attributes'] = level_total
    reporting_dict['filled_attributes'] = total_populated
    return reporting_dict


def check_dm_completeness(data_models):
    """
    @return:
    """
    # schema = get_json(BASELINE_SAMPLE)
    schema = generate_baseline_from_sections(REPORTING_ATTRIBUTES, REPORTING_LEVELS, True)
    data = []
    for data_model in data_models['dataModels']:
        dm = copy.deepcopy(data_model)
        print("Processing:", dm['id'])
        d = {
            'id': dm.get('id',None),
            'publisher': dm.get('publisher',None),
            'title': dm.get('title',None)
        }
        compute_tech_md_completeness(dm)
        for attribute in (set(dm.keys()) - set(schema.keys())):
            dm.pop(attribute, None) # any attribute not in the schema, drop from the data model
        s = copy.deepcopy(schema)
        s.update(dm)
        score = check_attribute_completeness(s)
        d.update(score)
        data.append(d)
    return data


def check_attribute_validation(data_models, metadata_sections=REPORTING_ATTRIBUTES, reporting_levels=REPORTING_LEVELS):
    """
    Generate dictionary that validates each attribute against the JSON validation schema
    @param data_models: data-models for validation
    @param metadata_sections: reporting levels and attributes
    @param reporting_levels: reporting attributes
    @return: dictionary with validation for each attribute
    """
    schema = get_json(DATASET_SCHEMA)
    validation_attributes = set(generate_attribute_list(metadata_sections, reporting_levels))
    data = []
    for dm in data_models['dataModels']:
        total_errors, level_errors = 0, 0
        dm_validate = copy.deepcopy(dm)
        compute_tech_md_validation(dm_validate)
        for attribute in (set(dm_validate.keys()) - validation_attributes):
            dm_validate.pop(attribute, None)
        errors = validate_attribute_schema(schema, dm_validate)
        d = {
            'id': dm.get('id',None),
            'publisher': dm.get('publisher',None),
            'title': dm.get('title',None)
        }
        reporting_dict = init_reporting_dict(metadata_sections=metadata_sections,
                                             reporting_levels=reporting_levels,
                                             txt='attributes_with_errors')
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
    return data


def generate_baseline_from_sections(metadata_sections=REPORTING_ATTRIBUTES, metadata_levels=REPORTING_LEVELS, add_id=True):
    '''
    generate the baseline schema from REPORTING_ATTRIBUTES, a dictionary of dictionaries
    @param metadata_sections: reporting levels and attributes
    @param metadata_levels: reporting attributes
    @param add_id: add ID field to levels
    @return: dictionary including all attributes

    '''
    baseline_dict = {}
    raw_attributes = generate_attribute_list(metadata_sections, metadata_levels, add_id)

    baseline_dict = {attribute: None for attribute in raw_attributes}

    return baseline_dict


def compute_tech_md_completeness(data_model):
    """
    check if technical metadata is complete
    @param data_model: uploaded data-model
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


def init_reporting_dict(metadata_sections = REPORTING_ATTRIBUTES, reporting_levels = REPORTING_LEVELS, txt='attribute_reporting'):
    """
    Initialise dictionary that mirrors reporting levels and attributes
    @param metadata_sections: reporting levels and attributes
    @param reporting_levels: reporting attributes
    @param txt: name for aggregation field
    @return: reporting attribute dictionary
    """
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


def compute_tech_md_validation(data_model):
    """
    validate technical meta-data
    @param data_model: uploaded data-model
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


def flatten_reporting_dict(data_models):
    """
    flatten nested reporting dictionary for export to .csv
    @param data_models: nested dictionary
    @return: flat dictionary
    """
    headers = []
    data = []

    for dm in data_models:
        flat_dm = {}
        for k, v in dm.items():
            if isinstance(v, dict):
                i = 0
                for nk, nv in v.items():  # nested key, value
                    if i == 0:
                        fk = f"{k}, {nk}"  # flat key
                        # i += 1
                    else:
                        fk = f"{k[:2]} {nk}"
                    flat_dm[fk] = nv
                    if not fk in headers:
                        headers.append(fk)
            else:
                flat_dm[k] = v
                if not k in headers:
                    headers.append(k)
        data.append(flat_dm)

    return data, headers


def main():
    validate_schema(DATASET_SCHEMA, BASELINE_SCHEMA)

    # read in datasets
    data_models = import_dm_tm(DATASETS_JSON)

    # Compile Metadata Completeness Score
    attribute_completeness_score = check_dm_completeness(data_models)
    export_json(attribute_completeness_score,'reports/attribute_completeness.json')
    # export_json(attribute_completeness_score,'reports/attribute_completeness.json')
    data, headers = flatten_reporting_dict(attribute_completeness_score)

    # Compile Schema Validation Error Score
    schema_errors = check_attribute_validation(data_models)
    export_json(schema_errors, 'reports/attribute_errors.json')


if __name__ == "__main__":
    main()
