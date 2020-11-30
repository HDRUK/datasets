#!/usr/bin/env python
# usage: update_readme.py
__author__ = "Susheel Varma"
__copyright__ = "Copyright (c) 2019-2020 Susheel Varma All Rights Reserved."
__email__ = "susheel.varma@hdruk.ac.uk"
__license__ = "Apache 2"

import os
import json
import requests

DATASETS_JSON = 'https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.json'

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

def cleanup_dataset_publishers(d):
    if d.get('publisher', None) is not None:
        publishers = d['publisher'].split(',')
        if len(publishers) > 1:
            print(d['id'])
        p = d.get('publisher', None)
        dp = {}
        p = p.lstrip().rstrip()
        if p.startswith('ALLIANCE > '):
            dp['name'] = p.split('ALLIANCE > ')[1]
            dp['type'] = "ALLIANCE"
        elif p.startswith('HUBS > '):
            dp['name'] = p.split('HUBS > ')[1]
            dp['type'] = "HUB"
        elif p.startswith('HUB > '):
            dp['name'] = p.split('HUB > ')[1]
            dp['type'] = "HUB"
        elif p.startswith('OTHER > '):
            dp['name'] = p.split('OTHER > ')[1]
            dp['type'] = "OTHER"
        else:
            dp['name'] = p
            dp['type'] = "OTHER"
        
        # if dp['name'] == "CYSTIC FIBROSIS":
        #     dp['name'] = "CYSTIC FIBROSIS TRUST"
        # if dp['name'] == "NHS Digital":
        #     dp['name'] = "NHS DIGITAL"
        # elif dp['name'] == "Oxford University Hospitals NHS Foundation Trust":
        #     dp['name'] = "OUH NHS"
        # elif dp['name'] == "Barts Health NHS Trust":
        #     dp['name'] = "BARTS HEALTH NHS TRUST"
        # elif dp['name'] == "BARTS":
        #     dp['name'] = "BARTS HEALTH NHS TRUST"
        # elif dp['name'] == "University of Bristol":
        #     dp['name'] = "UNIVERSITY OF BRISTOL"
        # elif dp['name'] == "SLaM":
        #     dp['name'] = "South London and Maudsley NHS Trust"
        # elif dp['name'].startswith("NIHR Health Informatics Collaborative"):
        #     dp['name'] = "NIHR HIC " + dp['name'].split("NIHR Health Informatics Collaborative ")[1]
        #     dp['name'] = dp['name'].upper()
    d['publisher'] = dp
    return d

def get_publishers(datasets):
    publishers = [d['publisher']['name'] for d in datasets]
    return sorted(list(set(publishers)))

def cleanup(datasets):
    datasets = datasets['dataModels']
    for d in datasets:
        d = cleanup_dataset_publishers(d)
    return datasets


def generate_readme(datasets, publishers):
    README_PREAMBLE = """[![Build](https://github.com/HDRUK/datasets/workflows/collect-datasets/badge.svg)](https://github.com/HDRUK/datasets/actions?query=workflow%3Acollect-datasets)

# HDR UK Gateway Datasets (Daily Extract)

This repo automatically collects the datasets published on the Gateway including all high-level metadata based the latest [specification](https://www.hdruk.ac.uk/wp-content/uploads/2019/12/MVP-Metadata-Specification_Final-v1.1.7.pdf).

### RAW Daily Extracts - [CSV](https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.csv) | [JSON](https://raw.githubusercontent.com/HDRUK/datasets/master/datasets.json)

---

"""
    with open('README.md', 'w') as readme:
        readme.write(README_PREAMBLE)
        readme.write("## HDR UK Datasets (%s)\n" % len(datasets))
        for p in publishers:
            filtered_datasets = [d for d in datasets if d['publisher']['name'] == p]
            readme.write("### %s (%s)\n" % (p, len(filtered_datasets)))
            for d in filtered_datasets:
                readme.write("- [{name}](https://web.www.healthdatagateway.org/dataset/{id})\n".format(name=d['label'], id=d['id']))
            readme.write('\n')


def main():
    datasets = get_json(DATASETS_JSON)
    datasets = cleanup(datasets)
    publishers = get_publishers(datasets)
    generate_readme(datasets, publishers)


if __name__ == "__main__":
    main()
