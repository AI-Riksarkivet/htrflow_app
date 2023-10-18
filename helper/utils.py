import hashlib
import os
import shutil
import sqlite3
import uuid
from datetime import datetime

import gradio as gr
import huggingface_hub
import pandas as pd
import pytz
from apscheduler.schedulers.background import BackgroundScheduler


class TrafficDataHandler:
    _DB_FILE_PATH = "./traffic_data.db"
    _DB_TEMP_PATH = "./data/traffic_data.db"
    _TOKEN = os.environ.get("HUB_TOKEN")
    _TZ = "Europe/Stockholm"
    _INTERVAL_MIN_UPDATE = 30

    def __init__(self, dataset_repo="Riksarkivet/traffic_demo_data"):
        self._repo = huggingface_hub.Repository(
            local_dir="data", repo_type="dataset", clone_from=dataset_repo, use_auth_token=self._TOKEN
        )
        self._pull_repo_data()
        self._setup_database()

    def _pull_repo_data(self):
        self._repo.git_pull()
        shutil.copyfile(self._DB_TEMP_PATH, self._DB_FILE_PATH)

    def _hash_ip(self, ip_address):
        return hashlib.sha256(ip_address.encode()).hexdigest()

    def _current_time_in_sweden(self):
        swedish_tz = pytz.timezone(self._TZ)
        return datetime.now(swedish_tz).strftime("%Y-%m-%d %H:%M:%S")

    def onload_store_metric_data(self, request: gr.Request):
        self._session_uuid = str(uuid.uuid1())
        hashed_host = self._hash_ip(request.client.host)
        self._backup_and_update_database(hashed_host, "load")

    def store_metric_data(self, action, request: gr.Request):
        self._session_uuid = str(uuid.uuid1())
        hashed_host = self._hash_ip(request.client.host)
        self._backup_and_update_database(hashed_host, action)

    def _commit_host_to_database(self, hashed_host, action):
        with sqlite3.connect(self._DB_FILE_PATH) as db:
            db.execute(
                "INSERT INTO ip_data(current_time, hashed_ip, session_uuid, action) VALUES(?,?,?,?)",
                [self._current_time_in_sweden(), hashed_host, self._session_uuid, action],
            )

    def _setup_database(self):
        with sqlite3.connect(self._DB_FILE_PATH) as db:
            try:
                db.execute("SELECT * FROM ip_data").fetchall()
            except sqlite3.OperationalError:
                db.execute(
                    """
                    CREATE TABLE ip_data (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                          current_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                          hashed_ip TEXT,
                                          session_uuid TEXT,
                                          action TEXT)
                    """
                )

    def _backup_and_update_database(self, hashed_host, action):
        self._commit_host_to_database(hashed_host, action)
        shutil.copyfile(self._DB_FILE_PATH, self._DB_TEMP_PATH)

        with sqlite3.connect(self._DB_FILE_PATH) as db:
            ip_data = db.execute("SELECT * FROM ip_data").fetchall()
            pd.DataFrame(ip_data, columns=["id", "current_time", "hashed_ip", "session_uuid", "action"]).to_csv(
                "./data/ip_data.csv", index=False
            )

        self._repo.push_to_hub(blocking=False, commit_message=f"Updating data at {datetime.now()}")

    def _initialize_and_schedule_backup(self, hashed_host, action):
        self._backup_and_update_database(hashed_host, action)
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self._backup_and_update_database, "interval", minutes=self._INTERVAL_MIN_UPDATE, args=(hashed_host, action)
        )
        scheduler.start()
