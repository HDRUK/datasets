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

<a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{150}&space;\\&space;\textbf{Completeness&space;%}&space;=&space;\frac{\text{\&hash;&space;filled&space;fields}}{\text{\&hash;&space;total&space;fields}}&space;\\&space;\textbf{Weighted&space;Completeness&space;%}&space;=&space;\sum{\text{(weights&space;of&space;filled&space;fields)}}&space;\\&space;\\&space;\\&space;\textbf{Error&space;%}&space;=&space;\frac{\text{\&hash;&space;fields&space;with&space;errors}}{\text{\&hash;&space;total&space;fields}}&space;\\&space;\textbf{Weighted&space;Error&space;%}&space;=&space;\sum{\text{(weights&space;of&space;fields&space;with&space;errors)}}&space;\\&space;\\&space;\\&space;\textbf{Quality&space;Score}&space;=&space;\frac{\text{(Completeness&space;%&space;&plus;&space;(1&space;-&space;Error&space;%)}}{2}&space;\\&space;\textbf{Weighted&space;Quality&space;Score}&space;=&space;\frac{\text{(Weighted&space;Completeness&space;%&space;&plus;&space;(1&space;-&space;Weighted&space;Error&space;%)}}{2}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;\\&space;\textbf{Completeness&space;%}&space;=&space;\frac{\text{\&hash;&space;filled&space;fields}}{\text{\&hash;&space;total&space;fields}}&space;\\&space;\textbf{Weighted&space;Completeness&space;%}&space;=&space;\sum{\text{(weights&space;of&space;filled&space;fields)}}&space;\\&space;\\&space;\\&space;\textbf{Error&space;%}&space;=&space;\frac{\text{\&hash;&space;fields&space;with&space;errors}}{\text{\&hash;&space;total&space;fields}}&space;\\&space;\textbf{Weighted&space;Error&space;%}&space;=&space;\sum{\text{(weights&space;of&space;fields&space;with&space;errors)}}&space;\\&space;\\&space;\\&space;\textbf{Quality&space;Score}&space;=&space;\frac{\text{(Completeness&space;%&space;&plus;&space;(1&space;-&space;Error&space;%)}}{2}&space;\\&space;\textbf{Weighted&space;Quality&space;Score}&space;=&space;\frac{\text{(Weighted&space;Completeness&space;%&space;&plus;&space;(1&space;-&space;Weighted&space;Error&space;%)}}{2}" title="\\ \textbf{Completeness %} = \frac{\text{\# filled fields}}{\text{\# total fields}} \\ \textbf{Weighted Completeness %} = \sum{\text{(weights of filled fields)}} \\ \\ \\ \textbf{Error %} = \frac{\text{\# fields with errors}}{\text{\# total fields}} \\ \textbf{Weighted Error %} = \sum{\text{(weights of fields with errors)}} \\ \\ \\ \textbf{Quality Score} = \frac{\text{(Completeness % + (1 - Error %)}}{2} \\ \textbf{Weighted Quality Score} = \frac{\text{(Weighted Completeness % + (1 - Weighted Error %)}}{2}" /></a>

**Quality Rating / Weighted Quality Rating:**  
Based on (weighted)/quality score 



| (Weighted)/Quality Score | Rating |
| --- | --- |
| <a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;\leq50" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;\leq50" title="\leq50" /></a> | Not rated |
| <a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;>50&space;\text{&space;\&&space;}&space;\leq70" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;>50&space;\text{&space;\&&space;}&space;\leq70" title=">50 \text{ \& } \leq70" /></a> | Bronze |
| <a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;>70&space;\text{&space;\&&space;}&space;\leq80" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;>70&space;\text{&space;\&&space;}&space;\leq80" title=">70 \text{ \& } \leq80" /></a>|  Silver |
| <a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;>80&space;\text{&space;\&&space;}&space;\leq90" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;>80&space;\text{&space;\&&space;}&space;\leq90" title=">80 \text{ \& } \leq90" /></a> | Gold |
| <a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;>90" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{120}&space;>90" title=">90" /></a> | Platinum |

## How to modify weights

1. Download the config/weights/attribute_weights_config.xls file
2. Update the weights in the 'weightings configuration' tab in the excel file, by adjusting the number in the boosting column
3. Copy the data from the TSV tab of the spreadsheet, and paste it over the existing data in the config/weights/weightings_config.tsv file in the directory
4. Run the "config/weights/create_weightings_json.py" script.  This will overwrite the data in the config/weights/weights.json file

