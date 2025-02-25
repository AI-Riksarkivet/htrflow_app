import gradio as gr
from htrflow.volume.volume import Collection
from jinja2 import Environment, FileSystemLoader

_ENV = Environment(loader=FileSystemLoader("app/assets/jinja-templates"))
_IMAGE_TEMPLATE = _ENV.get_template("image")
_TRANSCRIPTION_TEMPLATE = _ENV.get_template("transcription")


def render_image(collection: Collection, current_page_index):
    return _IMAGE_TEMPLATE.render(
        page=collection[current_page_index],
        lines=collection[current_page_index].traverse(lambda node: node.is_line()),
    )


def render_transcription(collection: Collection, current_page_index):
    regions = collection[current_page_index].traverse(
        lambda node: node.children and all(child.is_line() for child in node)
    )
    return _TRANSCRIPTION_TEMPLATE.render(regions=regions)


def toggle_navigation_button(collection: Collection):
    visible = len(collection.pages) > 1
    return gr.update(visible=visible)


def activate_left_button(current_page_index):
    interactive = current_page_index > 0
    return gr.update(interactive=interactive)


def activate_right_button(collection: Collection, current_page_index):
    interactive = current_page_index + 1 < len(collection.pages)
    return gr.update(interactive=interactive)


def right_button_click(collection: Collection, current_page_index):
    max_index = len(collection.pages) - 1
    return min(max_index, current_page_index + 1)


def left_button_click(current_page_index):
    return max(0, current_page_index - 1)


def update_image_caption(collection: Collection, current_page_index):
    n_pages = len(collection.pages)
    return f"Image {current_page_index + 1} of {n_pages}: `{collection[current_page_index].label}`"


with gr.Blocks() as visualizer:
    gr.Markdown("# Result")
    gr.Markdown(
        "The image to the left shows where HTRflow found text in the image. The transcription can be seen to the right."
    )

    with gr.Row():
        # Annotated image panel
        with gr.Column(scale=2):
            image = gr.HTML(
                label="Annotated image",
                padding=False,
                elem_classes="svg-image",
                container=True,
                max_height="65vh",
                min_height="65vh",
                show_label=True,
            )

            image_caption = gr.Markdown(elem_classes="button-group-viz")
            with gr.Row(elem_classes="button-group-viz"):
                left = gr.Button("← Previous", visible=False, interactive=False, scale=0)
                right = gr.Button("Next →", visible=False, scale=0)

        # Transcription panel
        with gr.Column(scale=1, elem_classes="transcription-column"):
            transcription = gr.HTML(
                label="Transcription",
                show_label=True,
                elem_classes="transcription",
                container=True,
                max_height="65vh",
                min_height="65vh",
            )

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
    collection.change(
        render_transcription,
        inputs=[collection, current_page_index],
        outputs=transcription,
    )
    collection.change(lambda _: 0, current_page_index, current_page_index)
    collection.change(toggle_navigation_button, collection, left)
    collection.change(toggle_navigation_button, collection, right)
    collection.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )

    # Updates on page change:
    # - update the view
    # - activate/deactivate buttons
    # - update the image caption
    current_page_index.change(render_image, inputs=[collection, current_page_index], outputs=image)
    current_page_index.change(
        render_transcription,
        inputs=[collection, current_page_index],
        outputs=transcription,
    )
    current_page_index.change(activate_left_button, current_page_index, left)
    current_page_index.change(activate_right_button, [collection, current_page_index], right)
    current_page_index.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )
