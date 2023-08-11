import gradio as gr

from helper.examples.examples import DemoImages
from src.htr_pipeline.gradio_backend import FastTrack, SingletonModelLoader

model_loader = SingletonModelLoader()

fast_track = FastTrack(model_loader)

images_for_demo = DemoImages()


with gr.Blocks() as htr_tool_tab:
    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            with gr.Row():
                fast_track_input_region_image = gr.Image(
                    label="Image to run HTR on", type="numpy", tool="editor", elem_id="image_upload", height=395
                )

            with gr.Row():
                # with gr.Group():
                # callback = gr.CSVLogger()
                # # hf_writer = gr.HuggingFaceDatasetSaver(HF_API_TOKEN, "htr_pipelin_flags")
                # flagging_button = gr.Button(
                #     "Flag",
                #     variant="secondary",
                #     visible=True,
                # ).style(full_width=True)
                # radio_file_input = gr.Radio(
                #     value="Text file", choices=["Text file ", "Page XML file "], label="What kind file output?"
                # )

                radio_file_input = gr.CheckboxGroup(
                    choices=["Txt", "XML"],
                    value=["Txt"],
                    label="Output file extension",
                    # info="Only txt and page xml is supported for now!",
                )

                htr_pipeline_button = gr.Button(
                    "Run HTR",
                    variant="primary",
                    visible=True,
                    elem_id="run_pipeline_button",
                ).style(full_width=False)

            with gr.Group():
                with gr.Row():
                    fast_file_downlod = gr.File(label="Download output file", visible=False)
                with gr.Row():
                    with gr.Accordion("Example images to use:", open=False) as fast_example_accord:
                        fast_name_files_placeholder = gr.Markdown(visible=False)

                        gr.Examples(
                            examples=images_for_demo.examples_list,
                            inputs=[fast_name_files_placeholder, fast_track_input_region_image],
                            label="Example images",
                            examples_per_page=3,
                        )

        with gr.Column(scale=4):
            fast_track_output_image = gr.Image(label="HTR results visualizer", type="numpy", tool="editor", height=650)

        with gr.Row(visible=False) as api_placeholder:
            htr_pipeline_button_api = gr.Button(
                "Run pipeline",
                variant="primary",
                visible=False,
            ).style(full_width=False)

    xml_rendered_placeholder_for_api = gr.Textbox(visible=False)
    htr_pipeline_button.click(
        fast_track.segment_to_xml,
        inputs=[fast_track_input_region_image, radio_file_input],
        outputs=[fast_track_output_image, fast_file_downlod, fast_file_downlod],
    )

    htr_pipeline_button_api.click(
        fast_track.segment_to_xml_api,
        inputs=[fast_track_input_region_image],
        outputs=[xml_rendered_placeholder_for_api],
        api_name="predict",
    )
