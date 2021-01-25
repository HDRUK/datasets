# HDR UK Data Documentation Scores

Scripts are available to score the metadata completeness and errors, and calculate the metadata quality score.

## How to run these scripts

1. Run quality_checks.py.  This script takes the output of the daily extract (see above) and produces the outputs 
in the reports folder

## About the reports

**completeness.json & completeness.csv**  
Lists the number of missing attributes, per section of the metadata specification, for each dataset

**schema_errors.json & schema_errors.csv**  
Lists the metadata attributes that reported schema validation errors, and the associated error messages for each dataset

**attribute_completeness.json & attribute_completeness.csv**  
Lists the attributes of the metadata specification, and whether or not they have been completed 
(0: missing or 1: complete), for each dataset.
Calculates the total number of filled attributes and total attributes by dataset.

**attribute_errors.json & attribute_errors.csv**
Lists the attributes of the metadata specification, and whether or not the schema validation returned an error 
(0: no errors or 1: one or more errors), for each dataset.
Calculates the total number of attributes with errors and total attributes by dataset.

**metadata_quality.json & metadata_quality.csv**  
Lists each dataset, and the resulting scores.

## How scores are calculated

**Completeness Percent** = # filled fields / # total fields  
**Weighted Completeness Percent** = sum(weights of filled fields)

**Error Percent** = # fields with errors/ # total fields  
**Weighted Error Percent** = sum(weights of fields with errors)

**Quality score** = (completeness percent + (1-error percent))/2  
**Weighted Quality Score**** = (weighted completeness percent + (1-weight error percent))/2

**Quality Rating / Weighted Quality Rating:**  
Based on (weighted)/quality score 

| (Weighted)/Quality Score | Rating |
| --- | --- |
| < 66 | Not rated |
| >66 & <= 76 | Bronze |
| - >76 & <=86|  Silver |
| >86 | Gold |
|  | Platinum |

## How to modify weights

1. Download the config/weights/attribute_weights_config.xls file
2. Update the weights in the 'weightings configuration' tab in the excel file, by adjusting the number in the boosting column
3. Copy the data from the TSV tab of the spreadsheet, and paste it over the existing data in the config/weights/weightings_config.tsv file in the directory
4. Run the "config/weights/create_weightings_json.py" script.  This will overwrite the data in the config/weights/weights.json file

