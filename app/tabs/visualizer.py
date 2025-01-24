import gradio as gr
from jinja2 import Environment, FileSystemLoader


_ENV = Environment(loader=FileSystemLoader("app/assets/jinja-templates"))
_IMAGE_TEMPLATE = _ENV.get_template("image")
_TRANSCRIPTION_TEMPLATE = _ENV.get_template("transcription")


def render_image(collection, current_page_index):
    return _IMAGE_TEMPLATE.render(page=collection[current_page_index], lines=collection[current_page_index].traverse(lambda node: node.is_line()))


def render_transcription(collection, current_page_index):
    return _TRANSCRIPTION_TEMPLATE.render(lines=collection[current_page_index].traverse(lambda node: node.is_line()))


def toggle_navigation_button(collection):
    visible = len(collection.pages) > 1
    return gr.update(visible=visible)


def activate_left_button(current_page_index):
    interactive = current_page_index > 0
    return gr.update(interactive=interactive)


def activate_right_button(collection, current_page_index):
    interactive = current_page_index + 1 < len(collection.pages)
    return gr.update(interactive=interactive)


def right_button_click(collection, current_page_index):
    max_index = len(collection.pages) - 1
    return min(max_index, current_page_index + 1)


def left_button_click(current_page_index):
    return max(0, current_page_index - 1)


def update_image_caption(collection, current_page_index):
    n_pages = len(collection.pages)
    return f"Image {current_page_index + 1} of {n_pages}: `{collection[current_page_index].label}`"


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

            image_caption = gr.Markdown()
            with gr.Row():
                left = gr.Button("← Previous", visible=False, interactive=False)
                right = gr.Button("Next →", visible=False)

    collection = gr.State()
    current_page_index = gr.State(0)

    # Wiring of navigation buttons
    left.click(left_button_click, current_page_index, current_page_index)
    right.click(right_button_click, [collection, current_page_index], current_page_index)

    # Updates on collection change:
    # - update the view
    # - reset the page index (always start on page 0)
    # - toggle visibility of navigation buttons (don't show them for single pages)
    # - update the image caption
    collection.change(render_image, inputs=[collection, current_page_index], outputs=image)
    collection.change(render_transcription, inputs=[collection, current_page_index], outputs=transcription)
    collection.change(lambda _: 0, current_page_index, current_page_index)
    collection.change(toggle_navigation_button, collection, left)
    collection.change(toggle_navigation_button, collection, right)
    collection.change(update_image_caption, inputs=[collection, current_page_index], outputs=image_caption)

    # Updates on page change:
    # - update the view
    # - activate/deactivate buttons
    # - update the image caption
    current_page_index.change(render_image, inputs=[collection, current_page_index], outputs=image)
    current_page_index.change(render_transcription, inputs=[collection, current_page_index], outputs=transcription)
    current_page_index.change(activate_left_button, current_page_index, left)
    current_page_index.change(activate_right_button, [collection, current_page_index], right)
    current_page_index.change(update_image_caption, inputs=[collection, current_page_index], outputs=image_caption)
