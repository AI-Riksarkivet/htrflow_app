import glob
import time
import uuid
import gradio as gr
from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import init_step
import os
from htrflow.volume.volume import Collection

from htrflow.pipeline.steps import auto_import
import yaml

MAX_IMAGES = int(os.environ.get("MAX_IMAGES", 5))  # env: Maximum allowed images


class PipelineWithProgress(Pipeline):
    @classmethod
    def from_config(cls, config: dict[str, str]):
        """Init pipeline from config, ensuring the correct subclass is instantiated."""
        return cls(
            [
                init_step(step["step"], step.get("settings", {}))
                for step in config["steps"]
            ]
        )

    def run(self, collection, start=0, progress=None):
        """
        Run pipeline on collection with Gradio progress support.
        If progress is provided, it updates the Gradio progress bar during execution.
        """
        total_steps = len(self.steps[start:])
        for i, step in enumerate(self.steps[start:]):
            step_name = f"{step} (step {start + i + 1} / {total_steps})"

            try:
                progress((i + 1) / total_steps, desc=f"Running {step_name}")
                collection = step.run(collection)

            except Exception:
                if self.pickle_path:
                    gr.Error(
                        f"HTRflow: Pipeline failed on step {step_name}. A backup collection is saved at {self.pickle_path}"
                    )
                else:
                    gr.Error(
                        f"HTRflow: Pipeline failed on step {step_name}",
                    )
                raise
        return collection


def rewrite_export_dests(config):
    """
    Rewrite the 'dest' in all 'Export' steps to include 'tmp' and a UUID.
    Returns:
        - A new config object with the updated 'dest' values.
        - A list of all updated 'dest' paths.
    """
    new_config = {"steps": []}
    updated_paths = []

    unique_id = str(uuid.uuid4())

    for step in config.get("steps", []):
        new_step = step.copy()
        if new_step.get("step") == "Export":
            settings = new_step.get("settings", {})
            if "dest" in settings:
                new_dest = os.path.join("tmp", unique_id, settings["dest"])
                settings["dest"] = new_dest
                updated_paths.append(new_dest)
        new_config["steps"].append(new_step)

    return new_config, updated_paths


def run_htrflow(custom_template_yaml, batch_image_gallery, progress=gr.Progress()):
    """
    Executes the HTRflow pipeline based on the provided YAML configuration and batch images.
    Args:
        custom_template_yaml (str): YAML string specifying the HTRflow pipeline configuration.
        batch_image_gallery (list): List of uploaded images to process in the pipeline.
    Returns:
        tuple: A collection of processed items, list of exported file paths, and a Gradio update object.
    """

    if custom_template_yaml is None or len(custom_template_yaml) < 1:
        gr.Warning("HTRflow: Please insert a HTRflow-yaml template")
    try:
        config = yaml.safe_load(custom_template_yaml)
    except Exception as e:
        gr.Warning(f"HTRflow: Error loading YAML configuration: {e}")
        return gr.skip()

    temp_config, tmp_output_paths = rewrite_export_dests(config)

    progress(0, desc="HTRflow: Starting")
    time.sleep(0.3)

    print(temp_config)

    if batch_image_gallery is None:
        gr.Warning("HTRflow: You must upload atleast 1 image or more")

    images = [temp_img[0] for temp_img in batch_image_gallery]

    pipe = PipelineWithProgress.from_config(temp_config)
    collections = auto_import(images)

    gr.Info(
        f"HTRflow: processing {len(images)} {'image' if len(images) == 1 else 'images'}."
    )
    progress(0.1, desc="HTRflow: Processing")

    for collection in collections:
        if "labels" in temp_config:
            collection.set_label_format(**temp_config["labels"])

        collection.label = "HTRflow_demo_output"
        collection: Collection = pipe.run(collection, progress=progress)

    exported_files = tracking_exported_files(tmp_output_paths)

    time.sleep(0.5)
    progress(1, desc="HTRflow: Finish")
    gr.Info("HTRflow: Finish")

    yield collection, exported_files, gr.skip()


def tracking_exported_files(tmp_output_paths):
    """
    Look for files with specific extensions in the provided tmp_output_paths,
    including subdirectories. Eliminates duplicate files.

    Args:
        tmp_output_paths (list): List of temporary output directories to search.

    Returns:
        list: Unique paths of all matching files found in the directories.
    """
    accepted_extensions = {".txt", ".xml", ".json"}

    exported_files = set()

    print(tmp_output_paths)

    # TODO: fix so that we get the file extension for page and alto...

    for tmp_folder in tmp_output_paths:
        for ext in accepted_extensions:
            search_pattern = os.path.join(tmp_folder, "**", f"*{ext}")
            matching_files = glob.glob(search_pattern, recursive=True)
            exported_files.update(matching_files)

    return sorted(exported_files)


with gr.Blocks() as submit:
    collection_submit_state = gr.State()

    with gr.Column(variant="panel"):
        with gr.Group():
            with gr.Row():
                with gr.Column(scale=1):
                    batch_image_gallery = gr.Gallery(
                        file_types=["image"],
                        label="Upload the images you want to transcribe",
                        interactive=True,
                        object_fit="cover",
                    )

                with gr.Column(scale=1):
                    custom_template_yaml = gr.Code(
                        value="",
                        language="yaml",
                        label="Pipeline",
                        interactive=True,
                    )
        with gr.Row():
            run_button = gr.Button("Submit", variant="primary", scale=0, min_width=200)
            progess_bar = gr.Textbox(visible=False, show_label=False)
            collection_output_files = gr.Files(
                label="Output Files", scale=0, min_width=400, visible=False
            )

    @batch_image_gallery.upload(
        inputs=batch_image_gallery,
        outputs=[batch_image_gallery],
    )
    def validate_images(images):
        if len(images) > MAX_IMAGES:
            gr.Warning(f"Maximum images you can upload is set to: {MAX_IMAGES}")
            return gr.update(value=None)
        return images

    run_button.click(
        lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[progess_bar, collection_output_files],
    ).then(
        fn=run_htrflow,
        inputs=[custom_template_yaml, batch_image_gallery],
        outputs=[collection_submit_state, collection_output_files, progess_bar],
    ).then(
        lambda: (gr.update(visible=False), gr.update(visible=True)),
        outputs=[progess_bar, collection_output_files],
    )

# TODO: valudate yaml before submitting...?
# TODO: Add toast gr.Warning: Lose previues run...
