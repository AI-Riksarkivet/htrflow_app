import gradio as gr
import yaml
from htrflow.pipeline.pipeline import Pipeline
from htrflow.volume.volume import Collection


def run_htrflow(custom_template_yaml, collection, progress=gr.Progress()):
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

    pipe = Pipeline.from_config(config)

    collection: Collection = pipe.run(collection, progress=progress)

    gr.Info("HTRflow: Export complete!")

    yield collection, gr.skip()


with gr.Blocks() as export:
    collection = gr.State()

    gr.Markdown("## Export")
    with gr.Group():
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                selected_output = gr.Dropdown(
                    label="Export file format",
                    info="Select (multiple) what export format you want",
                    choices=["txt", "alto", "page", "json"],
                    multiselect=True,
                    interactive=True,
                )
                name_of_files = gr.Textbox(
                    label="File name",
                    info="All files will be given the same name with a suffix of the file extension",
                    placeholder="my_htr_file",
                )

            with gr.Column(scale=1):
                download_files = gr.Files(interactive=False)
    with gr.Row():
        export_button = gr.Button("Export", scale=0, min_width=200, variant="primary")

        @export_button.click(inputs=[], outputs=[])
        def blable():
            pass


# TODO: test pylaia works...
# TODO: add other pipeliens for other language like english and hebrew model?
# TODO: add other pipeliens for other language like english and hebrew model?
# TODO kolla över toast. toast vid export?
