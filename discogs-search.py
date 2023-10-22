# TO RUN: flask --app discogs-search run --debug

from flask import (Flask, render_template, abort, jsonify, request,
                   redirect, url_for)

import discogs_client as dc
from authenticate import authenticate
from csv_converter import json_to_df
from model import db

d = authenticate()

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index():
    return render_template("search.html")

@app.route('/search', methods=['POST'])
def search_data():
    data = request.json
    print(data)
    result = d.search(artist=data["artist"], title=data["album"], format=data["format"], year=data["year"], type="release")
    
    # Filtering through returned data for most important information needed by the user to make an informed selection of the particular release they're searching for.
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
    
    result_list = []
    for release in result: 
        result_list.append(search_result(release))
    return result_list

@app.route('/search_collection', methods=['POST'])
def df_search_result():
    data = request.json
    result_list = []

    df = json_to_df('collection\collection.json')
    print(df)
    df = df[df['Artist'] == data['artist']]

    df_entries = []

    for index, row in df.iterrows():

        # list.append(row.values.flatten().tolist())
        df_entries.append(row.values.flatten().tolist())
        
    df_entries = df.to_json(orient='records')
    print(df_entries)
    return df_entries


    




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
