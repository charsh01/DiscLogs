# TO RUN: flask --app discogs-search run --debug

from flask import (Flask, render_template, abort, jsonify, request,
                   redirect, url_for)

import discogs_client as dc
from authenticate import authenticate

d = authenticate()

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index():
    return render_template("search.html")
    

#==================================================
# @app.route('/search', methods=['POST'])
# def search_data():
#     data = request.json
#     print(data)
#     result = d.search(artist=data["artist"], album=data["album"], format=data["format"], year=data["year"], type="release")

#     def search_result(result):
#         img = d.release(result.id).images[0]['resource_url']
#         artist = d.release(result.id).artists[0].name
#         title = d.release(result.id).title
#         format = d.release(result.id).formats[0]['name']
#         entry = [img, artist, title, format]
#         return entry

#     result_list = []
#     for release in result: 
#         result_list.append(search_result(release))
#     return result_list
#==================================================

# for release in result:
#     print(release.title, release.formats[0]['name'], release.year)
# print(search_result(result, release))
# print(search_result(result))
# result = d.search(artist=request.form['artist'], release_title=request.form['title'], format=request.form['format'], type='release')    

#==================================================

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
                    format_list.append(result.formats[0][x])
                    
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
    

#==================================================

# for release in result:
#     print(release.title, release.formats[0]['name'], release.year)
# print(search_result(result, release))
# print(search_result(result))

#==================================================









#=======================TESTING===========================
# result = d.search(artist='gauntlet ring', title='tyrannical bloodlust', format='cd', type='release', strict=True)
# for release in result:
#     entry = search_result(release)
#     print(entry)

#=======================OLD===========================
# print(dc_search)
# result = d.search(artist=request.form['artist'], release_title=request.form['title'], format=request.form['format'], type='release')    