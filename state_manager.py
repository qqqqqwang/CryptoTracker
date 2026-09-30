import json
import os

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"last_tweet_id": None, "last_youtube_url": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
