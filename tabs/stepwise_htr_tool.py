import os
import shutil

import gradio as gr

from helper.examples.examples import DemoImages
from src.htr_pipeline.gradio_backend import CustomTrack, SingletonModelLoader

model_loader = SingletonModelLoader()

custom_track = CustomTrack(model_loader)

images_for_demo = DemoImages()

with gr.Blocks() as stepwise_htr_tool_tab:
    with gr.Tabs():
        with gr.Tab("1. Region Segmentation"):
            with gr.Row():
                with gr.Column(scale=2):
                    vis_data_folder_placeholder = gr.Markdown(visible=False)
                    name_files_placeholder = gr.Markdown(visible=False)

                    with gr.Row():
                        input_region_image = gr.Image(
                            label="Image to Region segment",
                            # type="numpy",
                            tool="editor",
                            height=350,
                        )

                    with gr.Accordion("Region segment settings:", open=False):
                        with gr.Row():
                            reg_pred_score_threshold_slider = gr.Slider(
                                minimum=0.4,
                                maximum=1,
                                value=0.5,
                                step=0.05,
                                label="P-threshold",
                                info="""Filter and determine the confidence score 
                                                required for a prediction score to be considered""",
                            )
                            reg_containments_threshold_slider = gr.Slider(
                                minimum=0,
                                maximum=1,
                                value=0.5,
                                step=0.05,
                                label="C-threshold",
                                info="""The minimum required overlap or similarity 
                                                for a detected region or object to be considered valid""",
                            )

                        with gr.Row():
                            region_segment_model_dropdown = gr.Dropdown(
                                choices=["Riksarkivet/RmtDet_region"],
                                value="Riksarkivet/RmtDet_region",
                                label="Region segment model",
                                info="Will add more models later!",
                            )

                    with gr.Row():
                        clear_button = gr.Button("Clear", variant="secondary", elem_id="clear_button")

                        region_segment_button = gr.Button(
                            "Segment Region",
                            variant="primary",
                            elem_id="region_segment_button",
                        )

                    with gr.Row():
                        with gr.Accordion("Example images to use:", open=False) as example_accord:
                            gr.Examples(
                                examples=images_for_demo.examples_list,
                                inputs=[name_files_placeholder, input_region_image],
                                label="Example images",
                                examples_per_page=5,
                            )

                with gr.Column(scale=3):
                    output_region_image = gr.Image(label="Segmented regions", type="numpy", height=600)

        ##############################################
        with gr.Tab("2. Line Segmentation"):
            image_placeholder_lines = gr.Image(
                label="Segmented lines",
                # type="numpy",
                interactive="False",
                visible=True,
                height=600,
            )

            with gr.Row(visible=False) as control_line_segment:
                with gr.Column(scale=2):
                    with gr.Box():
                        regions_cropped_gallery = gr.Gallery(
                            label="Segmented regions",
                            elem_id="gallery",
                            columns=[2],
                            rows=[2],
                            # object_fit="contain",
                            height=450,
                            preview=True,
                            container=False,
                        )

                    input_region_from_gallery = gr.Image(
                        label="Region segmentation to line segment", interactive="False", visible=False, height=400
                    )

                    with gr.Row():
                        with gr.Accordion("Line segment settings:", open=False):
                            with gr.Row():
                                line_pred_score_threshold_slider = gr.Slider(
                                    minimum=0.3,
                                    maximum=1,
                                    value=0.4,
                                    step=0.05,
                                    label="Pred_score threshold",
                                    info="""Filter and determine the confidence score 
                                                    required for a prediction score to be considered""",
                                )
                                line_containments_threshold_slider = gr.Slider(
                                    minimum=0,
                                    maximum=1,
                                    value=0.5,
                                    step=0.05,
                                    label="Containments threshold",
                                    info="""The minimum required overlap or similarity 
                                                    for a detected region or object to be considered valid""",
                                )
                            with gr.Row(equal_height=False):
                                line_segment_model_dropdown = gr.Dropdown(
                                    choices=["Riksarkivet/RmtDet_lines"],
                                    value="Riksarkivet/RmtDet_lines",
                                    label="Line segment model",
                                    info="Will add more models later!",
                                )
                    with gr.Row():
                        clear_line_segment_button = gr.Button(
                            " ",
                            variant="Secondary",
                            # elem_id="center_button",
                            scale=1,
                        )

                        line_segment_button = gr.Button(
                            "Segment Lines",
                            variant="primary",
                            # elem_id="center_button",
                            scale=1,
                        )

                with gr.Column(scale=3):
                    # gr.Markdown("""lorem ipsum""")

                    output_line_from_region = gr.Image(
                        label="Segmented lines", type="numpy", interactive="False", height=600
                    )

        ###############################################
        with gr.Tab("3. Transcribe Text"):
            image_placeholder_htr = gr.Image(
                label="Transcribed lines",
                # type="numpy",
                interactive="False",
                visible=True,
                height=600,
            )

            with gr.Row(visible=False) as control_htr:
                inputs_lines_to_transcribe = gr.Variable()

                with gr.Column(scale=2):
                    image_inputs_lines_to_transcribe = gr.Image(
                        label="Transcribed lines", type="numpy", interactive="False", visible=False, height=470
                    )
                    with gr.Row():
                        with gr.Accordion("Transcribe settings:", open=False):
                            transcriber_model = gr.Dropdown(
                                choices=["Riksarkivet/SATRN_transcriber", "microsoft/trocr-base-handwritten"],
                                value="Riksarkivet/SATRN_transcriber",
                                label="Transcriber model",
                                info="Will add more models later!",
                            )
                    with gr.Row():
                        clear_transcribe_button = gr.Button(" ", variant="Secondary", visible=True, scale=1)

                        transcribe_button = gr.Button("Transcribe Lines", variant="primary", visible=True, scale=1)

                with gr.Column(scale=3):
                    with gr.Row():
                        transcribed_text_df = gr.Dataframe(
                            headers=["Transcribed text"],
                            max_rows=14,
                            col_count=(1, "fixed"),
                            wrap=True,
                            interactive=False,
                            overflow_row_behaviour="paginate",
                            height=600,
                        )

        #####################################
        with gr.Tab("4. Explore Results"):
            image_placeholder_explore_results = gr.Image(
                label="Cropped transcribed lines",
                # type="numpy",
                interactive="False",
                visible=True,
                height=600,
            )

            with gr.Row(visible=False, equal_height=False) as control_results_transcribe:
                with gr.Column(scale=1, visible=True):
                    with gr.Box():
                        temp_gallery_input = gr.Variable()

                        gallery_inputs_lines_to_transcribe = gr.Gallery(
                            label="Cropped transcribed lines",
                            elem_id="gallery_lines",
                            columns=[3],
                            rows=[3],
                            # object_fit="contain",
                            height=300,
                            preview=True,
                            container=False,
                        )

                    dataframe_text_index = gr.Textbox(
                        label="Text from DataFrame selection",
                        info="Click on a dataframe cell to view the corresponding transcribed text line crop. You can also sort the dataframe to easily locate specific entries.",
                        lines=2,
                        interactive=False,
                    )

                with gr.Column(scale=1, visible=True):
                    mapping_dict = gr.Variable()
                    transcribed_text_df_finish = gr.Dataframe(
                        headers=["Transcribed text", "pred score"],
                        max_rows=14,
                        col_count=(2, "fixed"),
                        wrap=True,
                        interactive=False,
                        overflow_row_behaviour="paginate",
                        height=600,
                    )

    # custom track
    region_segment_button.click(
        custom_track.region_segment,
        inputs=[input_region_image, reg_pred_score_threshold_slider, reg_containments_threshold_slider],
        outputs=[output_region_image, regions_cropped_gallery, image_placeholder_lines, control_line_segment],
    )

    regions_cropped_gallery.select(
        custom_track.get_select_index_image, regions_cropped_gallery, input_region_from_gallery
    )

    transcribed_text_df_finish.select(
        fn=custom_track.get_select_index_df,
        inputs=[transcribed_text_df_finish, mapping_dict],
        outputs=[gallery_inputs_lines_to_transcribe, dataframe_text_index],
    )

    line_segment_button.click(
        custom_track.line_segment,
        inputs=[input_region_from_gallery, line_pred_score_threshold_slider, line_containments_threshold_slider],
        outputs=[
            output_line_from_region,
            image_inputs_lines_to_transcribe,
            inputs_lines_to_transcribe,
            gallery_inputs_lines_to_transcribe,
            temp_gallery_input,
            # Hide
            transcribe_button,
            image_inputs_lines_to_transcribe,
            image_placeholder_htr,
            control_htr,
        ],
    )

    transcribe_button.click(
        custom_track.transcribe_text,
        inputs=[transcribed_text_df, inputs_lines_to_transcribe],
        outputs=[
            transcribed_text_df,
            transcribed_text_df_finish,
            mapping_dict,
            # Hide
            control_results_transcribe,
            image_placeholder_explore_results,
        ],
    )

    clear_button.click(
        lambda: (
            (shutil.rmtree("./vis_data") if os.path.exists("./vis_data") else None, None)[1],
            None,
            None,
            None,
            gr.update(visible=False),
            None,
            None,
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
        ),
        inputs=[],
        outputs=[
            vis_data_folder_placeholder,
            input_region_image,
            regions_cropped_gallery,
            input_region_from_gallery,
            control_line_segment,
            output_line_from_region,
            inputs_lines_to_transcribe,
            transcribed_text_df,
            control_htr,
            inputs_lines_to_transcribe,
            image_placeholder_htr,
            output_region_image,
            image_inputs_lines_to_transcribe,
            control_results_transcribe,
            image_placeholder_explore_results,
            image_placeholder_lines,
        ],
    )
