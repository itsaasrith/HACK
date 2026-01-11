import json
import os

DATA_FILE = "data/history.json"


def _load_data():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ================= ADD ENTRY =================
def add_entry(username, entry):
    data = _load_data()

    if username not in data:
        data[username] = []

    data[username].append(entry)
    _save_data(data)


# ================= FETCH USER HISTORY =================
def fetch_user_entries(username):
    data = _load_data()
    return data.get(username, [])


# ================= FETCH ALL USERS =================
def fetch_all_users():
    data = _load_data()
    return list(data.keys())
