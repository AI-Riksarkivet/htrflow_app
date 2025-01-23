import gradio as gr
from jinja2 import Environment, FileSystemLoader


_ENV = Environment(loader=FileSystemLoader("app/assets/jinja-templates"))
_IMAGE_TEMPLATE = _ENV.get_template("image")
_TRANSCRIPTION_TEMPLATE = _ENV.get_template("transcription")


def render_image(state):
    return _IMAGE_TEMPLATE.render(page=state[0], lines=state[0].traverse(lambda node: node.is_line()))


def render_transcription(state):
    return _TRANSCRIPTION_TEMPLATE.render(lines=state[0].traverse(lambda node: node.is_line()))


with gr.Blocks() as visualizer:

    with gr.Row():
        # Columns are needed here to get the scale right. The documentation
        # claims all components have the `scale` argument but it doesn't
        # seem to work for HTML components.

        # Transcription panel
        with gr.Column(scale=1):
            gr.Markdown("## Transcription")
            transcription = gr.HTML(elem_classes="transcription", container=True, max_height="60vh")

        # Annotated image panel
        with gr.Column(scale=2):
            gr.Markdown("## Annotated image")
            image = gr.HTML(padding=False, elem_classes="svg-image", container=True)

    collection_viz_state = gr.State()
    collection_viz_state.change(render_image, inputs=collection_viz_state, outputs=image)
    collection_viz_state.change(render_transcription, inputs=collection_viz_state, outputs=transcription)
