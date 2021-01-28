# HDR UK Data Documentation Scores

Scripts are available to score the metadata completeness and errors, and calculate the metadata quality score.

## How to run these scripts

1. Run `quality_checks.py` to generate v1 metadata quality scores - This script takes the output of the daily extract and produces the outputs in the `reports/v1.1.7` folder
2. Run `quality_checks_v2.py` to generate v2 metadata quality scores - This script takes the output of the daily extract and produces the outputs in the `reports/latest` folder
3. Run `merge_quality_scores.py` to merge the v1 and v2 metadata quality scores - This script takes the output of v1 and v2 quality scores and produces the outputs in the `reports/` folder. It also updates the data_utility scores

## About the reports

**`completeness.{json,csv}`**  
Lists the number of missing attributes, per section of the metadata specification, for each dataset

**`schema_errors.{json,csv}`**  
Lists the metadata attributes that reported schema validation errors, and the associated error messages for each dataset

**`attribute_completeness.{json,csv}`**  
Lists the attributes of the metadata specification, and whether or not they have been completed 
(0: missing or 1: complete), for each dataset.
Calculates the total number of filled attributes and total attributes by dataset.

**`attribute_errors.{json,csv}`**
Lists the attributes of the metadata specification, and whether or not the schema validation returned an error 
(0: no errors or 1: one or more errors), for each dataset.
Calculates the total number of attributes with errors and total attributes by dataset.

**`metadata_quality.{json,csv}`**  
Lists each dataset, and the resulting scores.

**[`metadata_score_breakdown_v2.xlsx`](https://github.com/HDRUK/datasets/blob/master/reports/metadata_score_breakdown_v2.xlsx)**    
Lists the completeness and error percentages of all v2 datasets showing how their percentage scores are derived. Details of field errors can be found for a particular dataset can be located using the value ref column. For example, details of the dataset with ref value "data-model-0001" can be found by clicking the cell, directing you to the corresponding worksheet.

## How scores are calculated

**Completeness Percent** = # filled fields / # total fields  
**Weighted Completeness Percent** = sum(weights of filled fields)

**Error Percent** = # fields with errors/ # total fields  
**Weighted Error Percent** = sum(weights of fields with errors)

**Quality score** = (completeness percent + (1-error percent))/2  
**Weighted Quality Score**** = (weighted completeness percent + (1-weight error percent))/2

**Quality Rating / Weighted Quality Rating:**  
Based on (weighted)/quality score - see `config/weights/medallions.v2.json`

| (Weighted)/Quality Score | Rating |
| --- | --- |
| < 60 | Not rated |
| >60 & <= 70 | Bronze |
| >70 & <=80|  Silver |
| >80 & <>=90 | Gold |
| >90 | Platinum |

## How to modify weights

#### For V1
1. Download the config/weights/attribute_weights_config.xls file
2. Update the weights in the 'weightings configuration' tab in the excel file, by adjusting the number in the boosting column
3. Copy the data from the TSV tab of the spreadsheet, and paste it over the existing data in the config/weights/weightings_config.tsv file in the directory
4. Run the "config/weights/create_weightings_json.py" script.  This will overwrite the data in the config/weights/weights.json file

#### For V2
1. Modify the weights directly `config/latest/weights.v2.json`
