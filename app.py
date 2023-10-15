import os

import gradio as gr
from apscheduler.schedulers.background import BackgroundScheduler

from helper.gradio_config import css, theme
from helper.text.text_about import TextAbout
from helper.text.text_app import TextApp
from helper.text.text_howto import TextHowTo
from helper.text.text_roadmap import TextRoadmap
from helper.utils import add_ip_data, backup_db
from tabs.htr_tool import htr_tool_tab
from tabs.stepwise_htr_tool import stepwise_htr_tool_tab

SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)

if SECRET_KEY:
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
