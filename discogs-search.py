# TO RUN: flask --app discogs-search run --debug
# flask --app discogs-search --debug run

from flask import (Flask, render_template, abort, jsonify, request,
                   redirect, url_for)
import matplotlib.pyplot as plt
import numpy as np
import discogs_client as dc
from authenticate import authenticate
from csv_converter import json_to_df
from model import db
import pandas as pd
from datetime import datetime

d = authenticate()

# Function for searching local collection by input fields; returns filtered dataframe.
def collection_search(data, df):
    for param in data:
        if param == "artist":
            if data[param] == "":
                continue
            else:
                df = df[df['Artist'].str.contains(data['artist'], case=False)]
        if param == "album":
            if data[param] == "":
                continue
            else:
                df = df[df['Title'].str.contains(data['album'], case=False)]
        if param == "label":
            if data[param] == "":
                continue
            else:
                df = df[df['Label'].str.contains(data['label'], case=False)]
        elif param == "format":
            if data[param] == "":
                continue
            elif data[param] == "Other":
                other_formats = ['vinyl','CD','Cass']
                df = df[~df['Format'].isin(other_formats)]
            else:
                df = df[df['Format'].str.contains(data['format'], case=False)]
    df_user = pd.read_csv('collection\\user_input.csv')
    df = df.merge(df_user, on='release_id')
    return df

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("search.html")

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    print(data)

    # Search Discogs using API.
    def search_by_inputs(input_data):
        for input in input_data:
            if input_data[input] == "":
                del input_data[input]
        try: 
            result = d.search(data["artist"], type='artist')[0].releases
        except AttributeError:
            try: 
                result = d.search(data["title"], type='title')[0].releases
            except AttributeError:
                result = d.search(data["label"], type='label')[0].releases
        return result

    # Collects necessary release data to display.
    def get_data(release):
            # 'Try' to prevent null attribute errors; replace with str 'none'.
            try:
                image = release.master.images[0]['uri150']
            # Aiming for master release img; fall back to release img or none.
            except AttributeError:
                try:
                    image = release.images[0]['uri150']
                except AttributeError:
                    image = 'none'
            try:
                id = release.id
            except AttributeError:
                id = 'none'
            try:
                artist = release.artists[0].name
            except AttributeError:
                artist = 'none'
            try:
                title = release.title
            except AttributeError:
                title = 'none'
            try:
                versions = []
                for version in release.versions:
                    versions.append(version.id)
            except AttributeError:
                versions = 'none'
            
            # entry = [image, id, artist, title]
            entry = {"image":image, "id":id, "Artist":artist, "Title":title, "versions":versions}
            print(entry)
            return entry
    
    # Checks if release id is in collection, returning true/false.
    def df_match_bool(release, df):
        return release in df
        
    df = pd.read_csv('collection\collection.csv')
    release_id_list = df.release_id.to_list()

    result_d = {}
    result_l = []

    result = search_by_inputs(data)
    for release in result:
        result_d = {"release_data": get_data(release), "in_collection": df_match_bool(release.id, df)}
        result_l.append(result_d)
    return result_l

@app.route('/search_collection', methods=['POST'])
def df_search_result():
    data = request.json
    print(data)
    df = pd.read_csv('collection\collection.csv')

    for param in data:
        if param == "artist":
            if data[param] == "":
                continue
            else:
                df = df[df['Artist'].str.contains(data['artist'], case=False)]
        if param == "album":
            if data[param] == "":
                continue
            else:
                df = df[df['Title'].str.contains(data['album'], case=False)]
        if param == "label":
            if data[param] == "":
                continue
            else:
                df = df[df['Label'].str.contains(data['label'], case=False)]
        elif param == "format":
            if data[param] == "":
                continue
            elif data[param] == "Other":
                other_formats = ['vinyl','CD','Cass']
                df = df[~df['Format'].isin(other_formats)]
            else:
                df = df[df['Format'].str.contains(data['format'], case=False)]

    df_user = pd.read_csv('collection\\user_input.csv')
    df = df.merge(df_user, on='release_id')

    df_entries = df.to_json(orient='records')
    return df_entries

@app.route('/versions', methods=['POST'])
def df_add():
    data = request.json
  
@app.route('/selected', methods=['POST'])
def see_details():
    data = request.json

    df = pd.read_csv('collection\collection.csv', dtype=str)
    df_user = pd.read_csv('collection\\user_input.csv', dtype=str)
    df = df[df.release_id == data]
    df_merged = df.merge(df_user, how='left', on='release_id')
    print(df_merged)

    release_info = df.to_json(orient='records')

    print(release_info)
    return release_info

@app.route('/release_edit', methods=['POST'])
def df_edit():
    data = request.json
    print(data)
    return data

@app.route('/price_history', methods=['POST'])
def price_history():
    release_id = request.json

    print(release_id)
    return release_id

# Returns price history data for releases in collection that search values return.
@app.route('/price', methods=['POST'])
def marketplace_graph():
    data = request.json
    df = pd.read_csv('collection\collection.csv')
    df = collection_search(data, df)
    columns = ['img_url','release_id','paid']
    df = df[columns]
    # df_entries = df.to_json(orient='records')

    # printtest = []
    # for entry in df_entries:
    #     test = d.release(int(entry['release_id'])).marketplace_stats
    #     printtest.append(test)

    # print(df_entries[0]['release_id'])
    for release, row in df.iterrows():
        id = row.release_id
        current_low = d.release(id).marketplace_stats.lowest_price.value
        paid = row.paid
        difference = (paid - current_low)
        low_val = 'Lowest price: ' + '$'+str(round(current_low,2))
        paid_val = 'Paid: ' + '$'+str(round(paid,2))
        # print('Price difference: ' + '$'+str(round(difference,2)))
        if '-' in str(difference):
            perc_val = 'Value: +'+str(round(100*(1-(paid/current_low))))+"%"
        else:
            perc_val = 'Value: -'+str(round(100*(1-(paid/current_low))))+"%"
        return_data = [low_val, paid_val, perc_val]

    return return_data

@app.route('/price_hist', methods=['POST'])
def update_total_values():
    df = pd.read_csv('collection\\price_history.csv')

    df_paid = pd.read_csv('collection\\user_input.csv')
    columns = ['release_id','paid']
    df_paid = df_paid[columns]

    # for release, row in df.iterrows():
    #     id = row.release_id
    #     current_low = d.release(id).marketplace_stats.lowest_price.value
    #     df[str(datetime.today().strftime('%Y-%m-%d'))] = current_low
    col_head = str(datetime.today().strftime('%Y-%m-%d'))
    
    for release, row in df.iterrows():
        id = str(row.release_id)
        try:
            current_low = d.release(id).marketplace_stats.lowest_price.value
            print(current_low)
            df.at[release, col_head] = current_low
        except AttributeError:
            df.at[release, col_head] = np.NaN
        print(id," ",current_low)

    df.to_csv('collection\\price_history.csv', index=False)

    return "test"
    # for index, row in df.iterrows():
    #     # list.append(row.values.flatten().tolist())
    #     entry[index] = row.values.flatten().tolist()

    # for row in df.iterrows():
    #     print("row test", row.tolist)
    #     result_list.append(row.tolist())
    # data = result_list.to_json()
    # for index, result in df[df['Artist'] == data['artist']].iterrows():
    #     df = df.append(result)
        # result_list.append(result)
    # return_test = result_list.tolist()
    # print(type(result_list))
    # list = []
    # print(df)


