import gradio as gr
import os
import re


def get_sorted_files(folder, extensions):
    """Retrieve sorted files by numeric value in their names."""
    return sorted(
        [
            os.path.join(folder, file)
            for file in os.listdir(folder)
            if file.lower().endswith(extensions)
        ],
        key=lambda x: (
            int(re.search(r"\d+", os.path.basename(x)).group())
            if re.search(r"\d+", os.path.basename(x))
            else float("inf")
        ),
    )


def filter_files_by_prefix(files, prefix_pattern):
    """Filter files based on a regex prefix pattern."""
    return [file for file in files if re.match(prefix_pattern, os.path.basename(file))]


def clean_file_names(files, prefix_to_remove):
    """Clean filenames by removing a specific prefix if present."""
    return [
        (
            os.path.basename(file)[len(prefix_to_remove) :]
            if os.path.basename(file).startswith(prefix_to_remove)
            else os.path.basename(file)
        )
        for file in files
    ]


def get_yaml_content(yaml_path):
    """Read and return YAML content from a file."""
    if os.path.isfile(yaml_path):
        with open(yaml_path, "r") as file:
            return file.read()
    return "YAML content not available"


TEMPLATE_IMAGE_FOLDER = "app/assets/images"
TEMPLATE_YAML_FOLDER = "app/assets/templates"

image_files = get_sorted_files(
    TEMPLATE_IMAGE_FOLDER, (".png", ".jpg", ".jpeg", ".webp")
)
yaml_files = get_sorted_files(TEMPLATE_YAML_FOLDER, (".yaml",))

yaml_files_numbered = filter_files_by_prefix(yaml_files, r"^\d")
yaml_files_c_letter = filter_files_by_prefix(yaml_files, r"^[cC]")

name_yaml_files_c_letter_cleaned = clean_file_names(yaml_files_c_letter, "c_")
name_to_yaml_map = dict(zip(name_yaml_files_c_letter_cleaned, yaml_files_c_letter))


def get_yaml_content(yaml_path):
    if yaml_path and os.path.isfile(yaml_path):
        with open(yaml_path, "r") as file:
            return file.read()
    return "YAML content not available"


with gr.Blocks() as templating_block:
    with gr.Row(variant="panel"):
        with gr.Column(scale=2):
            with gr.Row():
                dropdown_selection_template = gr.Dropdown(
                    label="Choose template",
                    info="Choice a suitable template for your material",
                    value="Simple",
                    choices=["Simple", "Nested", "Custom"],
                    multiselect=False,
                    interactive=True,
                )

                custom_dropdown_selection_template = gr.Dropdown(
                    label="Custom template",
                    info="Choice a different custom templates...",
                    value=name_yaml_files_c_letter_cleaned[0],
                    choices=name_yaml_files_c_letter_cleaned,
                    multiselect=False,
                    interactive=True,
                    visible=False,
                )

            with gr.Group():
                with gr.Row():
                    with gr.Column(scale=1):
                        template_image = gr.Image(
                            label="Example Templates", value=image_files[0], height=400
                        )
                    with gr.Column(scale=1):
                        template_output_yaml_code = gr.Code(
                            language="yaml",
                            label="Pipeline",
                            interactive=True,
                            visible=True,
                        )
    docs_link = gr.HTML(
        value='<p><a href="https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html#example-pipelines" target="_blank">📚 Click here 📚</a> for a detailed description on how to customize the configuration for HTRflow</p>',
        visible=True,
    )

    @dropdown_selection_template.select(
        inputs=dropdown_selection_template,
        outputs=[
            template_image,
            template_output_yaml_code,
            custom_dropdown_selection_template,
        ],
    )
    def on_template_select(dropdown_selection_template):
        if dropdown_selection_template == "Simple":
            yaml_content = get_yaml_content(yaml_files_numbered[0])
            return image_files[0], yaml_content, gr.update(visible=False)
        elif dropdown_selection_template == "Nested":
            yaml_content = get_yaml_content(yaml_files_numbered[1])
            return image_files[1], yaml_content, gr.update(visible=False)
        elif dropdown_selection_template == "Custom":
            yaml_content = get_yaml_content(yaml_files_c_letter[0])
            return image_files[2], yaml_content, gr.update(visible=True)
        else:
            return gr.Error(
                f"{dropdown_selection_template} - is not a valid Template selection"
            )

    @custom_dropdown_selection_template.select(
        inputs=custom_dropdown_selection_template,
        outputs=[template_output_yaml_code],
    )
    def on_custom_template_select(custom_template_selection):
        yaml_path = name_to_yaml_map.get(custom_template_selection)

        if yaml_path:
            yaml_content = get_yaml_content(yaml_path)
            return yaml_content
        else:
            return gr.Error(
                f"{custom_template_selection} - is not a valid Custom Template selection"
            )

    @dropdown_selection_template.select(
        inputs=dropdown_selection_template,
        outputs=[template_output_yaml_code],
    )
    def check_for_custom_template(dropdown_selection_template):
        if dropdown_selection_template == "Custom":
            return gr.update(visible=True)
        else:
            return gr.skip()

    templating_block.load(
        fn=on_template_select,
        inputs=dropdown_selection_template,
        outputs=[
            template_image,
            template_output_yaml_code,
            custom_dropdown_selection_template,
        ],
    )

# TODO: Vi vill ändra namn på på fileerna så man ser vilken extension (format) fileerna är i
# rimes_test - kopia 2_page
# .xml
# 3.5 KB ⇣
# ×
# rimes_test - kopia
# .xml
# 3.5 KB ⇣
# ×
# rimes_test
# .xml
# 3.4 KB ⇣
# ×
# rimes_test - kopia 2
# .xml
# 1.7 KB ⇣
# ×
# rimes_test - kopia
# .xml
# 1.7 KB ⇣
# ×
# rimes_test
# .xml
