import os
import shutil
from pathlib import Path

import gradio as gr
from htrflow.volume.volume import Collection
from htrflow.results import RecognizedText, TEXT_RESULT_KEY
from gradio_i18n import gettext as _

current_dir = Path(__file__).parent
visualizer_dir = current_dir / "visualizer"
DEFAULT_EXPORT_FORMAT = "txt"
EXPORT_CHOICES = ["txt", "alto", "page", "json"]


def load_file(filename):
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


def prepare_visualizer_data(collection: Collection, current_page_index: int):
    all_pages = []

    for page_idx, page in enumerate(collection.pages):
        lines = list(page.traverse(lambda node: node.is_line()))

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

        all_pages.append(
            {
                "width": page.width,
                "height": page.height,
                "path": page.path,
                "label": page.label,
                "lines": [
                    {
                        "polygonPoints": " ".join(
                            [f"{p[0]},{p[1]}" for p in line.polygon]
                        ),
                        "id": idx,
                    }
                    for idx, line in enumerate(lines)
                ],
                "regions": region_data,
            }
        )

    return {
        "pages": all_pages,
        "currentPageIndex": current_page_index,
        "totalPages": len(collection.pages),
    }


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
    if not file_format:
        gr.Warning(_("No export file format was selected"))
        return None

    if collection is None:
        gr.Warning(_("No image has been transcribed yet. Please go to the HTR tab"))
        return None

    temp_user_dir = current_dir / str(req.session_hash)
    temp_user_dir.mkdir(exist_ok=True)

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


def apply_text_edits(collection: Collection, visualizer_value: dict):
    """Apply text edits from the visualizer to the collection"""
    edit_data = (
        visualizer_value.get("edits", {}) if isinstance(visualizer_value, dict) else {}
    )

    if not edit_data:
        return collection

    # Edits are keyed as "pageIndex_lineId"
    for edit_key, new_text in edit_data.items():
        page_idx_str, line_id_str = edit_key.split("_")
        page_idx = int(page_idx_str)
        line_id = int(line_id_str)

        if 0 <= page_idx < len(collection.pages):
            page = collection[page_idx]
            lines = list(page.traverse(lambda node: node.is_line()))

            if 0 <= line_id < len(lines):
                line = lines[line_id]
                old_result = line.get(TEXT_RESULT_KEY)
                score = (
                    old_result.scores[0]
                    if (
                        old_result
                        and hasattr(old_result, "scores")
                        and old_result.scores
                    )
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

    with gr.Row(equal_height=True):
        gr.Column(scale=1)  # Empty space to push content right
        with gr.Column(scale=0, min_width=120, elem_classes="export-dropdown-col"):
            export_file_format = gr.Dropdown(
                value=DEFAULT_EXPORT_FORMAT,
                label=None,
                info=None,
                choices=EXPORT_CHOICES,
                multiselect=False,
                interactive=True,
                scale=1,
                min_width=120,
                container=False,
                elem_classes="export-dropdown",
            )
        with gr.Column(scale=0, min_width=100, elem_classes="export-button-col"):
            export_button = gr.Button(
                _("📤 Export"),
                scale=0,
                min_width=100,
                variant="primary",
                size="md",
                elem_classes="export-button",
            )

    # Hidden download button (needs to be in DOM for JS to trigger it)
    # Using custom CSS to hide it instead of visible=False
    download_button = gr.DownloadButton(
        _("⬇️ Download"),
        elem_id="hidden-download-btn",
        elem_classes="hidden-download-btn",
    )

    collection = gr.State()
    current_page_index = gr.State(0)

    def check_and_apply_edits(coll, viz_value):
        """Check if visualizer value has edits and apply them"""
        if isinstance(viz_value, dict) and "edits" in viz_value and viz_value["edits"]:
            updated_coll = apply_text_edits(coll, viz_value)
            viz_data = prepare_visualizer_data(updated_coll, 0)

            gr.Info("✅ Edits saved successfully!")
            return updated_coll, viz_data
        return coll, gr.update()

    collection.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component,
    )

    visualizer_component.change(
        fn=check_and_apply_edits,
        inputs=[collection, visualizer_component],
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
