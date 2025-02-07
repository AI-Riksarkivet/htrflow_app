import logging
import os
import time

import gradio as gr
import yaml
from gradio_modal import Modal
from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import auto_import, init_step
from htrflow.volume.volume import Collection

logger = logging.getLogger(__name__)

# Max number of images a user can upload at once
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", 5))

# Example pipelines
PIPELINES = {
    "Running text (Swedish)": {
        "file": "app/assets/templates/nested.yaml",
        "description": "This pipeline works well on documents with multiple text regions.",
        "examples": [
            "R0003364_00005.jpg",
            "30002027_00008.jpg",
            "A0070302_00201.jpg",
        ],
    },
    "Letters and snippets (Swedish)": {
        "file": "app/assets/templates/simple.yaml",
        "description": "This pipeline works well on letters and other documents with only one text region.",
        "examples": [
            "451511_1512_01.jpg",
            "A0062408_00006.jpg",
            "C0000546_00085_crop.png",
            "A0073477_00025.jpg",
        ],
    },
}

# Setup the cache directory to point to the directory where the example images
# are located. The images must lay in the cache directory because otherwise they
# have to be reuploaded when drag-and-dropped to the input image widget.
GRADIO_CACHE = ".gradio_cache"
EXAMPLES_DIRECTORY = os.path.join(GRADIO_CACHE, "examples")

if os.environ.get("GRADIO_CACHE_DIR", GRADIO_CACHE) != GRADIO_CACHE:
    logger.warning("Setting GRADIO_CACHE_DIR to '%s' (overriding a previous value).")


class PipelineWithProgress(Pipeline):
    @classmethod
    def from_config(cls, config: dict[str, str]):
        """Init pipeline from config, ensuring the correct subclass is instantiated."""
        return cls([init_step(step["step"], step.get("settings", {})) for step in config["steps"]])

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

    progress(0, desc="HTRflow: Starting")
    time.sleep(0.3)

    if batch_image_gallery is None:
        gr.Warning("HTRflow: You must upload atleast 1 image or more")

    images = [temp_img[0] for temp_img in batch_image_gallery]

    pipe = PipelineWithProgress.from_config(config)
    collections = auto_import(images)

    gr.Info(f"HTRflow: processing {len(images)} {'image' if len(images) == 1 else 'images'}.")
    progress(0.1, desc="HTRflow: Processing")

    for collection in collections:
        if "labels" in config:
            collection.set_label_format(**config["labels"])

        collection.label = "HTRflow_demo_output"
        collection: Collection = pipe.run(collection, progress=progress)

    progress(1, desc="HTRflow: Finish")
    time.sleep(1)
    gr.Info("HTRflow: Finish")

    yield collection, gr.skip()


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
    print([event.value["image"]["path"]])
    return [event.value["image"]["path"]]


def get_selected_example_pipeline(event: gr.SelectData) -> str | None:
    """
    Get the name of the pipeline that corresponds to the selected image.
    """
    for name, details in PIPELINES.items():
        if event.value["image"]["orig_name"] in details.get("examples", []):
            return name


with gr.Blocks() as submit:
    gr.Markdown("# Upload")
    gr.Markdown("Start Here! ")
    gr.Markdown(
        "First you upload upload 1 image or multiple images (max 5 images). You can also use directly the Image ID from the National Archives of Sweden to request an image"
    )
    gr.Markdown(
        "Afterward, choice a template from the examples based on your material. This will configure a certain pipeline that fits your image."
    )

    collection_submit_state = gr.State()
    with gr.Group():
        with gr.Row(equal_height=True):
            with gr.Column(scale=5):
                batch_image_gallery = gr.Gallery(
                    file_types=["image"],
                    label="Image to transcribe",
                    interactive=True,
                    object_fit="scale-down",
                    scale=3,
                    preview=True,
                )

            with gr.Column(scale=2):
                examples = gr.Gallery(
                    all_example_images(),
                    label="Examples",
                    interactive=False,
                    allow_preview=False,
                    object_fit="scale-down",
                    min_width=250,
                )

                image_iiif_url = gr.Textbox(
                    label="Images from the National Archives of Sweden",
                    info="e.g <a href='https://sok.riksarkivet.se/bildvisning/R0002231_00005' target='_blank'>R0002231_00005</a> - Press enter to submit",
                    placeholder="R0002231_00005",
                )

                iiif_image_placeholder = gr.Image(visible=False)

    with gr.Column(variant="panel", elem_classes="pipeline-panel"):
        gr.HTML("Pipeline", elem_classes="pipeline-header", padding=False)

        with gr.Row():
            with gr.Column(scale=0):
                pipeline_dropdown = gr.Dropdown(
                    PIPELINES,
                    container=False,
                    min_width=240,
                    scale=0,
                    elem_classes="pipeline-dropdown",
                )
            with gr.Column():
                with gr.Row():
                    pipeline_description = gr.HTML(
                        value=get_pipeline_description,
                        inputs=pipeline_dropdown,
                        elem_classes="pipeline-description",
                        padding=False,
                    )
                    help_button = gr.Button(
                        "Edit Pipeline",
                        scale=0,
                    )

                with Modal(visible=False) as help_modal:
                    custom_template_yaml = gr.Code(
                        value=get_yaml,
                        inputs=pipeline_dropdown,
                        language="yaml",
                        container=False,
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

    @batch_image_gallery.upload(
        inputs=batch_image_gallery,
        outputs=[batch_image_gallery],
    )
    def validate_images(images):
        if len(images) > MAX_IMAGES:
            gr.Warning(f"Maximum images you can upload is set to: {MAX_IMAGES}")
            return gr.update(value=None)
        return images

    def return_iiif_url(image_iiif_url):
        return f"https://lbiiif.riksarkivet.se/arkis!{image_iiif_url}/full/max/0/default.jpg"

    image_iiif_url.submit(fn=return_iiif_url, inputs=image_iiif_url, outputs=iiif_image_placeholder).then(
        fn=lambda x: [x], inputs=iiif_image_placeholder, outputs=batch_image_gallery
    )

    run_button.click(
        lambda: gr.update(visible=True),
        outputs=[progess_bar],
    ).then(
        fn=run_htrflow,
        inputs=[custom_template_yaml, batch_image_gallery],
        outputs=[collection_submit_state, progess_bar],
    ).then(
        lambda: gr.update(visible=False),
        outputs=[progess_bar],
    )

    examples.select(get_selected_example_image, None, batch_image_gallery)
    examples.select(get_selected_example_pipeline, None, pipeline_dropdown)

    help_button.click(lambda: Modal(visible=True), None, help_modal)
