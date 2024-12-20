import gradio as gr

from app.gradio_config import css, theme
from app.tabs.adv_htrflow_tab import adv_htrflow_pipeline
from app.tabs.htrflow_tab import htrflow_pipeline
from app.tabs.overview_tab import overview
from app.texts_langs.text_app import TextApp

with gr.Blocks(title="HTRflow", theme=theme, css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            radio = gr.Dropdown(
                choices=["ENG", "SWE"], value="ENG", container=False, min_width=50, scale=0, elem_id="langdropdown"
            )

        with gr.Column(scale=2):
            gr.Markdown(TextApp.title_markdown)
        with gr.Column(scale=1):
            gr.Markdown(TextApp.title_markdown_img)

    with gr.Tabs(elem_classes="top-navbar") as navbar:
        with gr.Tab("Home"):
            overview.render()

        with gr.Tab("Simple HTR"):
            htrflow_pipeline.render()

        with gr.Tab("Custom HTR"):
            adv_htrflow_pipeline.render()

    # radio.change(
    #     None,
    #     inputs=radio,
    #     js="""
    #     (data) => {
    #     window.localStorage.setItem('data', JSON.stringify(data))
    #     }
    #     """,
    # )

    demo.load(
        None,
        inputs=radio,
        js="""
        (data) => {
        window.localStorage.setItem('data', JSON.stringify(data))
        }
        """,
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, enable_monitoring=False)
