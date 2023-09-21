import gradio as gr

from helper.examples.examples import DemoImages
from src.htr_pipeline.gradio_backend import FastTrack, SingletonModelLoader

model_loader = SingletonModelLoader()

fast_track = FastTrack(model_loader)

images_for_demo = DemoImages()

terminate = False


with gr.Blocks() as htr_tool_tab:
    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            with gr.Row():
                fast_track_input_region_image = gr.Image(
                    label="Image to run HTR on", type="numpy", tool="editor", elem_id="image_upload", height=395
                )

            with gr.Row():
                with gr.Tab("Output and Settings") as tab_output_and_setting_selector:
                    with gr.Row():
                        stop_htr_button = gr.Button(
                            value="Stop HTR",
                            variant="stop",
                        )

                        htr_pipeline_button = gr.Button(
                            "Run HTR",
                            variant="primary",
                            visible=True,
                            elem_id="run_pipeline_button",
                        )

                    htr_pipeline_button_api = gr.Button("Run pipeline", variant="primary", visible=False, scale=1)

                    fast_file_downlod = gr.File(
                        label="Download output file", visible=True, scale=1, height=100, elem_id="download_file"
                    )

                with gr.Tab("Image Viewer") as tab_image_viewer_selector:
                    with gr.Row():
                        gr.Button(
                            value="External Image Viewer",
                            variant="secondary",
                            link="https://huggingface.co/spaces/Riksarkivet/Viewer_demo",
                            interactive=True,
                        )

                        run_image_visualizer_button = gr.Button(
                            value="Visualize results", variant="primary", interactive=True
                        )

                    selection_text_from_image_viewer = gr.Textbox(
                        interactive=False, label="Text Selector", info="Select a mask on Image Viewer to return text"
                    )

        with gr.Column(scale=4):
            with gr.Box():
                with gr.Row(visible=True) as output_and_setting_tab:
                    with gr.Column(scale=3):
                        with gr.Row():
                            with gr.Group():
                                gr.Markdown("  &nbsp; ⚙️ Settings ")
                                with gr.Row():
                                    radio_file_input = gr.CheckboxGroup(
                                        choices=["Txt", "XML"],
                                        value=["XML"],
                                        label="Output file extension",
                                        # info="Only txt and page xml is supported for now!",
                                        scale=1,
                                    )
                                with gr.Row():
                                    gr.Checkbox(
                                        value=True,
                                        label="Binarize image",
                                        info="Binarize image to reduce background noise",
                                    )
                                    gr.Checkbox(
                                        value=True,
                                        label="Output prediction threshold",
                                        info="Output XML with prediction score",
                                    )
                                with gr.Row():
                                    gr.Slider(
                                        value=0.6,
                                        minimum=0.5,
                                        maximum=1,
                                        label="HTR threshold",
                                        info="Prediction score threshold for transcribed lines",
                                        scale=1,
                                    )
                                    gr.Slider(
                                        value=0.7,
                                        minimum=0.6,
                                        maximum=1,
                                        label="Avg threshold",
                                        info="Average prediction score for a region",
                                        scale=1,
                                    )

                                htr_tool_region_segment_model_dropdown = gr.Dropdown(
                                    choices=["Riksarkivet/RmtDet_region"],
                                    value="Riksarkivet/RmtDet_region",
                                    label="Region Segment models",
                                    info="Will add more models later!",
                                )

                                # with gr.Accordion("Transcribe settings:", open=False):
                                htr_tool_line_segment_model_dropdown = gr.Dropdown(
                                    choices=["Riksarkivet/RmtDet_lines"],
                                    value="Riksarkivet/RmtDet_lines",
                                    label="Line Segment models",
                                    info="Will add more models later!",
                                )

                                htr_tool_transcriber_model_dropdown = gr.Dropdown(
                                    choices=["Riksarkivet/SATRN_transcriber", "microsoft/trocr-base-handwritten"],
                                    value="Riksarkivet/SATRN_transcriber",
                                    label="Transcriber models",
                                    info="Models will be continuously  updated with future additions for specific cases.",
                                )

                    with gr.Column(scale=2):
                        fast_name_files_placeholder = gr.Markdown(visible=False)
                        gr.Examples(
                            examples=images_for_demo.examples_list,
                            inputs=[fast_name_files_placeholder, fast_track_input_region_image],
                            label="Example images",
                            examples_per_page=5,
                        )

                with gr.Row(visible=False) as image_viewer_tab:
                    text_polygon_dict = gr.Variable()

                    fast_track_output_image = gr.Image(
                        label="Image Viewer", type="numpy", height=600, interactive=False
                    )

    xml_rendered_placeholder_for_api = gr.Textbox(visible=False)

    htr_event_click_event = htr_pipeline_button.click(
        fast_track.segment_to_xml,
        inputs=[fast_track_input_region_image, radio_file_input],
        outputs=[fast_file_downlod, fast_file_downlod],
    )

    htr_pipeline_button_api.click(
        fast_track.segment_to_xml_api,
        inputs=[fast_track_input_region_image],
        outputs=[xml_rendered_placeholder_for_api],
        api_name="predict",
    )

    def update_selected_tab_output_and_setting():
        return gr.update(visible=True), gr.update(visible=False)

    def update_selected_tab_image_viewer():
        return gr.update(visible=False), gr.update(visible=True)

    tab_output_and_setting_selector.select(
        fn=update_selected_tab_output_and_setting, outputs=[output_and_setting_tab, image_viewer_tab]
    )

    tab_image_viewer_selector.select(
        fn=update_selected_tab_image_viewer, outputs=[output_and_setting_tab, image_viewer_tab]
    )

    def stop_function():
        from src.htr_pipeline.utils import pipeline_inferencer

        pipeline_inferencer.terminate = True
        gr.Info("The HTR execution was halted")

    stop_htr_button.click(fn=stop_function, inputs=None, outputs=None, cancels=[htr_event_click_event])

    run_image_visualizer_button.click(
        fn=fast_track.visualize_image_viewer,
        inputs=fast_track_input_region_image,
        outputs=[fast_track_output_image, text_polygon_dict],
    )

    fast_track_output_image.select(
        fast_track.get_text_from_coords, inputs=text_polygon_dict, outputs=selection_text_from_image_viewer
    )
