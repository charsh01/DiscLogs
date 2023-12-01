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

app = Flask(__name__)

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

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("search.html")

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    print(data)

    # Search Discogs using API.
    # Could do this much more elegantly but out of time.
    def search_for_master(input_data):
        master_id_list = []
        # Search if both artist and title.
        if input_data['artist'] != '' and input_data['title'] != '':
            result = d.search(input_data['artist'], type='artist')  
            # print(result)    
            for artist in result:
                for release in artist.releases:
                    # print(release)
                    if release.data['type'] == 'master' and release.data['title'].lower() == input_data['title'].lower():
                        master_id_list.append(str(release.id))
                        

        # Search if only artist.
        elif input_data['artist'] != '' and input_data['title'] == '':
            result = d.search(input_data['artist'], type='artist')  
            for artist in result:
                for release in artist.releases:
                    if release.data['type'] == 'master':
                        master_id_list.append(str(release.id))     

        # Search if only title.              
        else:
            result = d.search(input_data['title'], type='title')
            for release in result:
                    if release.data['type'] == 'master':
                        master_id_list.append(str(release.id)) 

        return master_id_list, result

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
            return entry
    
    # Checks if release id is in collection, returning true/false.
    def df_match_bool(release, df):
        return release in df

    master_id_list, result = search_for_master(data)

    if result.data.type == "artist":
        for id in master_id_list:
            for release in result:
                if release.data.id == id:
                    master_info = get_data(release)

    # if result.data.type == "artist":
    #     for release in result:
    #         print("this is the release:",release)
    print(master_info)


    # for release in result:
    #     # result_d = {"release_data": get_data(release), "in_collection": df_match_bool(release.id, df)}
    #     result_d = {"release_data": get_data(release)}
    #     result_l.append(result_d)
    return "testing"

# !!! merge not displaying correct/working? No user data (price paid? double check this)
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

# Show price history graph for individual release when searching collection and selecting release in collection.
@app.route('/price_release', methods=['POST'])
def price_release_img():
    release_id = int(request.json)

    # Testing showing entire graph:

    df_history = pd.read_csv('collection\\price_history.csv')
    df_paid = pd.read_csv('collection\\user_input.csv')
    df_paid_columns = ['release_id','paid']
    df_paid = df_paid[df_paid_columns]
    paid_row = df_paid[df_paid.release_id == release_id]
    df_merged = paid_row.merge(df_history, on='release_id')

    # Dropping null values so we can deal only with dates with valid price change values.
    df_plot = df_merged.dropna(axis='columns')
    print(df_plot)

    ax = df_plot[['paid',df_plot.iloc[:,-1:]]].plot(kind='bar', title ="V comp", figsize=(15, 10), legend=True, fontsize=12)

    # list_price_bar = price_graph.add_subplot(111)
    plt.show()

    return "test"

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

# Working
# Tracks changes in lowest price listings (only marketplace data accessible via Discogs) 
# Updates price_history.csv with new value in a new column by date if the new value differs from old.
@app.route('/price_hist/', methods=['POST'])
def update_total_values():
    df = pd.read_csv('collection\\price_history.csv')
    df_paid = pd.read_csv('collection\\user_input.csv')

    my_columns = ['release_id','paid']
    df_paid = df_paid[my_columns]
    df_columns = list(df)


    col_head = str(datetime.today().strftime('%Y-%m-%d'))
    
    for release, row in df.iterrows():
        id = str(int(row.release_id))
        try:
            current_low = d.release(id).marketplace_stats.lowest_price.value
            # Comparing price returned from check to current price, skipping if same.
            if (str(current_low)) != (str(df.at[release, df_columns[-1]])):
                print(id,":"," new price - ",current_low,".")
                df.at[release, col_head] = current_low
            else:
                print(id,": price is the same.")
        except AttributeError:
            df.at[release, col_head] = np.NaN
            print(id,"NULL")
        

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


