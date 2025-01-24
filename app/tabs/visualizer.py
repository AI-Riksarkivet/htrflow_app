import gradio as gr
from jinja2 import Environment, FileSystemLoader


_ENV = Environment(loader=FileSystemLoader("app/assets/jinja-templates"))
_IMAGE_TEMPLATE = _ENV.get_template("image")
_TRANSCRIPTION_TEMPLATE = _ENV.get_template("transcription")


def render_image(collection, current_page_idx):
    return _IMAGE_TEMPLATE.render(page=collection[current_page_idx], lines=collection[current_page_idx].traverse(lambda node: node.is_line()))


def render_transcription(collection, current_page_idx):
    return _TRANSCRIPTION_TEMPLATE.render(lines=collection[current_page_idx].traverse(lambda node: node.is_line()))


def toggle_navigation_button(collection):
    visible = len(collection.pages) > 1
    return gr.update(visible=visible)


def activate_left_button(current_page_idx):
    interactive = current_page_idx > 0
    return gr.update(interactive=interactive)


def activate_right_button(collection, current_page_idx):
    interactive = current_page_idx + 1 < len(collection.pages)
    return gr.update(interactive=interactive)


def right_button_click(collection, current_page_index):
    max_index = len(collection.pages) - 1
    return min(max_index, current_page_index + 1)


def update_image_caption(collection, current_page_idx):
    n_pages = len(collection.pages)
    return f"Image {current_page_idx + 1} of {n_pages}: `{collection[current_page_idx].label}`"


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

    collection_viz_state = gr.State()

    current_page_idx = gr.State(0)

    # Update `current_page_idx` on button click
    left.click(lambda current_page_idx: max(0, current_page_idx-1), current_page_idx, current_page_idx)
    right.click(right_button_click, [collection_viz_state, current_page_idx], current_page_idx)

    # Update the view when...
    # ...the collection changes, or...
    collection_viz_state.change(render_image, inputs=[collection_viz_state, current_page_idx], outputs=image)
    collection_viz_state.change(render_transcription, inputs=[collection_viz_state, current_page_idx], outputs=transcription)
    # ...`current_page_idx` changes
    current_page_idx.change(render_image, inputs=[collection_viz_state, current_page_idx], outputs=image)
    current_page_idx.change(render_transcription, inputs=[collection_viz_state, current_page_idx], outputs=transcription)

    # Toggle interactivity of navigation buttons when `current_page_idx` changes
    current_page_idx.change(activate_left_button, current_page_idx, left)
    current_page_idx.change(activate_right_button, [collection_viz_state, current_page_idx], right)

    # Reset `current_page_idx` when the collection is updated
    collection_viz_state.change(lambda _: 0, current_page_idx, current_page_idx)

    # Toggle visibility of navigation buttons (they're hidden if there's only one page) when the collection is updated
    collection_viz_state.change(toggle_navigation_button, collection_viz_state, left)
    collection_viz_state.change(toggle_navigation_button, collection_viz_state, right)

    # Update the image caption when the collection or current index changes
    current_page_idx.change(update_image_caption, inputs=[collection_viz_state, current_page_idx], outputs=image_caption)
    collection_viz_state.change(update_image_caption, inputs=[collection_viz_state, current_page_idx], outputs=image_caption)
