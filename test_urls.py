import requests
import re
import time
import pandas as pd
from functools import reduce

# URL for the Innovation Gateway API
API_URL = "https://api.www.healthdatagateway.org/api/v2/datasets"

# Regex pattern for finding URLs in strings
URL_REGEX = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

# Fields which contain URLs in the dataset metadata
FIELDS = [
    'name',
    'datasetv2.summary.publisher.name',
    'datasetv2.documentation.description',
    'datasetv2.documentation.associatedMedia',
    'datasetv2.accessibility.usage.investigations',
    'datasetv2.accessibility.access.accessRights',
    'datasetv2.accessibility.access.accessService',
    'datasetv2.accessibility.access.accessRequestCost',
    'datasetv2.enrichmentAndLinkage.tools'
]

def get_dataset_objects(api_url, params:dict = {}):
    '''
    Retrieves active dataset objects from the Gateway API.
    '''

    # Default parameters:
    params['activeflag'] = 'active'
    params['limit'] = 100

    # Datasets will be added to this list in batches of 100
    out = []

    # Loop through the API pages:
    for i in range(1, 100):
        params['page'] = i
        r = requests.get(url = api_url, params = params)
        data = r.json()['datasets']

        # Add the datasets from the page to the output list:
        out.extend(data)

        # Wait 1 second before requesting the next page:
        time.sleep(1)

        # Stop when there are less than 100 datasets on the page (i.e. the last page):
        if len(data) < 100:
            break

    return out

def recursive_get(d, path):
    return reduce(lambda d, k: d.get(k, {}), path, d)

def reduce_dictionary(d, keys):
    return {k: recursive_get(d, k.split('.')) for k in keys}

def url_test(url):
    try:
        status_code = requests.get(url, timeout=10.0).status_code
        return status_code
    except requests.Timeout:
        return 'Timeout' 
    except:
        return 'Error'

def report(dataset, regex=URL_REGEX):
    compiled_regex = re.compile(regex)

    out = {
        'dataset': dataset['name'], 
        'publisher': dataset['datasetv2.summary.publisher.name'],
        'urls': []
        }
    
    for k, v in dataset.items():

        if isinstance(v, str):
            urls = re.findall(regex, v)
        elif isinstance(v, list):
            urls = [url for url in v if compiled_regex.match(str(url))]
        else:
            urls = []

        out['urls'].extend(
            [{'url': url, 'location': k, 'status':url_test(url)} for url in urls]
            )
        
    return out

def build_df(report):
    df = pd.json_normalize(report)

    # Explode the urls column into a new row for each URL
    df = df.explode('urls')
    df = df.dropna(subset=['urls'])
    df = df.reset_index(drop=True)

    # Convert the urls column to a separate columns
    df = df.join(pd.json_normalize(df['urls'])).drop('urls', axis=1).reset_index(drop=True)

    return df

def main() -> None:
    # Retrieve the dataset objects from the API
    print(f"Querying {API_URL}...")
    data = get_dataset_objects(API_URL, params = {'fields':','.join(FIELDS)})
    print(f"Retrieved {len(data)} dataset objects from gateway API.")

    # Reduce the size of the dataset objects
    print("Reducing object sizes...")
    data = [reduce_dictionary(d, FIELDS) for d in data]
    print("Object sizes reduced.")

    # Create a report of URL statuses for each dataset
    print("Creating reports...")
    reports = []
    for i, d in enumerate(data):
        print(f"Creating report for {d['name']}, {i+1}/{len(data)}")
        reports.append(report(d))
    print("Reports created.")

    # Build a dataframe from the reports
    print("Building dataframe and exporting to CSV...")
    df = build_df(reports)
    df.to_csv('reports/url_test.csv', index=False)
    print("Complete.")

if __name__ == "__main__":
    main()
