import sys
import json
import pandas as pd

def main(in_file, out_file):
    df = pd.read_csv(in_file)
    df['Weighting'] = pd.to_numeric(df['Weighting'], errors='coerce')
    data = {}
    sections = df['Section'].unique()
    for section in sections:
        section_df = df[df["Section"] == section]
        data[section] = {}
        for r, v in section_df.iterrows():
            data[section][v["Attribute"]] = v["Weighting"]

    # Writing to sample.json
    with open(out_file, "w") as outfile:
        outfile.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process metadata quality weights into JSON')
    parser.add_argument('--in', metavar='CSV', dest='in_file', type=str, help='Input CSV path to metadata quality weights')
    parser.add_argument('--out', metavar='JSON', dest='out_file', type=str, help='Output JSON path for metadata quality weights')

    args = parser.parse_args()
    if args.in_file is None and args.out_file is None:
        parser.print_help()
        sys.exit(1)

    main(args.in_file, args.out_file)