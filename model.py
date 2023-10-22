import json

def load_db():
        with open("collection\collection.json") as f:
                return json.load(f)

# def dump_db(entry):
#         with open("db_id.json", "w") as f:
#                 return json.dump(entry, f)

db = load_db()