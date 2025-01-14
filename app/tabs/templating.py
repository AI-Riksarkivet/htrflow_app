import gradio as gr
import os
import re

template_image_folder = "app/assets/images"
template_yaml_folder = "app/assets/templates"

image_files = sorted(
    [
        os.path.join(template_image_folder, img)
        for img in os.listdir(template_image_folder)
        if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ],
    key=lambda x: (
        int(re.search(r"\d+", os.path.basename(x)).group())
        if re.search(r"\d+", os.path.basename(x))
        else float("inf")
    ),
)

yaml_files = [
    os.path.join(template_yaml_folder, yml)
    for yml in os.listdir(template_yaml_folder)
    if yml.lower().endswith(".yaml")
]

yaml_files_numbered = sorted(
    [yml for yml in yaml_files if re.match(r"^\d", os.path.basename(yml))],
    key=lambda x: (
        int(re.search(r"\d+", os.path.basename(x)).group())
        if re.search(r"\d+", os.path.basename(x))
        else float("inf")
    ),
)

yaml_files_c_letter = [
    yml for yml in yaml_files if re.match(r"^[cC]", os.path.basename(yml))
]

name_yaml_files_c_letter_cleaned = [
    (
        os.path.basename(yml)[2:]
        if os.path.basename(yml).startswith("c_")
        else os.path.basename(yml)
    )
    for yml in yaml_files_c_letter
]


def get_yaml_content(yaml_path):
    if yaml_path and os.path.isfile(yaml_path):
        with open(yaml_path, "r") as file:
            return file.read()
    return "YAML content not available"


with gr.Blocks() as templating_block:
    with gr.Row(variant="panel"):
        with gr.Column(scale=2):
            dropdown_selection_template = gr.Dropdown(
                label="Choice template",
                info="template info",
                value="Simple",
                choices=["Simple", "Nested", "Custom"],
                max_choices=1,
                interactive=True,
            )
            template_image = gr.Image(
                label="Example Templates", value=image_files[0], height=400
            )

            custom_dropdown = gr.Dropdown(
                label="Custom template",
                info="Choice a different custom templates...",
                value=name_yaml_files_c_letter_cleaned[0],
                choices=name_yaml_files_c_letter_cleaned,
                max_choices=1,
                interactive=True,
                visible=False,
            )

            output_yaml_code = gr.Code(
                language="yaml",
                label="yaml",
                interactive=True,
                visible=True,
                lines=15,
            )

    @dropdown_selection_template.select(
        inputs=dropdown_selection_template,
        outputs=[template_image, output_yaml_code, custom_dropdown],
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

    templating_block.load(
        fn=on_template_select,
        inputs=dropdown_selection_template,
        outputs=[template_image, output_yaml_code, custom_dropdown],
    )
