# discogs_manager
- Discogs management tool for collections and marketplace data.
- App linked to Discogs profile. Local collection pulled from my personal data. Authentication token for an empty new profile I made for testing. Will implement token input field to individualize for users.
- Search function was not running in an efficient way, so it is not usable in its current state as I continue working on it.
- Collection search label field not working.
- Collection artist and title fields are working correctly.
- Collection search results need to be limited by pages; getting too many requests error when pulling image data from Discogs.
- Collection search can be used to find releases in inventory. Clicking the release image will open a new pane showing details. Option to edit user-defined fields will be added and tracked in user_input.csv.
- Export to .csv and wantlist side panel buttons only placeholders.
- Update price history working. This checks the current lowest price listing (the only marketplace data available via the Discogs API) for every release in collection, and if different than the last checked days, adds this to a new dated column in the price_history.csv.
- Search collection > image click for release details > price history: generates a matplotlib bar graph comparing paid price from user_input.csv to listed prices in price_history.csv. Will have this passed to html and displayed in browser. Right now saving the graph @ static/images/plot.png.
- Will also include another side panel option to visually display collection-wide data, with options to filter by details such as artist, genre, label, dates, etc.

TO RUN:
- In command prompt: Navigate to saved file directory location. Double click the shortbut.bat file, which will open command prompt and run the flask app. You can also manually locate the directory location in command prompt and run "flask --app discogs-search.py run" once there.
- Open your browser and go to 'http://localhost:5000/' in the address bar.
- The app should now be usable. Exit command prompt to end the app.
