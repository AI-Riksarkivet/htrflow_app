import os
import shutil
from pathlib import Path

import gradio as gr
from htrflow.volume.volume import Collection

DEFAULT_C = "txt"
CHOICES = ["txt", "alto", "page", "json"]

current_dir = Path(__file__).parent


def rename_files_in_directory(directory, fmt):
    """
    If fmt is "alto" or "page", rename each file in the directory so that its
    base name ends with _{fmt} (if it doesn't already). For other formats, leave
    the file names unchanged.
    Returns a list of the (new or original) file paths.
    """
    renamed = []
    for root, _, files in os.walk(directory):
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


def export_files(file_formats, collection: Collection, req: gr.Request):
    if len(file_formats) < 1:
        gr.Warning("No export file format was selected. Please select a File format")
        return gr.skip()

    if collection is None:
        gr.Warning("No image has been transcribed yet. Please go to the Upload tab")
        return gr.skip()

    temp_user_dir = current_dir / str(req.session_hash)
    temp_user_dir.mkdir(exist_ok=True)

    all_renamed_files = []
    for fmt in file_formats:
        temp_user_file_dir = os.path.join(temp_user_dir, fmt)
        collection.save(directory=temp_user_file_dir, serializer=fmt)
        renamed = rename_files_in_directory(temp_user_file_dir, fmt)
        all_renamed_files.extend(renamed)

    unique_files = list(dict.fromkeys(all_renamed_files))

    return unique_files, temp_user_dir


with gr.Blocks() as export:
    collection = gr.State()
    temp_state = gr.State()

    gr.Markdown("## Export")
    gr.Markdown("Choose file format for export.")
    with gr.Row():
        with gr.Column(scale=1):
            export_file_format = gr.Dropdown(
                value=DEFAULT_C,
                label="File format",
                info="Select export format(s)",
                choices=CHOICES,
                multiselect=True,
                interactive=True,
            )
            export_button = gr.Button("Export", scale=0, min_width=200, variant="primary")

        with gr.Column(scale=1):
            download_files = gr.Files(label="Download files", interactive=False)

        export_button.click(
            fn=export_files,
            inputs=[export_file_format, collection],
            outputs=[download_files, temp_state],
        ).then(
            fn=lambda folder: shutil.rmtree(folder) if folder else None,
            inputs=temp_state,
            outputs=None,
        )
