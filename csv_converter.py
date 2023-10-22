import pandas as pd

def csv_to_json():
    df = pd.read_csv("collection\collection.csv")
    df.to_json("collection\collection.json")

def json_to_df(json_file):
    with open(json_file, encoding='utf-8-sig') as f_input:
        df = pd.read_json(f_input)
        return df
       
# df = json_to_df('collection\collection.json')
# print(df.head(20))