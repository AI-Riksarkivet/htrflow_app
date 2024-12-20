import gradio as gr
import pandas as pd

from app.assets.examples import DemoImages

images_for_demo = DemoImages()


def toggle_visibility_default_templates(selected_option):
    return [
        gr.update(visible=(selected_option == "Simple layout")),
        gr.update(visible=(selected_option == "Nested segmentation")),
        gr.update(visible=(selected_option == "Tables")),
        selected_option,
    ]


def dummy_revealer(reveal_bool):
    if reveal_bool == 0:
        return gr.update(visible=False)
    else:
        return gr.update(visible=True)


def submit_button_pipeline_fn(method, input_image, yaml_str):
    data = {"transcription": ["Example transcription"], "prediction score": [0.95]}

    df = pd.DataFrame(data)

    # HTRflow code here

    serialized_files = (
        "https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/refs/heads/main/app_project_line.png"
    )

    return f"Selected Option: {method}", input_image, serialized_files, gr.update(visible=True), df


def htr_image_placehholder(txt, method, image):
    needs_yaml_to_forward_tohtrflow_ = """steps:
"""
    print(method)

    return txt, method, image


def get_yaml_button_fn(
    method,
    output_formats,
    simple_segment_model=None,
    simple_htr_model=None,
    simple_htr_model_type=None,
    simple_segment_model_type=None,
    nested_segment_model_1=None,
    nested_segment_model_2=None,
    nested_htr_model=None,
    nested_segment_model_1_type=None,
    nested_segment_model_2_type=None,
    nested_htr_model_type=None,
):
    if method == "Simple layout":
        yaml_value = f"""steps:
  - step: Segmentation
    settings:
      model: {simple_htr_model_type}
      model_settings:
        model: {simple_segment_model}
  - step: TextRecognition
    settings:
      model: {simple_segment_model_type}
      model_settings:
        model: {simple_htr_model}
  - step: OrderLines
"""
    elif method == "Nested segmentation":
        yaml_value = f"""steps:
  - step: Segmentation
    settings:
      model: {nested_segment_model_1_type}
      model_settings:
        model: {nested_segment_model_1}
  - step: Segmentation
    settings:
      model: {nested_segment_model_2_type}
      model_settings:
        model: {nested_segment_model_2}
  - step: TextRecognition
    settings:
      model: {nested_htr_model_type}
      model_settings:
        model: {nested_htr_model}
  - step: OrderLines
"""
    else:
        return gr.Error("Invalid method or not yet supported.")

    export_steps = ""
    for output_format in output_formats:
        export_steps += f"""  - step: Export
    settings:
      format: {output_format}
      dest: {output_format}-outputs
"""

    yaml_value += export_steps

    return yaml_value


output_image_placehholder = gr.Image(label="Output image", height=500, show_share_button=True)
markdown_selected_option = gr.Markdown(container=True)

inital_state_selection_option = "Simple layout"

with gr.Blocks() as htrflow_pipeline:
    with gr.Row(variant="panel"):
        with gr.Column():
            # gr.Markdown("<h2>Control Panel</h2>")
            with gr.Tabs():
                with gr.Tab("Templates"):
                    with gr.Group():
                        example_text_input_placeholder = gr.Markdown(visible=False, container=False)
                        example_method_input_placeholder = gr.Markdown(visible=False, container=False)
                        example_text_output_placeholder = gr.Markdown(visible=False, container=False)

                        selected_option = gr.State(inital_state_selection_option)
                        dummy_none = gr.State(0)

                        user_image_input = gr.Image(
                            interactive=True, sources=["upload", "clipboard"], label="Input image", height=300
                        )

                        template_method_radio = gr.Dropdown(
                            [inital_state_selection_option, "Nested segmentation", "Tables"],
                            value=inital_state_selection_option,
                            label="Select template",
                            info="Will add more templates later!",
                        )

                        with gr.Row() as simple_pipeline:
                            with gr.Column():
                                with gr.Row():
                                    simple_segment_model = gr.Textbox(
                                        "model1", label="Segmentation", info="Info about the Segmentation model"
                                    )
                                    simple_segment_model_type = gr.Dropdown(
                                        choices=["yolo"], value="yolo", label="Segmentation", info="Model"
                                    )
                                with gr.Row():
                                    simple_htr_model = gr.Textbox(
                                        "model1", label="HTR", info="Info about the HTR model"
                                    )
                                    simple_htr_model_type = gr.Dropdown(
                                        choices=["TrOCR"], value="TrOCR", label="HTR", info="Model"
                                    )

                        with gr.Row(visible=False) as nested_pipeline:
                            with gr.Column():
                                with gr.Row():
                                    nested_segment_model_1 = gr.Textbox(
                                        "model1", label="Segmentation", info="Info about the Segmentation model"
                                    )
                                    nested_segment_model_1_type = gr.Dropdown(
                                        choices=["yolo"], value="yolo", label="Segmentation", info="Model"
                                    )
                                with gr.Row():
                                    nested_segment_model_2 = gr.Textbox(
                                        "model2", label="Segmentation", info="Info about the Segmentation model"
                                    )
                                    nested_segment_model_2_type = gr.Dropdown(
                                        choices=["yolo"], value="yolo", label="Segmentation", info="Model"
                                    )
                                with gr.Row():
                                    nested_htr_model = gr.Textbox(
                                        "model1", label="HTR", info="Info about the HTR model"
                                    )
                                    nested_htr_model_type = gr.Dropdown(
                                        choices=["TrOCR"], value="TrOCR", label="HTR", info="Model"
                                    )

                        with gr.Row(visible=False) as table_pipeline:
                            with gr.Column():
                                gr.Textbox("WIP")
                        with gr.Row():
                            output_formats = gr.Dropdown(
                                choices=["txt", "alto", "page"],
                                value="txt",
                                multiselect=True,
                                label="Serialized Output",
                                info="Supported format are: ...",
                            )

                    with gr.Row():
                        submit_button_pipeline = gr.Button("Submit", variant="primary", scale=0)
                        get_yaml_button = gr.Button("Get Yaml", variant="secondary", scale=0)

                with gr.Tab("Examples") as examples_tab:
                    # TODO:  Perhaps we should move examples to a seperate tab for simplicity?
                    gr.Examples(
                        fn=htr_image_placehholder,
                        examples=images_for_demo.examples_list,
                        inputs=[
                            example_text_input_placeholder,
                            example_method_input_placeholder,
                            user_image_input,
                        ],
                        outputs=[example_text_output_placeholder, markdown_selected_option, output_image_placehholder],
                        cache_examples=True,
                        cache_mode="lazy",
                        label="Example images",
                        examples_per_page=7,
                    )

        with gr.Column():
            # gr.Markdown("<h2>Output Panel</h2>")
            with gr.Tabs():
                with gr.Tab("Viewer"): #interactive=False, elem_id="htrflowouttab"
                    with gr.Group():
                        with gr.Row():
                            output_image_placehholder.render()
                        with gr.Row():
                            markdown_selected_option.render()
                        with gr.Row():
                            output_dataframe_pipeline = gr.Textbox(label="Click text",info="click on image bla bla..")
                with gr.Tab("Table") as htrflow_output_table_tab:
                    with gr.Group():
                        with gr.Row():
                            output_dataframe_pipeline = gr.Image(label="Output image", interactive=False, height="100")
                        with gr.Row():
                            output_dataframe_pipeline = gr.Dataframe(label="Output image", col_count=2)

            output_files_pipeline = gr.Files(label="Output files", height=100, visible=False)
            output_yaml_code = gr.Code(language="yaml", label="yaml", interactive=True, visible=False)

    submit_button_pipeline.click(
        get_yaml_button_fn,
        inputs=[
            template_method_radio,
            output_formats,
            simple_segment_model,
            simple_htr_model,
            simple_htr_model_type,
            simple_segment_model_type,
            nested_segment_model_1,
            nested_segment_model_2,
            nested_htr_model,
            nested_segment_model_1_type,
            nested_segment_model_2_type,
            nested_htr_model_type,
        ],
        outputs=[output_yaml_code],
    ).then(
        submit_button_pipeline_fn,
        inputs=[template_method_radio, user_image_input, output_yaml_code],
        outputs=[
            markdown_selected_option,
            output_image_placehholder,
            output_files_pipeline,
            output_files_pipeline,
            output_dataframe_pipeline,
        ],
    ).then(dummy_revealer, inputs=dummy_none, outputs=output_yaml_code)

    get_yaml_button.click(
        get_yaml_button_fn,
        inputs=[
            template_method_radio,
            output_formats,
            simple_segment_model,
            simple_htr_model,
            simple_htr_model_type,
            simple_segment_model_type,
            nested_segment_model_1,
            nested_segment_model_2,
            nested_htr_model,
            nested_segment_model_1_type,
            nested_segment_model_2_type,
            nested_htr_model_type,
        ],
        outputs=[output_yaml_code],
    ).then(dummy_revealer, inputs=output_yaml_code, outputs=output_yaml_code)

# TODO : hide the tab when selected for yaml code
# htrflow_output_table_tab.select(dummy_revealer, inputs=output_yaml_code, outputs=output_yaml_code)

template_method_radio.select(
    lambda choice: toggle_visibility_default_templates(choice),
    inputs=template_method_radio,
    outputs=[simple_pipeline, nested_pipeline, table_pipeline, selected_option],
)
