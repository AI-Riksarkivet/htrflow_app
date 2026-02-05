import os
import shutil
from pathlib import Path

import gradio as gr
from htrflow.volume.volume import Collection
from htrflow.results import RecognizedText, TEXT_RESULT_KEY
from gradio_i18n import gettext as _

# Export functionality
current_dir = Path(__file__).parent
visualizer_dir = current_dir / "visualizer"
DEFAULT_EXPORT_FORMAT = "txt"
EXPORT_CHOICES = ["txt", "alto", "page", "json"]

# Load external files (HTML, CSS, JavaScript)
def load_file(filename):
    """Load external file content (HTML, CSS, or JavaScript)"""
    file_path = visualizer_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class HTRVisualizer(gr.HTML):
    """Unified HTR visualization with synchronized image and transcription panels"""

    def __init__(self, max_height="70vh", layout="auto", edits=None, **kwargs):
        html_template = load_file("template.html")
        css_template = load_file("visualizer.css")
        js_on_load = load_file("visualizer.js")

        super().__init__(
            value={"width": 100, "height": 100, "path": "", "lines": [], "regions": []},
            edits=edits or {},
            html_template=html_template,
            css_template=css_template,
            js_on_load=js_on_load,
            maxHeight=max_height,
            layout=layout,
            **kwargs,
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
                            "id": {"type": "integer"},
                        },
                    },
                },
                "regions": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "text": {"type": "string"},
                            },
                        },
                    },
                },
            },
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
            region_lines.append({"id": line_counter, "text": line.text})
            line_counter += 1
        region_data.append(region_lines)

    return {
        "width": page.width,
        "height": page.height,
        "path": page.path,
        "lines": [
            {
                "polygonPoints": " ".join([f"{p[0]},{p[1]}" for p in line.polygon]),
                "id": idx,
            }
            for idx, line in enumerate(lines)
        ],
        "regions": region_data,
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

def rename_files_in_directory(directory, fmt):
    """
    If fmt is "alto" or "page", rename each file in the directory so that its
    base name ends with _{fmt} (if it doesn't already). For other formats, leave
    the file names unchanged.
    Returns a list of the (new or original) file paths.
    """
    renamed = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            old_path = os.path.join(root, file)

            if fmt in ["alto", "page"]:
                name, ext = os.path.splitext(file)

                if not name.endswith(f"_{fmt}"):
                    new_name = f"{name}_{fmt}{ext}"
                    new_path = os.path.join(root, new_name)
                    os.rename(old_path, new_path)
                    renamed.append(new_path)
                else:
                    renamed.append(old_path)
            else:
                renamed.append(old_path)
    return renamed

def export_and_download(file_format, collection: Collection, req: gr.Request):
    """Export collection and prepare download button with file"""
    if not file_format:
        gr.Warning(_("No export file format was selected"))
        return None

    if collection is None:
        gr.Warning(_("No image has been transcribed yet. Please go to the HTR tab"))
        return None

    temp_user_dir = current_dir / str(req.session_hash)
    temp_user_dir.mkdir(exist_ok=True)

    # Export to single format
    temp_user_file_dir = os.path.join(temp_user_dir, file_format)
    collection.save(directory=temp_user_file_dir, serializer=file_format)
    exported_files = rename_files_in_directory(temp_user_file_dir, file_format)

    if exported_files and len(exported_files) > 0:
        if len(exported_files) > 1:
            zip_path = os.path.join(temp_user_dir, f"export_{file_format}.zip")
            shutil.make_archive(zip_path.replace(".zip", ""), "zip", temp_user_file_dir)
            file_path = zip_path
        else:
            file_path = exported_files[0]

        gr.Info("✅ Export successful! Download starting...")
        return file_path

    return None

def apply_text_edits(collection: Collection, page_index: int, visualizer_value: dict):
    """Apply text edits from the visualizer to the collection"""
    edit_data = (
        visualizer_value.get("edits", {}) if isinstance(visualizer_value, dict) else {}
    )

    if not edit_data:
        return collection

    page = collection[page_index]
    lines = list(page.traverse(lambda node: node.is_line()))

    for line_id_str, new_text in edit_data.items():
        line_id = int(line_id_str)
        if 0 <= line_id < len(lines):
            line = lines[line_id]
            old_result = line.get(TEXT_RESULT_KEY)
            score = (
                old_result.scores[0]
                if (old_result and hasattr(old_result, "scores") and old_result.scores)
                else 1.0
            )
            line.add_data(**{TEXT_RESULT_KEY: RecognizedText([new_text], [score])})

    return collection

with gr.Blocks() as visualizer:
    gr.Markdown(_("visualizer_description"))

    visualizer_component = HTRVisualizer(
        max_height="70vh",
        layout="auto",
        edits={},
    )

    image_caption = gr.Markdown()

    with gr.Row(equal_height=False):
        with gr.Column(elem_classes="button-group-viz"):
            left = gr.Button(
                _("← Previous"),
                visible=False,
                interactive=False,
                scale=0,
                min_width=100,
            )
            right = gr.Button(_("Next →"), visible=False, scale=0, min_width=100)
        with gr.Column(scale=0, min_width=200):
            with gr.Row(equal_height=True):
                export_file_format = gr.Dropdown(
                    value=DEFAULT_EXPORT_FORMAT,
                    label=None,
                    info=None,
                    choices=EXPORT_CHOICES,
                    multiselect=False,
                    interactive=True,
                    scale=0,
                    min_width=70,
                    container=False,
                )
                export_button = gr.Button(
                    _("📤 Export"), scale=0, min_width=70, variant="primary", size="sm"
                )
                download_button = gr.DownloadButton(
                    _("⬇️ Download"),
                    scale=0,
                    min_width=70,
                    variant="secondary",
                    size="sm",
                    elem_id="hidden-download-btn",
                    elem_classes="hidden-download-btn",
                )

    collection = gr.State()
    current_page_index = gr.State(0)
    temp_state = gr.State()

    left.click(left_button_click, current_page_index, current_page_index)
    right.click(
        right_button_click, [collection, current_page_index], current_page_index
    )

    collection.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component,
    )
    collection.change(lambda _: 0, current_page_index, current_page_index)
    collection.change(toggle_navigation_button, collection, left)
    collection.change(toggle_navigation_button, collection, right)
    collection.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )

    current_page_index.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component,
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

    def check_and_apply_edits(coll, page_idx, viz_value):
        """Check if visualizer value has edits and apply them"""
        if isinstance(viz_value, dict) and "edits" in viz_value and viz_value["edits"]:
            updated_coll = apply_text_edits(coll, page_idx, viz_value)
            viz_data = prepare_visualizer_data(updated_coll, page_idx)

            gr.Info("✅ Edits saved successfully!")
            return updated_coll, viz_data
        return coll, gr.update()

    visualizer_component.change(
        fn=check_and_apply_edits,
        inputs=[collection, current_page_index, visualizer_component],
        outputs=[collection, visualizer_component],
    )

    export_button.click(
        fn=export_and_download,
        inputs=[export_file_format, collection],
        outputs=download_button,
    ).then(
        fn=None,
        inputs=None,
        outputs=None,
        js="() => document.getElementById('hidden-download-btn').click()",
    )
