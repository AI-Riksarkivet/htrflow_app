import os
SECRET_KEY = os.environ.get("HUB_TOKEN", False)
if SECRET_KEY:
    from helper.utils import TrafficDataHandler
    
import uuid

import gradio as gr

from helper.gradio_config import css, theme
from helper.text.text_app import TextApp

from tabs.htr_tool import htr_tool_tab
from tabs.overview_tab import overview
from tabs.stepwise_htr_tool import stepwise_htr_tool_tab

session_uuid = str(uuid.uuid1())

with gr.Blocks(title="Riksarkivet", theme=theme, css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            text_ip_output = gr.Markdown(TextApp.demo_version)
        with gr.Column(scale=2):
            gr.Markdown(TextApp.title_markdown)
        with gr.Column(scale=1):
            gr.Markdown(TextApp.title_markdown_img)

    with gr.Tabs():
        with gr.Tab("Fast track"):
            htr_tool_tab.render()

        with gr.Tab("Stepwise"):
            stepwise_htr_tool_tab.render()

        with gr.Tab("Overview"):
            overview.render()

        with gr.Tab("How to use"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Fast track")
                    gr.Video(
                        value="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/eating_spaghetti.mp4",
                        format="mp4",
                    )
                with gr.Column():
                    gr.Markdown("## Stepwise")
                    gr.Video(
                        "https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/htr_tool_media_cut.mp4",
                        format="mp4",
                    )

    if SECRET_KEY:
        demo.load(
            fn=TrafficDataHandler.onload_store_metric_data,
            inputs=None,
            outputs=None,
        )


demo.queue(concurrency_count=2, max_size=2)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=False)
