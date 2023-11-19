# TO RUN: flask --app discogs-search run --debug
# flask --app discogs-search --debug run

from flask import (Flask, render_template, abort, jsonify, request,
                   redirect, url_for)

import discogs_client as dc
from authenticate import authenticate
from csv_converter import json_to_df
from model import db
import pandas as pd

d = authenticate()

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index():
    return render_template("search.html")

@app.route('/search', methods=['POST'])
def search_data():
    data = request.json
    print(data)

    # This searches Discogs directly, trying to search paginated pull instead to save time.
    result = d.search(data["artist"], type='artist')[0].releases

    def get_data(release):
            # 'Try' to prevent null attribute errors; replace with str 'none'.
            try:
                image = release.master.images[0]['resource_url']
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
            entry = [image, id, artist, title]
            return entry
    
    def df_match(release, df):
        return release in df
        
    df = pd.read_csv('collection\collection.csv')
    df = df.release_id.to_list()

    result_d = {}
    result_l = []

    for release in result:
        # print(release)
        result_d = {"release_data": get_data(release), "in_collection": df_match(release.id, df)}
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
            # Not working!!! vvvvvvvvvvvvvvvv
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


