import os

import gradio as gr

from helper.examples.examples import DemoImages
from helper.utils import TrafficDataHandler
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
                with gr.Tab("HTRFLOW") as tab_output_and_setting_selector:
                    with gr.Row():
                        stop_htr_button = gr.Button(
                            value="Stop run",
                            variant="stop",
                        )

                        htr_pipeline_button = gr.Button(
                            "Run ",
                            variant="primary",
                            visible=True,
                            elem_id="run_pipeline_button",
                        )
                        htr_pipeline_button_var = gr.State(value="htr_pipeline_button")

                    htr_pipeline_button_api = gr.Button("Run pipeline", variant="primary", visible=False, scale=1)

                    fast_file_downlod = gr.File(
                        label="Download output file", visible=True, scale=1, height=100, elem_id="download_file"
                    )

                with gr.Tab("Visualize") as tab_image_viewer_selector:
                    with gr.Row():
                        gr.Markdown("")
                        #     gr.Button(
                        #     value="Image viewer",
                        #     variant="secondary",
                        #     link="https://huggingface.co/spaces/Riksarkivet/Viewer_demo",
                        #     interactive=True,
                        # )

                        run_image_visualizer_button = gr.Button(
                            value="Visualize results", variant="primary", interactive=True
                        )

                    selection_text_from_image_viewer = gr.Textbox(
                        interactive=False, label="Text Selector", info="Select a line on Image Viewer to return text"
                    )

                with gr.Tab("Compare") as tab_model_compare_selector:
                    with gr.Box():
                        gr.Markdown(
                            """
                            **Work in progress**

                            Compare different runs with uploaded Ground Truth and calculate CER. You will also be able to upload output format files

                            """
                        )

                        calc_cer_button_fast = gr.Button("Calculate CER", variant="primary", visible=True)

        with gr.Column(scale=4):
            with gr.Box():
                with gr.Row(visible=True) as output_and_setting_tab:
                    with gr.Column(scale=2):
                        fast_name_files_placeholder = gr.Markdown(visible=False)
                        gr.Examples(
                            examples=images_for_demo.examples_list,
                            inputs=[fast_name_files_placeholder, fast_track_input_region_image],
                            label="Example images",
                            examples_per_page=5,
                        )

                        gr.Markdown("&nbsp;")

                    with gr.Column(scale=3):
                        with gr.Group():
                            gr.Markdown("  &nbsp; ⚙️ Settings ")
                            with gr.Row():
                                radio_file_input = gr.CheckboxGroup(
                                    choices=["Txt", "Page XML"],
                                    value=["Txt", "Page XML"],
                                    label="Output file extension",
                                    info="JSON and ALTO-XML will be added",
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

                            with gr.Accordion("Advanced settings", open=False):
                                with gr.Group():
                                    with gr.Row():
                                        htr_tool_region_segment_model_dropdown = gr.Dropdown(
                                            choices=["Riksarkivet/rtmdet_region"],
                                            value="Riksarkivet/rtmdet_region",
                                            label="Region segmentation models",
                                            info="More models will be added",
                                        )

                                        gr.Slider(
                                            minimum=0.4,
                                            maximum=1,
                                            value=0.5,
                                            step=0.05,
                                            label="P-threshold",
                                            info="""Filter confidence score for a prediction score to be considered""",
                                        )

                                    with gr.Row():
                                        htr_tool_line_segment_model_dropdown = gr.Dropdown(
                                            choices=["Riksarkivet/rtmdet_lines"],
                                            value="Riksarkivet/rtmdet_lines",
                                            label="Line segmentation models",
                                            info="More models will be added",
                                        )

                                        gr.Slider(
                                            minimum=0.4,
                                            maximum=1,
                                            value=0.5,
                                            step=0.05,
                                            label="P-threshold",
                                            info="""Filter confidence score for a prediction score to be considered""",
                                        )

                                    with gr.Row():
                                        htr_tool_transcriber_model_dropdown = gr.Dropdown(
                                            choices=["Riksarkivet/satrn_htr", "microsoft/trocr-base-handwritten"],
                                            value="Riksarkivet/satrn_htr",
                                            label="Text recognition models",
                                            info="More models will be added",
                                        )

                                        gr.Slider(
                                            value=0.6,
                                            minimum=0.5,
                                            maximum=1,
                                            label="HTR threshold",
                                            info="Prediction score threshold for transcribed lines",
                                            scale=1,
                                        )
                                    with gr.Row():
                                        gr.Markdown("  &nbsp; More settings will be added")

                with gr.Row(visible=False) as image_viewer_tab:
                    text_polygon_dict = gr.Variable()

                    fast_track_output_image = gr.Image(
                        label="Image Viewer", type="numpy", height=600, interactive=False
                    )

                with gr.Column(visible=False) as model_compare_selector:
                    with gr.Row():
                        gr.Radio(
                            choices=["Compare Page XML", "Compare different runs"],
                            value="Compare Page XML",
                            info="Compare different runs from HTRFLOW or with external runs.",
                        )
                    with gr.Row():
                        gr.UploadButton(label="Run A")

                        gr.UploadButton(label="Run B")

                        gr.UploadButton(label="Ground Truth")

                    with gr.Row():
                        gr.HighlightedText(
                            label="Text diff runs",
                            combine_adjacent=True,
                            show_legend=True,
                            color_map={"+": "red", "-": "green"},
                        )

                    with gr.Row():
                        gr.HighlightedText(
                            label="Text diff ground truth",
                            combine_adjacent=True,
                            show_legend=True,
                            color_map={"+": "red", "-": "green"},
                        )

                    with gr.Row():
                        with gr.Column(scale=1):
                            with gr.Row(equal_height=False):
                                cer_output_fast = gr.Textbox(label="CER:")
                        with gr.Column(scale=2):
                            pass

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

    def dummy_update_htr_tool_transcriber_model_dropdown(htr_tool_transcriber_model_dropdown):
        return gr.update(value="Riksarkivet/satrn_htr")

    htr_tool_transcriber_model_dropdown.change(
        fn=dummy_update_htr_tool_transcriber_model_dropdown,
        inputs=htr_tool_transcriber_model_dropdown,
        outputs=htr_tool_transcriber_model_dropdown,
    )

    def update_selected_tab_output_and_setting():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    def update_selected_tab_image_viewer():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

    def update_selected_tab_model_compare():
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

    tab_output_and_setting_selector.select(
        fn=update_selected_tab_output_and_setting,
        outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector],
    )

    tab_image_viewer_selector.select(
        fn=update_selected_tab_image_viewer, outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector]
    )

    tab_model_compare_selector.select(
        fn=update_selected_tab_model_compare, outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector]
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

    SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
    if SECRET_KEY:
        htr_pipeline_button.click(fn=TrafficDataHandler.store_metric_data, inputs=htr_pipeline_button_var)
