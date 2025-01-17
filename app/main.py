import shutil
import gradio as gr
import os
from app.gradio_config import css, theme
from app.tabs.submit import (
    submit,
    custom_template_yaml,
    collection_submit_state,
)
from app.tabs.visualizer import visualizer, collection_viz_state, viz_image_gallery
from app.tabs.templating import (
    templating_block,
    TEMPLATE_IMAGE_FOLDER,
    TEMPLATE_YAML_FOLDER,
    template_output_yaml_code,
)

from htrflow.models.huggingface.trocr import TrOCR

gr.set_static_paths(paths=[TEMPLATE_IMAGE_FOLDER])
gr.set_static_paths(paths=[TEMPLATE_YAML_FOLDER])

# TODO: fix api/ endpoints..
# TODO add colab
# TDOO addd eexmaple for api

def load_markdown(language, section, content_dir="app/content"):
    """Load markdown content from files."""
    if language is None:
        file_path = os.path.join(content_dir, f"{section}.md")
    else:
        file_path = os.path.join(content_dir, language, f"{section}.md")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"## Content missing for {file_path} in {language}"


with gr.Blocks(title="HTRflow", theme=theme, css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=2):
            gr.Markdown(load_markdown(None, "main_title"))
        with gr.Column(scale=1):
            gr.Markdown(load_markdown(None, "main_sub_title"))

    with gr.Tabs(elem_classes="top-navbar") as navbar:
        with gr.Tab(label="Templating") as tab_templating:
            templating_block.render()

        with gr.Tab(label="Submit Job") as tab_submit:
            submit.render()

        with gr.Tab(label="Visualize Result") as tab_visualizer:
            visualizer.render()

    @demo.load()
    def inital_yaml_code():
        tmp_dir = "tmp/"
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

    @demo.load(
        inputs=[template_output_yaml_code],
        outputs=[template_output_yaml_code],
    )
    def inital_yaml_code(template_output_yaml_code):
        return template_output_yaml_code

    @demo.load()
    def inital_trocr_load():
        return TrOCR("Riksarkivet/trocr-base-handwritten-hist-swe-2")

    def sync_gradio_objects(input_value, state_value):
        """Synchronize the YAML state if there is a mismatch."""
        return input_value if input_value != state_value else gr.skip()

    def sync_gradio_object_state(input_value, state_value):
        """Synchronize the Collection."""
        state_value = input_value
        return state_value if state_value is not None else gr.skip()

    tab_templating.select(
        inputs=[custom_template_yaml, template_output_yaml_code],
        outputs=[template_output_yaml_code],
        fn=sync_gradio_objects,
    )

    tab_submit.select(
        inputs=[template_output_yaml_code, custom_template_yaml],
        outputs=[custom_template_yaml],
        fn=sync_gradio_objects,
    )

    tab_visualizer.select(
        inputs=[collection_submit_state, collection_viz_state],
        outputs=[collection_viz_state],
        fn=sync_gradio_object_state,
    )


demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        enable_monitoring=True,
        ssr_mode=True
        # show_error=True,
    )
