import gradio as gr

from helper.text.text_about import TextAbout
from helper.text.text_roadmap import TextRoadmap

with gr.Blocks() as about_tab:
    with gr.Tabs():
        with gr.Tab("HTRFLOW"):
            gr.Markdown(
                "update... todo.. here we should talk about the pipline and the app as seperate things... pipline overview perhaps be moved?"
            )
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextAbout.intro_text)
                with gr.Column():
                    gr.Markdown(TextAbout.text_src_code_data_models)
            with gr.Row():
                gr.Markdown(TextAbout.pipeline_overview_text)
            with gr.Row():
                with gr.Tabs():
                    with gr.Tab("1. Binarization"):
                        gr.Markdown(TextAbout.binarization)
                    with gr.Tab("2. Region Segmentation"):
                        gr.Markdown(TextAbout.text_region_segment)
                    with gr.Tab("3. Line Segmentation"):
                        gr.Markdown(TextAbout.text_line_segmentation)
                    with gr.Tab("4. Transcriber"):
                        gr.Markdown(TextAbout.text_htr)

        with gr.Tab("Contributions"):
            with gr.Row():
                gr.Markdown(TextRoadmap.text_contribution)

        with gr.Tab("Changelog & Roadmap"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextRoadmap.changelog)
                with gr.Column():
                    gr.Markdown(TextRoadmap.roadmap)
