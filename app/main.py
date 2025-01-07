import logging

import gradio as gr

from app.gradio_config import css, theme
from app.tabs.adv_htrflow_tab import adv_htrflow_pipeline
from app.tabs.data_explorer_tab import data_explorer
from app.tabs.examples_tab import examples
from app.tabs.htrflow_tab import htrflow_pipeline
from app.tabs.overview_tab import overview, overview_language
from app.utils.lang_helper import get_tab_updates
from app.utils.md_helper import load_markdown

logger = logging.getLogger("gradio_log")


TAB_LABELS = {
    "ENG": ["Home", "Simple HTR", "Custom HTR", "Examples"],
    "SWE": ["Hem", "Enkel HTR", "Anpassad HTR", "Exempel"],
}

LANG_CHOICES = ["ENG", "SWE"]

with gr.Blocks(title="HTRflow", theme=theme, css=css) as demo:
    with gr.Row():
        local_language = gr.BrowserState(default_value="ENG", storage_key="selected_language")
        main_language = gr.State(value="ENG")

        with gr.Column(scale=1):
            language_selector = gr.Dropdown(
                choices=LANG_CHOICES, value="ENG", container=False, min_width=50, scale=0, elem_id="langdropdown"
            )

        with gr.Column(scale=2):
            gr.Markdown(load_markdown(None, "main_title"))
        with gr.Column(scale=1):
            gr.Markdown(load_markdown(None, "main_sub_title"))

    with gr.Tabs(elem_classes="top-navbar") as navbar:
        with gr.Tab(label="Home") as tab_home:
            overview.render()

        with gr.Tab(label="Simple HTR") as tab_simple_htr:
            htrflow_pipeline.render()

        with gr.Tab(label="Custom HTR") as tab_custom_htr:
            adv_htrflow_pipeline.render()

        with gr.Tab(label="Examples") as tab_examples:
            examples.render()

        with gr.Tab(label="Data Explorer") as tab_data_explorer:
            data_explorer.render()

    @demo.load(inputs=[local_language], outputs=[language_selector, main_language, overview_language])
    def load_language(saved_values):
        return (saved_values,) * 3

    @language_selector.change(
        inputs=[language_selector],
        outputs=[
            local_language,
            main_language,
            overview_language,
        ],
    )
    def save_language_to_browser(selected_language):
        return (selected_language,) * 3

    @main_language.change(
        inputs=[main_language],
        outputs=[
            tab_home,
            tab_simple_htr,
            tab_custom_htr,
        ],
    )
    def update_main_tabs(selected_language):
        return (*get_tab_updates(selected_language, TAB_LABELS),)

    @main_language.change(inputs=[main_language])
    def log_on_language_change(selected_language):
        logger.info(f"Language changed to: {selected_language}")


demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, enable_monitoring=False)
