import logging
import os
import re
import time

import gradio as gr
import spaces
import requests
import yaml
from gradio_modal import Modal
from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import init_step
from htrflow.volume.volume import Collection

from app.pipelines import PIPELINES

logger = logging.getLogger(__name__)

# Max number of images a user can upload at once
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", 5))

# Setup the cache directory to point to the directory where the example images
# are located. The images must lay in the cache directory because otherwise they
# have to be reuploaded when drag-and-dropped to the input image widget.
GRADIO_CACHE = ".gradio_cache"
EXAMPLES_DIRECTORY = os.path.join(GRADIO_CACHE, "examples")

if os.environ.get("GRADIO_CACHE_DIR", GRADIO_CACHE) != GRADIO_CACHE:
    os.environ["GRADIO_CACHE_DIR"] = GRADIO_CACHE
    logger.warning("Setting GRADIO_CACHE_DIR to '%s' (overriding a previous value).")


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


@spaces.GPU
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

    collection = Collection(images)

    pipe = PipelineWithProgress.from_config(config)

    gr.Info(
        f"HTRflow: processing {len(images)} {'image' if len(images) == 1 else 'images'}."
    )
    progress(0.1, desc="HTRflow: Processing")

    collection.label = "demo_output"

    collection = pipe.run(collection, progress=progress)

    progress(1, desc="HTRflow: Finish, redirecting to 'Results tab'")
    time.sleep(2)
    gr.Info("Completed succesfully ✨")

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
    return [event.value["image"]["path"]]


def get_selected_example_pipeline(event: gr.SelectData) -> str | None:
    """
    Get the name of the pipeline that corresponds to the selected image.
    """
    for name, details in PIPELINES.items():
        if event.value["image"]["orig_name"] in details.get("examples", []):
            return name


def get_image_from_image_url(input_value):
    """
    Get URL of the image from either an image_id (from Riksarkivet) or an image_url directly.
    If input_value is an image_id, it constructs the IIIF URL.
    If input_value is an image_url, it returns the URL as-is.
    """

    if input_value.startswith("http"):
        return [input_value]
    else:
        input_value = input_value.split(",")

        return [
            (
                f"https://lbiiif.riksarkivet.se/arkis!{item.strip()}/full/max/0/default.jpg"
            )
            for item in input_value
        ]


def is_image_id(input_value: str) -> bool:
    """
    Check if `input_value` is a valid Riksarkivet image ID
    """
    return bool(re.match(r"\w{8}_\w{5}", input_value))


def get_images_from_iiif_manifest(manifest: dict, height: int=1600):
    """
    Read all images from a v2/v3 IIIF manifest.

    Arguments:
        manifest: IIIF manifest
        height: Max height of returned images.
    """
    # Hacky solution to get all images regardless of API version - treat
    # the manifest as a string and match everything that looks like an IIIF
    # image URL.
    manifest = str(manifest)
    pattern = r"(?P<identifier>https?://\S*)/(?P<region>\S*?)/(?P<size>\S*?)/(?P<rotation>!?\d*?)/(?P<quality>\S*?)\.(?P<format>jpg|tif|png|gif|jp2|pdf|webp)"

    images = set()  # create a set to eliminate duplicates (e.g. thumbnails and fullsize images)
    for match in re.findall(pattern, manifest):
        identifier, _, _, _, _, format_ = match
        images.add(f"{identifier}/full/{height},/0/default.{format_}")
    return sorted(images)


def handle_url_input(input_value: str) -> list[str]:
    """
    Get images from a string input.

    Arguments:
        input_value: A string, which is any of the following:
            - A Riksarkivet image ID (e.g. A0068688_00123)
            - A IIIF manifest URI
            - An image URL

    Returns:
        A list of image URLs.
    """
    # Does it look like an image ID? => Fetch the image from Riksarkivet's IIIF.
    if is_image_id(input_value):
        return [f"https://lbiiif.riksarkivet.se/arkis!{input_value}/full/max/0/default.jpg"]

    # Does the URL return JSON? => Treat it like a IIIF manifest.
    try:
        manifest = requests.get(input_value, timeout=10).json()
        return get_images_from_iiif_manifest(manifest)
    except (requests.HTTPError, requests.JSONDecodeError):
        pass

    # Else treat it as an image URL.
    return [input_value]


def select_uploaded_image(selected_images, event: gr.SelectData):
    """
    Select an uploaded image.

    Move the selected (clicked) image from the uploaded image gallery
    to the selected image gallery.
    """
    selected_images = selected_images or []
    paths = [path for path, _ in selected_images]
    if event.value["image"]["path"] not in paths:
        selected_images.append(event.value["image"]["path"])
    return selected_images[-MAX_IMAGES:]


def deselect_selected_image(selected_images, event: gr.SelectData):
    """
    Deselect (remove) a previously selected image.
    """
    selected_images = selected_images or []
    for image in selected_images:
        path, _ = image
        if path == event.value["image"]["path"]:
            selected_images.remove(image)

    # When an image is removed from the gallery, the selected index is not updated, which
    # leaves a blue box around the new image at the deleted image's index. Example:
    # you have three images, img0, img1 and img2 and you click img1 to delete it:
    #
    #   img0 [img1] img2
    #
    # When img1 is removed, the new gallery looks like this:
    #
    #   img0 [img2]
    #
    # Which means that img2 is "selected", and if you try to delete (i.e. click/select) it,
    # nothing will happen. To avoid it, we need to update/remove the selected index too. For
    # some reason it doesn't work to set the selected index to None, but setting it to a
    # sufficiently large index achieves the wanted effect.
    return gr.update(value=selected_images, selected_index=1000)


def open_image_selector_modal(uploaded_images):
    """
    Open image selector modal if needed (i.e. len(uploaded_images) > MAX_IMAGES)
    """
    visible = uploaded_images is not None and len(uploaded_images) > MAX_IMAGES
    return Modal(visible=visible)


def move_uploaded_to_selected_if_possible(uploaded_images):
    """
    Select all uploaded images if len(uploaded_images) <= MAX_IMAGES
    """
    if uploaded_images is None or len(uploaded_images) <= MAX_IMAGES:
        return uploaded_images
    return []


with gr.Blocks() as submit:
    with gr.Row():
        with gr.Column():
            gr.Markdown("# Upload")
            gr.Markdown(
                "Select or upload the image you want to transcribe. You can upload up to five images at a time. \n "
                "Alternatively, you can choose from example images from the gallery or use Image_IDs."
            )

    collection_submit_state = gr.State()
    with gr.Group():
        with gr.Row(
            equal_height=True,
        ):
            with gr.Column(scale=2):
                batch_image_gallery = gr.Gallery(
                    file_types=["image"],
                    label="Image to transcribe",
                    interactive=True,
                    object_fit="scale-down",
                )

            with gr.Column(scale=1):
                examples = gr.Gallery(
                    all_example_images(),
                    label="Examples",
                    interactive=False,
                    allow_preview=False,
                    object_fit="scale-down",
                    min_width=250,
                    height="100%",
                    columns=4,
                )
                # with Modal(visible=False) as edit_pipeline_modal:

                image_iiif_url = gr.Textbox(
                    label="From the web",
                    info="Paste an image URL, IIIF manifest or Riksarkivet image ID and press enter to submit.",
                    placeholder="www.example.com/image.jpg",
                )

    with gr.Column(variant="panel", elem_classes="pipeline-panel"):
        gr.Markdown("## Settings")
        gr.Markdown(
            "Select a pipeline that best matches your image. The pipeline determines the processing workflow optimized for different handwritten text recognition tasks. "
            "If you select an example image, a suitable pipeline will be preselected automatically. However, you can edit the pipeline if you need to customize it further. "
            "Choosing the right pipeline significantly improves transcription quality. "
        )

        with gr.Row():
            with gr.Column(scale=0):
                pipeline_dropdown = gr.Dropdown(
                    PIPELINES,
                    container=False,
                    min_width=240,
                    scale=0,
                    elem_classes="pipeline-dropdown",
                )

            with gr.Column(scale=0, min_width=100):
                edit_pipeline_button = gr.Button("Edit", scale=0)
            with gr.Column(scale=3):
                progess_bar = gr.Textbox(visible=False, show_label=False)
            with gr.Column(scale=0, min_width=20):
                pass

        pipeline_description = gr.HTML(
            value=get_pipeline_description,
            inputs=pipeline_dropdown,
            elem_classes="pipeline-info",
            padding=False,
        )

    with Modal(
        visible=False,
    ) as edit_pipeline_modal:
        with gr.Column():
            gr.Markdown(
                """
                ## Edit Pipeline
                The code snippet below is a YAML file that the HTRflow app uses to process the image. If you have chosen an
                image from the "Examples" section, the YAML is already a pre-made template tailored to fit the example image.

                Edit pipeline if needed:
                """
            )
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
        run_button = gr.Button("Transcribe", variant="primary", scale=0, min_width=200)

    with Modal(visible=False, allow_user_close=False) as image_selector_modal:
        gr.Markdown("# Select images")
        gr.Markdown(f"The number of images exceeds the app's limit of {MAX_IMAGES} images. Please select up to {MAX_IMAGES} images to continue.")

        uploaded_images_gallery = gr.Gallery(
            file_types=["image"],
            object_fit="scale-down",
            allow_preview=False,
            interactive=False,
            columns=6,
            label="Uploaded images",
            height="100%"
        )
        selected_images_gallery = gr.Gallery(
            file_types=["image"],
            object_fit="scale-down",
            allow_preview=False,
            interactive=False,
            columns=MAX_IMAGES,
            height="100%",
            label="Selected images",
            visible=False
        )

        with gr.Row():
            cancel_button = gr.Button("Cancel", variant="secondary")
            ok_button = gr.Button("Continue", variant="primary")

    # All incoming images (uploaded or URL) are put in `uploaded_images_gallery`
    batch_image_gallery.upload(lambda images: images, batch_image_gallery, uploaded_images_gallery)
    image_iiif_url.submit(handle_url_input, image_iiif_url, uploaded_images_gallery).then(fn=lambda: "Swedish - Spreads", outputs=pipeline_dropdown)
    image_iiif_url.submit(open_image_selector_modal, uploaded_images_gallery, image_selector_modal)
    image_iiif_url.submit(move_uploaded_to_selected_if_possible, uploaded_images_gallery, selected_images_gallery)

    # Move uploaded images to `selected_images`, opening the modal if needed
    uploaded_images_gallery.change(open_image_selector_modal, uploaded_images_gallery, image_selector_modal)
    uploaded_images_gallery.change(move_uploaded_to_selected_if_possible, uploaded_images_gallery, selected_images_gallery)

    # Image selector modal logic
    uploaded_images_gallery.select(select_uploaded_image, selected_images_gallery, selected_images_gallery)
    selected_images_gallery.select(deselect_selected_image, selected_images_gallery, selected_images_gallery)
    selected_images_gallery.change(lambda images: gr.update(visible=bool(images)), selected_images_gallery, selected_images_gallery)
    selected_images_gallery.change(lambda images: images, selected_images_gallery, batch_image_gallery)
    selected_images_gallery.change(lambda images: gr.update(interactive=bool(images)), selected_images_gallery, ok_button)

    # Image selector modal buttons
    cancel_button.click(lambda: Modal(visible=False), None, image_selector_modal)
    cancel_button.click(lambda: [], None, selected_images_gallery)
    cancel_button.click(lambda: gr.update(value=None), None, batch_image_gallery)
    cancel_button.click(lambda: gr.update(value=None), None, uploaded_images_gallery)
    ok_button.click(lambda: Modal(visible=False), None, image_selector_modal)

    # Run HTRflow on selected images
    run_button.click(fn=run_htrflow, inputs=[custom_template_yaml, selected_images_gallery], outputs=[collection_submit_state, batch_image_gallery])

    examples.select(get_selected_example_image, None, batch_image_gallery)
    examples.select(get_selected_example_image, None, uploaded_images_gallery)
    examples.select(get_selected_example_pipeline, None, pipeline_dropdown)

    edit_pipeline_button.click(lambda: Modal(visible=True), None, edit_pipeline_modal)
