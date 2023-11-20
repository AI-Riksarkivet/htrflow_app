import os
SECRET_KEY = os.environ.get("HUB_TOKEN", False)
if SECRET_KEY:
    from helper.utils import TrafficDataHandler
    
import gradio as gr

from helper.examples.examples import DemoImages
from src.htr_pipeline.gradio_backend import (
    FastTrack,
    SingletonModelLoader,
    compare_diff_runs_highlight,
    compute_cer_a_and_b_with_gt,
    update_selected_tab_image_viewer,
    update_selected_tab_model_compare,
    update_selected_tab_output_and_setting,
    upload_file,
)

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
                        run_image_visualizer_button = gr.Button(
                            value="Visualize results", variant="primary", interactive=True
                        )

                    selection_text_from_image_viewer = gr.Textbox(
                        interactive=False, label="Text Selector", info="Select a line on Image Viewer to return text"
                    )

                with gr.Tab("Compare") as tab_model_compare_selector:
                    with gr.Row():
                        diff_runs_button = gr.Button("Compare runs", variant="primary", visible=True)
                        calc_cer_button_fast = gr.Button("Calculate CER", variant="primary", visible=True)
                    with gr.Row():
                        cer_output_fast = gr.Textbox(
                            label="Character Error Rate:",
                            info="The percentage of characters that have been transcribed incorrectly",
                        )

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
                                            choices=[
                                                "Riksarkivet/satrn_htr",
                                                "microsoft/trocr-base-handwritten",
                                                "pstroe/bullinger-general-model",
                                            ],
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
                        gr.Markdown("Compare different runs (Page XML output) with Ground Truth (GT)")
                    with gr.Row():
                        with gr.Group():
                            upload_button_run_a = gr.UploadButton("A", file_types=[".xml"], file_count="single")
                            file_input_xml_run_a = gr.File(
                                label=None,
                                file_count="single",
                                height=100,
                                elem_id="download_file",
                                interactive=False,
                                visible=False,
                            )

                        with gr.Group():
                            upload_button_run_b = gr.UploadButton("B", file_types=[".xml"], file_count="single")
                            file_input_xml_run_b = gr.File(
                                label=None,
                                file_count="single",
                                height=100,
                                elem_id="download_file",
                                interactive=False,
                                visible=False,
                            )

                        with gr.Group():
                            upload_button_run_gt = gr.UploadButton("GT", file_types=[".xml"], file_count="single")
                            file_input_xml_run_gt = gr.File(
                                label=None,
                                file_count="single",
                                height=100,
                                elem_id="download_file",
                                interactive=False,
                                visible=False,
                            )
                    with gr.Tab("Comparing run A with B"):
                        text_diff_runs = gr.HighlightedText(
                            label="A with B",
                            combine_adjacent=True,
                            show_legend=True,
                            color_map={"+": "red", "-": "green"},
                        )
                    with gr.Tab("Compare run A with Ground Truth"):
                        text_diff_gt = gr.HighlightedText(
                            label="A with GT",
                            combine_adjacent=True,
                            show_legend=True,
                            color_map={"+": "red", "-": "green"},
                        )

        xml_rendered_placeholder_for_api = gr.Textbox(placeholder="XML", visible=False)

    htr_event_click_event = htr_pipeline_button.click(
        fast_track.segment_to_xml,
        inputs=[fast_track_input_region_image, radio_file_input, htr_tool_transcriber_model_dropdown],
        outputs=[fast_file_downlod, fast_file_downlod],
        api_name=False,
    )

    htr_pipeline_button_api.click(
        fast_track.segment_to_xml_api,
        inputs=[fast_track_input_region_image],
        outputs=[xml_rendered_placeholder_for_api],
        queue=False,
        api_name="run_htr_pipeline",
    )

    tab_output_and_setting_selector.select(
        fn=update_selected_tab_output_and_setting,
        outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector],
        api_name=False,
    )

    tab_image_viewer_selector.select(
        fn=update_selected_tab_image_viewer,
        outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector],
        api_name=False,
    )

    tab_model_compare_selector.select(
        fn=update_selected_tab_model_compare,
        outputs=[output_and_setting_tab, image_viewer_tab, model_compare_selector],
        api_name=False,
    )

    def stop_function():
        from src.htr_pipeline.utils import pipeline_inferencer

        pipeline_inferencer.terminate = True
        gr.Info("The HTR execution was halted")

    stop_htr_button.click(
        fn=stop_function,
        inputs=None,
        outputs=None,
        api_name=False,
        # cancels=[htr_event_click_event],
    )

    run_image_visualizer_button.click(
        fn=fast_track.visualize_image_viewer,
        inputs=fast_track_input_region_image,
        outputs=[fast_track_output_image, text_polygon_dict],
        api_name=False,
    )

    fast_track_output_image.select(
        fast_track.get_text_from_coords,
        inputs=text_polygon_dict,
        outputs=selection_text_from_image_viewer,
        api_name=False,
    )

    upload_button_run_a.upload(
        upload_file, inputs=upload_button_run_a, outputs=[file_input_xml_run_a, file_input_xml_run_a], api_name=False
    )

    upload_button_run_b.upload(
        upload_file, inputs=upload_button_run_b, outputs=[file_input_xml_run_b, file_input_xml_run_b], api_name=False
    )

    upload_button_run_gt.upload(
        upload_file, inputs=upload_button_run_gt, outputs=[file_input_xml_run_gt, file_input_xml_run_gt], api_name=False
    )

    diff_runs_button.click(
        fn=compare_diff_runs_highlight,
        inputs=[file_input_xml_run_a, file_input_xml_run_b, file_input_xml_run_gt],
        outputs=[text_diff_runs, text_diff_gt],
        api_name=False,
    )

    calc_cer_button_fast.click(
        fn=compute_cer_a_and_b_with_gt,
        inputs=[file_input_xml_run_a, file_input_xml_run_b, file_input_xml_run_gt],
        outputs=cer_output_fast,
        api_name=False,
    )

    SECRET_KEY = os.environ.get("HUB_TOKEN", False)
    if SECRET_KEY:
        htr_pipeline_button.click(
            fn=TrafficDataHandler.store_metric_data,
            inputs=htr_pipeline_button_var,
        )
