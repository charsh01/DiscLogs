import discogs_client as dc

# Authenticates user for (better) API access.
# Need to set up way to save credentials to avoid retyping every time.

def authenticate():
    # Have user input these manually; will move vars index, outside of function. 
    string = 'MagneticLairLibraryManager/0.1'
    token = 'jgSavcSeMQISGWmBjOsjoGyQfpDkqgQGdoDfHCbQ'
    d = dc.Client(string, user_token=token)
    me = d.identity()
    return d