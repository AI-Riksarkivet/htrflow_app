import os
import shutil

import gradio as gr

from helper.examples.examples import DemoImages
from helper.gradio_config import css, js, theme
from helper.text import TextAbout, TextApp, TextHowTo, TextRiksarkivet, TextRoadmap
from src.htr_pipeline.gradio_backend import CustomTrack, FastTrack, SingletonModelLoader

model_loader = SingletonModelLoader()
fast_track = FastTrack(model_loader)
custom_track = CustomTrack(model_loader)
images_for_demo = DemoImages()

with gr.Blocks(title="HTR Riksarkivet", theme=theme, css=css) as demo:
    gr.Markdown("&nbsp;")
    gr.Markdown(TextApp.title_markdown)

    with gr.Tabs():
        with gr.Tab("HTR Tool"):
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Row():
                        fast_track_input_region_image = gr.Image(
                            label="Image to run HTR on", type="numpy", tool="editor", elem_id="image_upload"
                        ).style(height=395)

                    with gr.Row(equal_height=False):
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
                            choices=["Txt", "Page XML"],
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
                    with gr.Row():
                        fast_track_output_image = gr.Image(
                            label="HTR results visualizer",
                            type="numpy",
                            tool="editor",
                        ).style(height=650)

                with gr.Row(visible=False) as api_placeholder:
                    htr_pipeline_button_api = gr.Button(
                        "Run pipeline",
                        variant="primary",
                        visible=False,
                    ).style(full_width=False)

                    xml_rendered_placeholder_for_api = gr.Textbox(visible=False)

        with gr.Tab("Stepwise HTR Tool"):
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
                                ).style(height=350)

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
                                )  # .style(full_width=False)

                            with gr.Row():
                                with gr.Accordion("Example images to use:", open=False) as example_accord:
                                    gr.Examples(
                                        examples=images_for_demo.examples_list,
                                        inputs=[name_files_placeholder, input_region_image],
                                        label="Example images",
                                        examples_per_page=2,
                                    )

                        with gr.Column(scale=3):
                            output_region_image = gr.Image(label="Segmented regions", type="numpy").style(height=600)

                ##############################################
                with gr.Tab("2. Line Segmentation"):
                    image_placeholder_lines = gr.Image(
                        label="Segmented lines",
                        # type="numpy",
                        interactive="False",
                        visible=True,
                    ).style(height=600)

                    with gr.Row(visible=False) as control_line_segment:
                        with gr.Column(scale=2):
                            with gr.Box():
                                regions_cropped_gallery = gr.Gallery(
                                    label="Segmented regions",
                                    show_label=False,
                                    elem_id="gallery",
                                ).style(
                                    columns=[2],
                                    rows=[2],
                                    # object_fit="contain",
                                    height=400,
                                    preview=True,
                                    container=False,
                                )

                            input_region_from_gallery = gr.Image(
                                label="Region segmentation to line segment", interactive="False", visible=False
                            ).style(height=400)
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
                                    with gr.Row().style(equal_height=False):
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
                                ).style(full_width=True)

                                line_segment_button = gr.Button(
                                    "Segment Lines",
                                    variant="primary",
                                    # elem_id="center_button",
                                ).style(full_width=True)

                        with gr.Column(scale=3):
                            # gr.Markdown("""lorem ipsum""")

                            output_line_from_region = gr.Image(
                                label="Segmented lines",
                                type="numpy",
                                interactive="False",
                            ).style(height=600)

                ###############################################
                with gr.Tab("3. Transcribe Text"):
                    image_placeholder_htr = gr.Image(
                        label="Transcribed lines",
                        # type="numpy",
                        interactive="False",
                        visible=True,
                    ).style(height=600)

                    with gr.Row(visible=False) as control_htr:
                        inputs_lines_to_transcribe = gr.Variable()

                        with gr.Column(scale=2):
                            image_inputs_lines_to_transcribe = gr.Image(
                                label="Transcribed lines",
                                type="numpy",
                                interactive="False",
                                visible=False,
                            ).style(height=470)

                            with gr.Row():
                                with gr.Accordion("Transcribe settings:", open=False):
                                    transcriber_model = gr.Dropdown(
                                        choices=["Riksarkivet/SATRN_transcriber", "microsoft/trocr-base-handwritten"],
                                        value="Riksarkivet/SATRN_transcriber",
                                        label="Transcriber model",
                                        info="Will add more models later!",
                                    )
                            with gr.Row():
                                clear_transcribe_button = gr.Button(" ", variant="Secondary", visible=True).style(
                                    full_width=True
                                )
                                transcribe_button = gr.Button(
                                    "Transcribe lines", variant="primary", visible=True
                                ).style(full_width=True)

                                donwload_txt_button = gr.Button(
                                    "Download text", variant="secondary", visible=False
                                ).style(full_width=True)

                            with gr.Row():
                                txt_file_downlod = gr.File(label="Download text", visible=False)

                        with gr.Column(scale=3):
                            with gr.Row():
                                transcribed_text_df = gr.Dataframe(
                                    headers=["Transcribed text"],
                                    max_rows=15,
                                    col_count=(1, "fixed"),
                                    wrap=True,
                                    interactive=False,
                                    overflow_row_behaviour="paginate",
                                ).style(height=600)

                #####################################
                with gr.Tab("4. Explore Results"):
                    image_placeholder_explore_results = gr.Image(
                        label="Cropped transcribed lines",
                        # type="numpy",
                        interactive="False",
                        visible=True,
                    ).style(height=600)

                    with gr.Row(visible=False) as control_results_transcribe:
                        with gr.Column(scale=1, visible=True):
                            with gr.Box():
                                temp_gallery_input = gr.Variable()

                                gallery_inputs_lines_to_transcribe = gr.Gallery(
                                    label="Cropped transcribed lines",
                                    show_label=True,
                                    elem_id="gallery_lines",
                                ).style(
                                    columns=[3],
                                    rows=[3],
                                    # object_fit="contain",
                                    # height="600",
                                    preview=True,
                                    container=False,
                                )
                        with gr.Column(scale=1, visible=True):
                            mapping_dict = gr.Variable()
                            transcribed_text_df_finish = gr.Dataframe(
                                headers=["Transcribed text", "HTR prediction score"],
                                max_rows=15,
                                col_count=(2, "fixed"),
                                wrap=True,
                                interactive=False,
                                overflow_row_behaviour="paginate",
                            ).style(height=600)

        with gr.Tab("How to use"):
            with gr.Tabs():
                with gr.Tab("HTR Tool"):
                    with gr.Row().style(equal_height=False):
                        with gr.Column():
                            gr.Markdown(TextHowTo.htr_tool)
                        with gr.Column():
                            gr.Markdown(TextHowTo.both_htr_tool_video)
                            gr.Video(
                                value="https://github.com/Borg93/htr_gradio_file_placeholder/raw/main/eating_spaghetti.mp4",
                                label="How to use HTR Tool",
                            )
                            gr.Markdown(TextHowTo.reach_out)

                with gr.Tab("Stepwise HTR Tool"):
                    with gr.Row().style(equal_height=False):
                        with gr.Column():
                            gr.Markdown(TextHowTo.stepwise_htr_tool)
                            with gr.Row():
                                with gr.Accordion("The tabs for the Stepwise HTR Tool:", open=False):
                                    with gr.Tabs():
                                        with gr.Tab("1. Region Segmentation"):
                                            gr.Markdown(TextHowTo.stepwise_htr_tool_tab1)
                                        with gr.Tab("2. Line Segmentation"):
                                            gr.Markdown(TextHowTo.stepwise_htr_tool_tab2)
                                        with gr.Tab("3. Transcribe Text"):
                                            gr.Markdown(TextHowTo.stepwise_htr_tool_tab3)
                                        with gr.Tab("4. Explore Results"):
                                            gr.Markdown(TextHowTo.stepwise_htr_tool_tab4)
                            gr.Markdown(TextHowTo.stepwise_htr_tool_end)
                        with gr.Column():
                            gr.Markdown(TextHowTo.both_htr_tool_video)
                            gr.Video(
                                value="https://github.com/Borg93/htr_gradio_file_placeholder/raw/main/eating_spaghetti.mp4",
                                label="How to use Stepwise HTR Tool",
                            )
                            gr.Markdown(TextHowTo.reach_out)

        with gr.Tab("About"):
            with gr.Tabs():
                with gr.Tab("Project"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextAbout.intro_and_pipeline_overview_text)
                            with gr.Row():
                                with gr.Tabs():
                                    with gr.Tab("I. Binarization"):
                                        gr.Markdown(TextAbout.binarization)
                                    with gr.Tab("II. Region Segmentation"):
                                        gr.Markdown(TextAbout.text_region_segment)
                                    with gr.Tab("III. Line Segmentation"):
                                        gr.Markdown(TextAbout.text_line_segmentation)
                                    with gr.Tab("IV. Transcriber"):
                                        gr.Markdown(TextAbout.text_htr)
                            with gr.Row():
                                gr.Markdown(TextAbout.text_data)

                        with gr.Column():
                            gr.Markdown(TextAbout.filler_text_data)
                            gr.Markdown(TextAbout.text_models)
                            with gr.Row():
                                with gr.Tabs():
                                    with gr.Tab("Region Segmentation"):
                                        gr.Markdown(TextAbout.text_models_region)
                                    with gr.Tab("Line Segmentation"):
                                        gr.Markdown(TextAbout.text_line_segmentation)
                                    with gr.Tab("Transcriber"):
                                        gr.Markdown(TextAbout.text_models_htr)

                with gr.Tab("Roadmap"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextRoadmap.roadmap)
                        with gr.Column():
                            gr.Markdown(TextRoadmap.notebook)

                with gr.Tab("Riksarkivet"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextRiksarkivet.riksarkivet)
                        with gr.Column():
                            gr.Markdown(TextRiksarkivet.contact)

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

    # fast_track_input_region_image.change(
    #     fn=lambda: (gr.Accordion.update(open=False)),
    #     outputs=[fast_example_accord],
    # )

    # input_region_image.change(
    #     fn=lambda: (gr.Accordion.update(open=False)),
    #     outputs=[example_accord],
    # )

    # callback.setup([fast_track_input_region_image], "flagged_data_points")
    # flagging_button.click(lambda *args: callback.flag(args), [fast_track_input_region_image], None, preprocess=False)
    # flagging_button.click(lambda: (gr.update(value="Flagged")), outputs=flagging_button)
    # fast_track_input_region_image.change(lambda: (gr.update(value="Flag")), outputs=flagging_button)

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
        outputs=gallery_inputs_lines_to_transcribe,
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
            txt_file_downlod,
            control_results_transcribe,
            image_placeholder_explore_results,
        ],
    )

    donwload_txt_button.click(
        custom_track.download_df_to_txt,
        inputs=transcribed_text_df,
        outputs=[txt_file_downlod, txt_file_downlod],
    )

    # def remove_temp_vis():
    #     if os.path.exists("./vis_data"):
    #         os.remove("././vis_data")
    #     return None

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

    demo.load(None, None, None, _js=js)


demo.queue(concurrency_count=5, max_size=20)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=True)
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=True)
