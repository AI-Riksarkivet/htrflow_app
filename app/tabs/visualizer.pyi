import gradio as gr
from htrflow.volume.volume import Collection
from gradio_i18n import gettext as _

from gradio.events import Dependency

class HTRVisualizer(gr.HTML):
    """Unified HTR visualization with synchronized image and transcription panels"""

    def __init__(self, max_height="70vh", layout="auto", edits=None, **kwargs):
        """
        Args:
            max_height: Maximum height for the visualizer (default: "70vh")
            layout: Layout mode - "horizontal" (side-by-side), "vertical" (stacked), or "auto" (responsive)
            edits: Dictionary to store edited line texts
        """
        # Load HTML, CSS, and JavaScript from external files
        html_template = load_file('template.html')
        css_template = load_file('visualizer.css')
        js_on_load = load_file('visualizer.js')

        super().__init__(
            value={"width": 100, "height": 100, "path": "", "lines": [], "regions": []},
            edits=edits or {},
            html_template=html_template,
            css_template=css_template,
            js_on_load=js_on_load,
            maxHeight=max_height,
            layout=layout,
            **kwargs
        )

    def api_info(self):
        return {
            "type": "object",
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"},
                "path": {"type": "string"},
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "polygonPoints": {"type": "string"},
                            "id": {"type": "integer"}
                        }
                    }
                },
                "regions": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "text": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component


def prepare_visualizer_data(collection: Collection, current_page_index: int):
    """Convert collection page to format expected by HTRVisualizer"""
    page = collection[current_page_index]
    lines = list(page.traverse(lambda node: node.is_line()))

    # Prepare regions with line IDs
    regions_raw = page.traverse(
        lambda node: node.children and all(child.is_line() for child in node)
    )

    line_counter = 0
    region_data = []
    for region in regions_raw:
        region_lines = []
        for line in region:
            region_lines.append({
                "id": line_counter,
                "text": line.text
            })
            line_counter += 1
        region_data.append(region_lines)

    return {
        "width": page.width,
        "height": page.height,
        "path": page.path,
        "lines": [
            {
                "polygonPoints": " ".join([f"{p[0]},{p[1]}" for p in line.polygon]),
                "id": idx
            }
            for idx, line in enumerate(lines)
        ],
        "regions": region_data
    }


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
    return f"**Image {current_page_index + 1} of {n_pages}:** `{collection[current_page_index].label}`"


def apply_text_edits(collection: Collection, page_index: int, edit_data: dict):
    """Apply text edits from the visualizer to the collection"""
    if not edit_data or not edit_data.get("edits"):
        return collection, gr.update(visible=False)

    page = collection[page_index]
    lines = list(page.traverse(lambda node: node.is_line()))

    edits = edit_data.get("edits", {})
    for line_id_str, new_text in edits.items():
        line_id = int(line_id_str)
        if 0 <= line_id < len(lines):
            lines[line_id].text = new_text

    # Return updated collection and hide save button
    return collection, gr.update(visible=False)


with gr.Blocks() as visualizer:
    gr.Markdown(
        _("visualizer_description")
    )

    visualizer_component = HTRVisualizer(
        max_height="70vh",
        layout="auto",
    )

    image_caption = gr.Markdown()

    # Edit mode controls
    with gr.Row(elem_classes="button-group-viz"):
        edit_mode = gr.Checkbox(label="✏️ Edit Mode", value=False, scale=0)
        save_btn = gr.Button("💾 Save Changes", visible=False, variant="primary", scale=0)

    with gr.Row(elem_classes="button-group-viz"):
        left = gr.Button(
            _("← Previous"), visible=False, interactive=False, scale=0
        )
        right = gr.Button(_("Next →"), visible=False, scale=0)

    collection = gr.State()
    current_page_index = gr.State(0)
    edit_data_trigger = gr.Textbox(visible=False, elem_id="edit_data_trigger")  # Hidden field to receive edits from JavaScript

    # Wiring of navigation buttons
    left.click(left_button_click, current_page_index, current_page_index)
    right.click(
        right_button_click, [collection, current_page_index], current_page_index
    )

    # Updates on collection change
    collection.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component
    )
    collection.change(lambda _: 0, current_page_index, current_page_index)
    collection.change(toggle_navigation_button, collection, left)
    collection.change(toggle_navigation_button, collection, right)
    collection.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )

    # Updates on page change
    current_page_index.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component
    )
    current_page_index.change(activate_left_button, current_page_index, left)
    current_page_index.change(
        activate_right_button, [collection, current_page_index], right
    )
    current_page_index.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )

    # Edit mode functionality
    edit_mode.change(
        lambda is_edit: gr.update(visible=is_edit),
        inputs=[edit_mode],
        outputs=[save_btn]
    )

    # Parse JSON from text trigger and apply edits
    def parse_and_apply_edits(collection_val, page_idx, edit_json_str):
        """Parse JSON string and apply edits"""
        import json
        try:
            if edit_json_str:
                edit_data_dict = json.loads(edit_json_str)
                return apply_text_edits(collection_val, page_idx, edit_data_dict)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing edit data: {e}")
            return collection_val, gr.update(visible=False)
        return collection_val, gr.update(visible=False)

    # Save button - apply edits to collection
    save_btn.click(
        fn=parse_and_apply_edits,
        inputs=[collection, current_page_index, edit_data_trigger],
        outputs=[collection, save_btn]
    ).then(
        fn=prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=[visualizer_component]
    )

    # When edit_data_trigger changes, show save button
    edit_data_trigger.change(
        lambda x: gr.update(visible=True) if x else gr.update(visible=False),
        inputs=[edit_data_trigger],
        outputs=[save_btn]
    )