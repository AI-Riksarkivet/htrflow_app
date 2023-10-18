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
    _repo = huggingface_hub.Repository(
        local_dir="data", repo_type="dataset", clone_from="Riksarkivet/traffic_demo_data", use_auth_token=_TOKEN
    )
    _session_uuid = None

    @classmethod
    def _pull_repo_data(cls):
        cls._repo.git_pull()
        shutil.copyfile(cls._DB_TEMP_PATH, cls._DB_FILE_PATH)

    @staticmethod
    def _hash_ip(ip_address):
        return hashlib.sha256(ip_address.encode()).hexdigest()

    @classmethod
    def _current_time_in_sweden(cls):
        swedish_tz = pytz.timezone(cls._TZ)
        return datetime.now(swedish_tz).strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def onload_store_metric_data(cls, request: gr.Request):
        cls._session_uuid = str(uuid.uuid1())
        cls._setup_database()
        hashed_host = cls._hash_ip(request.client.host)
        cls._backup_and_update_database(hashed_host, "load")

    @classmethod
    def store_metric_data(cls, action, request: gr.Request):
        hashed_host = cls._hash_ip(request.client.host)
        cls._backup_and_update_database(hashed_host, action)

    @classmethod
    def _commit_host_to_database(cls, hashed_host, action):
        with sqlite3.connect(cls._DB_FILE_PATH) as db:
            db.execute(
                "INSERT INTO ip_data(current_time, hashed_ip, session_uuid, action) VALUES(?,?,?,?)",
                [cls._current_time_in_sweden(), hashed_host, cls._session_uuid, action],
            )

    @classmethod
    def _setup_database(cls):
        with sqlite3.connect(cls._DB_FILE_PATH) as db:
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
        cls._pull_repo_data()

    @classmethod
    def _backup_and_update_database(cls, hashed_host, action):
        cls._commit_host_to_database(hashed_host, action)
        shutil.copyfile(cls._DB_FILE_PATH, cls._DB_TEMP_PATH)

        with sqlite3.connect(cls._DB_FILE_PATH) as db:
            ip_data = db.execute("SELECT * FROM ip_data").fetchall()
            pd.DataFrame(ip_data, columns=["id", "current_time", "hashed_ip", "session_uuid", "action"]).to_csv(
                "./data/ip_data.csv", index=False
            )

        cls._repo.push_to_hub(blocking=False, commit_message=f"Updating data at {datetime.now()}")

    @classmethod
    def _initialize_and_schedule_backup(cls, hashed_host, action):
        cls._backup_and_update_database(hashed_host, action)
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            cls._backup_and_update_database, "interval", minutes=cls._INTERVAL_MIN_UPDATE, args=(hashed_host, action)
        )
        scheduler.start()
