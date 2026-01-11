import json
import os
import hashlib

USERS_FILE = "data/users.json"


def _load_users():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    users = _load_users()
    if username in users:
        return False

    users[username] = {
        "password": _hash_password(password)
    }
    _save_users(users)
    return True


def login_user(username, password):
    users = _load_users()
    if username not in users:
        return False

    return users[username]["password"] == _hash_password(password)
