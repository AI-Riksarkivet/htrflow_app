import gradio as gr

from helper.text.text_about import TextAbout
from helper.text.text_roadmap import TextRoadmap

with gr.Blocks() as about_tab:
    with gr.Tabs():
        with gr.Tab("HTRFLOW"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextAbout.intro_text)
                with gr.Column():
                    gr.Markdown(TextAbout.text_src_code_data_models)
            with gr.Row():
                gr.Markdown(TextAbout.pipeline_overview_text)
            with gr.Row():
                with gr.Tabs():
                    with gr.Tab("Binarization"):
                        gr.Markdown(TextAbout.binarization)
                    with gr.Tab("Region segmentation"):
                        gr.Markdown(TextAbout.text_region_segment)
                    with gr.Tab("Line segmentation"):
                        gr.Markdown(TextAbout.text_line_segmentation)
                    with gr.Tab("Text recognition"):
                        gr.Markdown(TextAbout.text_htr)

        with gr.Tab("Contributions"):
            with gr.Row():
                gr.Markdown(TextRoadmap.text_contribution)

        with gr.Tab("Changelog & Roadmap"):
            with gr.Row():
                with gr.Column():
                    with gr.Accordion("Current Changelog", open=True):
                        gr.Markdown(TextRoadmap.changelog)
                    with gr.Accordion("Old Changelog", open=False):
                        pass
                with gr.Column():
                    gr.Markdown(TextRoadmap.roadmap)
