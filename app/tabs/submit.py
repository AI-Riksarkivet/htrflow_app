import glob
import time
import uuid
import gradio as gr
from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import init_step
import os
import logging
from htrflow.volume.volume import Collection

from htrflow.pipeline.steps import auto_import
import yaml

logger = logging.getLogger(__name__)

# Max number of images a user can upload at once
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", 5))

# Example pipelines
PIPELINES = {
    "Running text (Swedish)": {
        "file": "app/assets/templates/2_nested.yaml",
        "description": "This pipeline works well on documents with multiple text regions.",
        "examples": [
            "R0003364_00005.jpg",
            "30002027_00008.jpg",
            "A0070302_00201.jpg",
        ]
    },
    "Letters and snippets (Swedish)": {
        "file": "app/assets/templates/1_simple.yaml",
        "description": "This pipeline works well on letters and other documents with only one text region.",
        "examples": [
            "451511_1512_01.jpg",
            "A0062408_00006.jpg",
            "C0000546_00085_crop.png",
            "A0073477_00025.jpg",
        ]
    },
}

# Setup the cache directory to point to the directory where the example images
# are located. The images must lay in the cache directory because otherwise they
# have to be reuploaded when drag-and-dropped to the input image widget.
GRADIO_CACHE = ".gradio_cache"
EXAMPLES_DIRECTORY = os.path.join(GRADIO_CACHE, "examples")

if os.environ.get("GRADIO_CACHE_DIR", GRADIO_CACHE) != GRADIO_CACHE:
    logger.warning(
        "Setting GRADIO_CACHE_DIR to '%s' (overriding a previous value)."
    )


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


def get_pipeline_description(pipeline: str) -> str:
    """
    Get the description of the given pipeline
    """
    return PIPELINES[pipeline]["description"]


def get_yaml(pipeline: str) -> str:
    """
    Get the yaml file for the given pipeline

    Args:
        pipeline: Name of pipeline (must be a key in the PIPELINES directory)
    """
    with open(PIPELINES[pipeline]["file"], "r") as f:
        pipeline = f.read()
    return pipeline


def all_example_images() -> list[str]:
    """
    Get paths to all example images.
    """
    examples = []
    for pipeline in PIPELINES.values():
        for example in pipeline.get("examples", []):
            examples.append(os.path.join(EXAMPLES_DIRECTORY, example))
    return examples


def get_selected_example_image(event: gr.SelectData) -> str:
    """
    Get path to the selected example image.
    """
    return [event.value["image"]["path"]]


def get_selected_example_pipeline(event: gr.SelectData) -> str | None:
    """
    Get the name of the pipeline that corresponds to the selected image.
    """
    for name, details in PIPELINES.items():
        if event.value["image"]["orig_name"] in details.get("examples", []):
            return name


with gr.Blocks() as submit:
    collection_submit_state = gr.State()

    with gr.Group():
        with gr.Row(equal_height=True):
            batch_image_gallery = gr.Gallery(
                file_types=["image"],
                label="Image to transcribe",
                interactive=True,
                object_fit="scale-down",
                scale=3,
                preview=True
            )

            examples = gr.Gallery(
                all_example_images(),
                label="Examples",
                interactive=False,
                allow_preview=False,
                object_fit="scale-down",
                min_width=250,
            )

    with gr.Column(variant="panel", elem_classes="pipeline-panel"):
        gr.HTML("Pipeline", elem_classes="pipeline-header", padding=False)

        with gr.Row():
            pipeline_dropdown = gr.Dropdown(
                PIPELINES, container=False, min_width=240, scale=0, elem_classes="pipeline-dropdown"
            )
            pipeline_description = gr.HTML(
                value=get_pipeline_description, inputs=pipeline_dropdown, elem_classes="pipeline-description", padding=False
            )

        with gr.Group():
            with gr.Accordion("Edit pipeline", open=False):
                custom_template_yaml = gr.Code(
                    value=get_yaml, inputs=pipeline_dropdown, language="yaml", container=False
                )
                url = "https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html#example-pipelines"
                gr.HTML(
                    f'See the <a href="{url}">documentation</a> for a detailed description on how to customize HTRflow pipelines.',
                    padding=False,
                    elem_classes="pipeline-help",
                )

    with gr.Row():
        run_button = gr.Button("Submit", variant="primary", scale=0, min_width=200)
        progess_bar = gr.Textbox(visible=False, show_label=False)
        collection_output_files = gr.Files(label="Output Files", scale=0, min_width=400, visible=False)

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

    examples.select(get_selected_example_image, None, batch_image_gallery)
    examples.select(get_selected_example_pipeline, None, pipeline_dropdown)

# TODO: valudate yaml before submitting...?
# TODO: Add toast gr.Warning: Lose previues run...
