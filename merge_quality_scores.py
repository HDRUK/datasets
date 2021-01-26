import os
import csv
import json
import requests

METADATA_QUALITY_V1_JSON = 'reports/v1.1.7/metadata_quality.json'
METADATA_QUALITY_V2_JSON = 'reports/latest/metadata_quality.v2.json'
MERGED_METADATA_QUALITY_JSON = 'reports/metadata_quality.json'
MERGED_METADATA_QUALITY_CSV = 'reports/metadata_quality.csv'

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

metadata_quality_v1 = get_json(METADATA_QUALITY_V1_JSON)
metadata_quality_v2 = get_json(METADATA_QUALITY_V2_JSON)

print("Metadata V1 Scores:", len(metadata_quality_v1))
print("Metadata V2 Scores:", len(metadata_quality_v2))

def get_v2_quality_score(id):
    for score in metadata_quality_v2:
        if score['id'] == id:
            return score
    return None

def export_json(data, filename, indent=2):
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=indent)

def export_csv(data, filename, header):
  with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)

def main():
    headers = []
    for score in metadata_quality_v1:
        v2_score = get_v2_quality_score(score['id'])
        if v2_score is not None:
            score['@schema.version'] = v2_score['@schema.version']
            score['weighted_quality_rating'] = v2_score['weighted_quality_rating']
            score['weighted_quality_score'] = v2_score['weighted_quality_score']
            score['weighted_completeness_percent'] = v2_score['weighted_completeness_percent']
            score['weighted_error_percent'] = v2_score['weighted_error_percent']
        headers = list(score.keys())
    
    print("Merged Metadata V1 Scores:", len([score for score in metadata_quality_v1 if score['@schema.version'] == "1.1.7"]))
    print("Merged Metadata V2 Scores:", len([score for score in metadata_quality_v1 if score['@schema.version'] == "2.0.1"]))

    export_json(metadata_quality_v1, MERGED_METADATA_QUALITY_JSON)
    export_csv(metadata_quality_v1, MERGED_METADATA_QUALITY_CSV, headers)
    

if __name__ == "__main__":
    main()