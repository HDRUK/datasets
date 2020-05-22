import pandas as pd
import json

REPORTING_LEVELS = ["A: Summary", "B: Business", "C: Coverage & Detail",
                    "D: Format & Structure", "E: Attribution", "F: Technical Metadata"]

def main():
    df = pd.read_csv("weightings_config.tsv", sep="\t")
    main_dict = {}
    for section in REPORTING_LEVELS:
        section_df = df[df["Section"] == section]
        section_df = section_df[["Attribute", "Weighting"]]
        sub_dict = {}
        for r, v in section_df.iterrows():
            sub_dict[v["Attribute"]] = v["Weighting"]
        main_dict[section] = sub_dict
    # Serializing json
    json_object = json.dumps(main_dict, indent=4)

    # Writing to sample.json
    with open("CI_TEST.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    main()