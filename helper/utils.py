import hashlib
import os
import shutil
import sqlite3
from datetime import datetime

import gradio as gr
import huggingface_hub
import pandas as pd
import pytz


def hash_ip(ip_address):
    return hashlib.sha256(ip_address.encode()).hexdigest()


def current_time_sw():
    swedish_tz = pytz.timezone("Europe/Stockholm")
    return datetime.now(swedish_tz).strftime("%Y-%m-%d %H:%M:%S")


def add_ip_data(request: gr.Request):
    host = request.client.host
    hashed_ip = hash_ip(host)

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("INSERT INTO ip_data(current_time, hashed_ip) VALUES(?,?)", [current_time_sw(), hashed_ip])
    db.commit()
    db.close()


def backup_db():
    shutil.copyfile(DB_FILE, "./data/traffic_data.db")
    db = sqlite3.connect(DB_FILE)
    ip_data = db.execute("SELECT * FROM ip_data").fetchall()
    pd.DataFrame(ip_data, columns=["id", "current_time", "hashed_ip"]).to_csv("./data/ip_data.csv", index=False)

    print("updating traffic_data")
    repo.push_to_hub(blocking=False, commit_message=f"Updating data at {datetime.now()}")


DB_FILE = "./traffic_data.db"

TOKEN = os.environ.get("HUB_TOKEN")
repo = huggingface_hub.Repository(
    local_dir="data", repo_type="dataset", clone_from="Riksarkivet/traffic_demo_data", use_auth_token=TOKEN
)
repo.git_pull()

# Set db to latest
shutil.copyfile("./data/traffic_data.db", DB_FILE)


# Create table if it doesn't already exist
db = sqlite3.connect(DB_FILE)
try:
    db.execute("SELECT * FROM ip_data").fetchall()
    db.close()
except sqlite3.OperationalError:
    db.execute(
        """
        CREATE TABLE ip_data (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                              current_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                              hashed_ip TEXT)
        """
    )
    db.commit()
    db.close()
