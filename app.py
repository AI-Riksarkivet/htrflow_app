import hashlib
import os
import shutil
import sqlite3
from datetime import datetime

import gradio as gr
import huggingface_hub
import pandas as pd
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from helper.gradio_config import css, theme
from helper.text.text_about import TextAbout
from helper.text.text_app import TextApp
from helper.text.text_howto import TextHowTo
from helper.text.text_roadmap import TextRoadmap
from tabs.htr_tool import htr_tool_tab
from tabs.stepwise_htr_tool import stepwise_htr_tool_tab

DB_FILE = "./traffic_data.db"

TOKEN = os.environ.get("HUB_TOKEN")
repo = huggingface_hub.Repository(
    local_dir="data", repo_type="dataset", clone_from="Riksarkivet/traffic_demo_data", use_auth_token=TOKEN
)
repo.git_pull()

# Set db to latest
shutil.copyfile("./data/traffic_data.db", DB_FILE)


def hash_ip(ip_address):
    return hashlib.sha256(ip_address.encode()).hexdigest()


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


scheduler = BackgroundScheduler()
scheduler.add_job(func=backup_db, trigger="interval", seconds=60)
scheduler.start()


with gr.Blocks(title="HTR Riksarkivet", theme=theme, css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            text_ip_output = gr.Markdown()
        with gr.Column(scale=1):
            gr.Markdown(TextApp.title_markdown)
        with gr.Column(scale=1):
            gr.Markdown(TextApp.title_markdown_img)

    with gr.Tabs():
        with gr.Tab("HTR Tool"):
            htr_tool_tab.render()

        with gr.Tab("Stepwise HTR Tool"):
            stepwise_htr_tool_tab.render()

        with gr.Tab("About"):
            with gr.Tabs():
                with gr.Tab("Project"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextAbout.intro_text)
                        with gr.Column():
                            gr.Markdown(TextAbout.text_src_code_data_models)
                    with gr.Row():
                        gr.Markdown(TextAbout.pipeline_overview_text)
                    with gr.Row():
                        with gr.Tabs():
                            with gr.Tab("I. Binarization"):
                                gr.Markdown(TextAbout.binarization)
                            with gr.Tab("II. Region Segmentation"):
                                gr.Markdown(TextAbout.text_region_segment)
                            with gr.Tab("III. Line Segmentation"):
                                gr.Markdown(TextAbout.text_line_segmentation)
                            with gr.Tab("IV. Transcriber"):
                                gr.Markdown(TextAbout.text_htr)

                with gr.Tab("Contribution"):
                    with gr.Row():
                        gr.Markdown(TextRoadmap.text_contribution)

                with gr.Tab("API & Duplicate for Privat use"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextHowTo.htr_tool_api_text)
                            gr.Code(
                                value=TextHowTo.code_for_api,
                                language="python",
                                interactive=False,
                                show_label=False,
                            )
                        with gr.Column():
                            gr.Markdown(TextHowTo.duplicatin_space_htr_text)
                            gr.Markdown(TextHowTo.figure_htr_hardware)
                            gr.Markdown(TextHowTo.duplicatin_for_privat)

                with gr.Tab("Roadmap"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextRoadmap.roadmap)
                        with gr.Column():
                            gr.Markdown(TextRoadmap.discussion)

    demo.load(add_ip_data)


demo.queue(concurrency_count=2, max_size=2)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=True)
