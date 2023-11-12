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
    result = d.search(artist=data["artist"], title=data["album"], format=data["format"], year=data["year"], type="release")
    
    def search_result(result):
            # 'Try' to prevent null attribute errors; replace with str 'none'.
            try:
                image = result.master.images[0]['resource_url']
            except AttributeError:
                image = 'none'
            try:
                id = result.id
            except AttributeError:
                id = 'none'
            try:
                artist = result.artists[0].name
            except AttributeError:
                artist = 'none'
            try:
                title = result.title
            except AttributeError:
                title = 'none'
            try:
            # TO DO: add condition for CDs to return different format value; currently returning 'album' and 'comp'
                format_list = []
                for x in result.formats[0]:
                    if x == "name":
                        continue
                    if x == "qty":
                        format_list.append(str(" ") + str(result.formats[0][x]) + "x" + str(result.formats[0]["descriptions"][0]))
                    if x == "descriptions":
                        try:
                            format_list.append(str(" ") + str(result.formats[0][x][2]))
                        except(IndexError):
                            continue
                    if x == "text":
                        format_list.append(str(" ") + str(result.formats[0][x]))
            except AttributeError:
                format = 'none'
            try:
                year = result.year
            except AttributeError:
                year = 'none'
            entry = [image, id, artist, title, format_list, year]
            return entry
    
    def df_match(release, df):
        return release in df
        
    df = pd.read_csv('collection\collection.csv')
    df = df.release_id.to_list()

    result_d = {}
    result_l = []

    # !!! NOT WORKING CORRECTLY. ID changing, but rest not !!!
    for release in result:
        result_d = {"release_data": search_result(release), "in_collection": df_match(release.id, df)}
        # result_d["in_collection"] = df_match(release.id, df)
        result_l.append(result_d)
    return result_l

@app.route('/search_collection', methods=['POST'])
def df_search_result():
    data = request.json

    # df = json_to_df('collection\collection.json')
    df = pd.read_csv('collection\collection.json')
    # print(df)
    df = df[df['Artist'].str.lower() == data['artist'].lower()]
        
    df_user = pd.read_csv('collection\\user_input.csv')
    df = df.merge(df_user, on='release_id')

    df_entries = []
    for index, row in df.iterrows():
        # list.append(row.values.flatten().tolist())
        df_entries.append(row.values.flatten().tolist())

    df_entries = df.to_json(orient='records')
    print(df_entries)
    return df_entries

@app.route('/release_add', methods=['POST'])
def df_add():
    data = request.json
    print(data)
    return data

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
