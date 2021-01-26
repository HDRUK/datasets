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

def read_csv(filename):
  header = []
  data = []
  with open(filename, mode='r', encoding='utf-8-sig', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames
    for row in reader:
      data.append(row)
  return data, header

def update_utility_scores(quality_scores, utility_scores, headers=None):
    DATA = []
    for score in quality_scores:
        id = score['id']
        d  = dict.fromkeys(headers, "")
        us = [us for us in utility_scores if us['id'] == id]
        if len(us):
            d.update(us[0])
        d['id'] = score['id']
        d['publisher'] = score['publisher']
        d['title'] = score['title']
        d['metadata_richness'] = score['weighted_quality_rating']
        DATA.append(d)
    return DATA

def main():
    headers = []
    for score in metadata_quality_v1:
        v2_score = get_v2_quality_score(score['id'])
        if v2_score is not None:
            score['schema_version'] = v2_score['schema_version']
            score['weighted_quality_rating'] = v2_score['weighted_quality_rating']
            score['weighted_quality_score'] = v2_score['weighted_quality_score']
            score['weighted_completeness_percent'] = v2_score['weighted_completeness_percent']
            score['weighted_error_percent'] = v2_score['weighted_error_percent']
        headers = list(score.keys())
    
    print("Merged Metadata V1 Scores:", len([score for score in metadata_quality_v1 if score['schema_version'] == "1.1.7"]))
    print("Merged Metadata V2 Scores:", len([score for score in metadata_quality_v1 if score['schema_version'] == "2.0.1"]))
    print("Not Rated:", len([score for score in metadata_quality_v1 if score['weighted_quality_rating'] == "Bronze"]))
    print("Bronze:", len([score for score in metadata_quality_v1 if score['weighted_quality_rating'] == "Not Rated"]))
    print("Silver:", len([score for score in metadata_quality_v1 if score['weighted_quality_rating'] == "Silver"]))
    print("Gold:", len([score for score in metadata_quality_v1 if score['weighted_quality_rating'] == "Gold"]))
    print("Platinum:", len([score for score in metadata_quality_v1 if score['weighted_quality_rating'] == "Platinum"]))

    export_json(metadata_quality_v1, MERGED_METADATA_QUALITY_JSON)
    export_csv(metadata_quality_v1, MERGED_METADATA_QUALITY_CSV, headers)

    # Generate Data Utility Framework scores
    utility_scores, headers = read_csv('reports/data_utility.csv')
    utility_scores = update_utility_scores(metadata_quality_v1, utility_scores, headers)
    export_json(utility_scores,'reports/data_utility.json')
    export_csv(utility_scores, 'reports/data_utility.csv', headers)

if __name__ == "__main__":
    main()