import io
import logging
import os
import re
import time

import certifi
import fitz  # PyMuPDF
import gradio as gr
import pycurl
import yaml
import spaces

from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import init_step
from htrflow.volume.volume import Collection
from PIL import Image

from app.pipelines import PIPELINES
from gradio_i18n import gettext as _

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


def pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of PIL Image objects using PyMuPDF.
    Extracts full-resolution images with no DPI adjustment.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        list: List of PIL Image objects
    """
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pixmap = page.get_pixmap(alpha=False)
        img_data = pixmap.tobytes("jpeg")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)

    pdf_document.close()
    return images


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


def get_pipeline_description(pipeline: str, language: str = "en") -> str:
    """
    Get the description of the given pipeline in the specified language
    """
    desc = PIPELINES[pipeline]["description"]
    if isinstance(desc, dict):
        return str(desc.get(language, desc.get("en", "")))
    return str(desc)


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


def get_selected_example_image(event: gr.SelectData):
    """
    Get path to the selected example image with caption, and open in preview mode.
    """
    image_path = event.value["image"]["path"]
    caption = event.value["image"].get("orig_name") or os.path.basename(image_path)
    return gr.update(value=[(image_path, caption)], selected_index=0)


def get_selected_example_pipeline(event: gr.SelectData) -> str | None:
    """
    Get the name of the pipeline that corresponds to the selected image.
    """
    for name, details in PIPELINES.items():
        if event.value["image"]["orig_name"] in details.get("examples", []):
            return name


def get_image_from_image_id(image_id):
    url = f"https://lbiiif.riksarkivet.se/arkis!{image_id}/full/max/0/default.jpg"
    return gr.update(value=[(url, image_id)], selected_index=0)


def get_images_from_iiif_manifest(iiif_manifest_url, max_images=20, height=1200):
    """
    Read images from a v2/v3 IIIF manifest, limited to max_images.

    Arguments:
        iiif_manifest_url: URL to IIIF manifest
        height: Max height of returned images
        max_images: Maximum number of images to return (default: 20)
    """
    try:
        buffer = io.BytesIO()
        c = pycurl.Curl()

        c.setopt(c.URL, iiif_manifest_url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.MAXREDIRS, 5)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 10)
        c.setopt(c.NOSIGNAL, 1)
        c.setopt(c.USERAGENT, "curl/7.68.0")

        c.perform()

        http_code = c.getinfo(c.RESPONSE_CODE)
        if http_code != 200:
            raise Exception(f"HTTP Error: {http_code}")

        manifest = buffer.getvalue().decode("utf-8")
        c.close()

    except pycurl.error as e:
        error_code, error_msg = e.args
        raise Exception(
            f"Could not fetch IIIF manifest from {iiif_manifest_url} ({error_msg})"
        )

    pattern = r'(?P<identifier>https?://[^"\s]*)/(?P<region>[^"\s]*?)/(?P<size>[^"\s]*?)/(?P<rotation>!?\d*?)/(?P<quality>[^"\s]*?)\.(?P<format>jpg|tif|png|gif|jp2|pdf|webp)'
    images = set()

    for match in re.findall(pattern, manifest):
        identifier, _, _, _, _, format_ = match
        images.add(f"{identifier}/full/{height},/0/default.{format_}")
        if len(images) >= max_images:
            break

    return sorted(images)[:max_images], gr.update(visible=True)


with gr.Blocks() as submit:
    gr.Markdown(
        _(
            "Select or upload the image you want to transcribe. Most common image formats are supported and you can upload max 5 images at a time in this hosted demo."
        )
    )

    collection_submit_state = gr.State()

    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            batch_image_gallery = gr.Gallery(
                file_types=["image"],
                label=_("Image to transcribe"),
                interactive=True,
                object_fit="contain",
                allow_preview=True,
                preview=True,
                columns=3,
                height=400,
                rows=2,
            )

        with gr.Column(scale=1, variant="panel"):
            with gr.Tabs():
                with gr.Tab(_("Examples")):
                    examples = gr.Gallery(
                        all_example_images(),
                        show_label=False,
                        interactive=False,
                        allow_preview=False,
                        object_fit="scale-down",
                        min_width=250,
                        columns=3,
                        container=False,
                    )

                with gr.Tab(_("Image ID")):
                    image_id = gr.Textbox(
                        label=_("Upload by image ID"),
                        info=_(
                            "Use any image from our digitized archives by pasting its image ID found in the "
                            "<a href='https://sok.riksarkivet.se/bildvisning/R0002231_00005' target='_blank'>image viewer</a>. "
                            "Press enter to submit."
                        ),
                        placeholder="R0002231_00005",
                    )

                with gr.Tab(_("IIIF Manifest")):
                    with gr.Group():
                        iiif_manifest_url = gr.Textbox(
                            label=_("IIIF Manifest"),
                            info=_(
                                "Use an image from a IIIF manifest by pasting a IIIF manifest URL. Press enter to submit."
                            ),
                            placeholder="",
                            scale=0,
                        )
                        max_images_iiif_manifest = gr.Number(
                            value=20,
                            min_width=50,
                            scale=0,
                            label=_("Number of image to return from IIIF manifest"),
                            minimum=1,
                            visible=False,
                        )
                    iiif_gallery = gr.Gallery(
                        interactive=False,
                        columns=4,
                        allow_preview=False,
                        container=False,
                        show_label=False,
                        object_fit="scale-down",
                    )

                with gr.Tab(_("URL")):
                    image_url = gr.Textbox(
                        label=_("Image URL"),
                        info=_("Upload an image by pasting its URL."),
                        placeholder="https://example.com/image.jpg",
                    )

                with gr.Tab(_("PDF")):
                    pdf_file = gr.File(label=_("PDF"), file_types=[".pdf"])

                    pdf_gallery = gr.Gallery(
                        interactive=False,
                        columns=4,
                        allow_preview=False,
                        container=False,
                        show_label=False,
                        object_fit="scale-down",
                    )

    with gr.Column(variant="panel"):
        gr.Markdown(
            _(
                "Select a pipeline that best matches your image. The pipeline determines the processing workflow optimized for different text recognition tasks. "
                "If you select an example image, a suitable pipeline will be preselected automatically. However, you can edit the pipeline if you need to customize it further. "
                "Choosing the right pipeline significantly improves transcription quality."
            )
        )

        with gr.Row():
            with gr.Column(scale=0, min_width=250):
                pipeline_dropdown = gr.Dropdown(
                    choices=[
                        (_("Swedish - Spreads"), "Swedish - Spreads"),
                        (
                            _("Swedish - Single page and snippets"),
                            "Swedish - Single page and snippets",
                        ),
                        (
                            _("Norwegian - Single page and snippets"),
                            "Norwegian - Single page and snippets",
                        ),
                        (
                            _("Medieval - Single page and snippets"),
                            "Medieval - Single page and snippets",
                        ),
                        (
                            _("English - Single page and snippets"),
                            "English - Single page and snippets",
                        ),
                        (_("Custom"), "Custom"),
                    ],
                    value="Swedish - Spreads",
                    container=False,
                    elem_classes="pipeline-dropdown",
                )
            with gr.Column(scale=0, min_width=100):
                run_button = gr.Button(_("Run HTR"), variant="primary")

        pipeline_description = gr.HTML(
            value=get_pipeline_description("Swedish - Spreads", "en"),
            elem_classes="pipeline-info",
        )

        with gr.Row(visible=False) as edit_pipeline_column:
            with gr.Accordion(_("Edit Pipeline"), open=False):
                gr.Markdown(
                    _(
                        "The code snippet below is a YAML file that the HTRflow app uses to process the image. If you have chosen an "
                        'image from the "Examples" section, the YAML is already a pre-made template tailored to fit the example image.\n\n'
                        "Edit pipeline if needed:"
                    )
                )
                custom_template_yaml = gr.Code(
                    value=get_yaml("Swedish - Spreads"),
                    language="yaml",
                    container=False,
                )
                gr.HTML(
                    _(
                        'See the <a href="https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html#example-pipelines">documentation</a> for a detailed description on how to customize HTRflow pipelines.'
                    ),
                    elem_classes="pipeline-help",
                )

    @batch_image_gallery.upload(
        inputs=batch_image_gallery,
        outputs=[batch_image_gallery],
    )
    def validate_images(images):
        if len(images) > MAX_IMAGES:
            gr.Warning(f"{_('Maximum images you can upload is set to')}: {MAX_IMAGES}")
            return gr.update(value=None)

        processed_images = []
        for img in images:
            if isinstance(img, (list, tuple)) and len(img) >= 2:
                processed_images.append(img)
            elif isinstance(img, dict) and "name" in img:
                processed_images.append((img["name"], os.path.basename(img["name"])))
            elif isinstance(img, str):
                processed_images.append((img, os.path.basename(img)))
            else:
                processed_images.append(img)

        return gr.update(
            value=processed_images, selected_index=0 if processed_images else None
        )

    image_id.submit(get_image_from_image_id, image_id, batch_image_gallery).then(
        fn=lambda: "Swedish - Spreads", outputs=pipeline_dropdown
    )
    iiif_manifest_url.submit(
        get_images_from_iiif_manifest,
        [iiif_manifest_url, max_images_iiif_manifest],
        [iiif_gallery, max_images_iiif_manifest],
    )
    image_url.submit(
        lambda url: gr.update(value=[(url, url.split("/")[-1])], selected_index=0),
        image_url,
        batch_image_gallery,
    )

    pdf_file.upload(
        lambda imgs: pdf_to_images(imgs), inputs=pdf_file, outputs=pdf_gallery
    )

    run_button.click(
        fn=run_htrflow,
        inputs=[custom_template_yaml, batch_image_gallery],
        outputs=[collection_submit_state, batch_image_gallery],
    )

    examples.select(get_selected_example_image, None, batch_image_gallery)
    examples.select(get_selected_example_pipeline, None, pipeline_dropdown)

    iiif_gallery.select(get_selected_example_image, None, batch_image_gallery)
    pdf_gallery.select(get_selected_example_image, None, batch_image_gallery)

    pipeline_dropdown.change(
        fn=lambda x: (gr.update(visible=(x == "Custom")), get_yaml(x) if x else ""),
        inputs=pipeline_dropdown,
        outputs=[edit_pipeline_column, custom_template_yaml],
    )

    pipeline_dropdown.change(
        fn=get_pipeline_description,
        inputs=pipeline_dropdown,
        outputs=pipeline_description,
    )
