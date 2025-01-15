import gradio as gr

from app.gradio_config import css, theme
from app.tabs.submit import submit, custom_template_yaml
from app.tabs.examples_tab import examples
from app.tabs.templating import (
    templating_block,
    TEMPLATE_IMAGE_FOLDER,
    TEMPLATE_YAML_FOLDER,
    template_output_yaml_code,
)
from app.utils.md_helper import load_markdown

gr.set_static_paths(paths=[TEMPLATE_IMAGE_FOLDER])
gr.set_static_paths(paths=[TEMPLATE_YAML_FOLDER])


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

        with gr.Tab(label="Output & Visualize") as tab_examples:
            examples.render()

    @demo.load(
        inputs=[template_output_yaml_code],
        outputs=[template_output_yaml_code],
    )
    def inital_yaml_code(template_output_yaml_code):
        return template_output_yaml_code

    def sync_yaml_state(input_value, state_value):
        """Synchronize the YAML state if there is a mismatch."""
        return input_value if input_value != state_value else gr.skip()

    tab_submit.select(
        inputs=[template_output_yaml_code, custom_template_yaml],
        outputs=[custom_template_yaml],
        fn=sync_yaml_state,
    )

    tab_templating.select(
        inputs=[custom_template_yaml, template_output_yaml_code],
        outputs=[template_output_yaml_code],
        fn=sync_yaml_state,
    )


demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7862,
        enable_monitoring=False,
        show_error=True,
    )
