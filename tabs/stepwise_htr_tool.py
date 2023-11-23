import os
import shutil
from difflib import Differ

import evaluate
import gradio as gr

from helper.examples.examples import DemoImages
from src.htr_pipeline.gradio_backend import CustomTrack, SingletonModelLoader

SECRET_KEY = os.environ.get("HUB_TOKEN", False)
if SECRET_KEY:
    from helper.utils import TrafficDataHandler


model_loader = SingletonModelLoader()

custom_track = CustomTrack(model_loader)

images_for_demo = DemoImages()

cer_metric = evaluate.load("cer")


with gr.Blocks() as stepwise_htr_tool_tab:
    with gr.Tabs():
        with gr.Tab("1. Region segmentation"):
            with gr.Row():
                with gr.Column(scale=1):
                    vis_data_folder_placeholder = gr.Markdown(visible=False)
                    name_files_placeholder = gr.Markdown(visible=False)

                    with gr.Group():
                        input_region_image = gr.Image(
                            label="Image to region segment",
                            # type="numpy",
                            tool="editor",
                            height=500,
                        )
                        with gr.Accordion("Settings", open=False):
                            with gr.Group():
                                reg_pred_score_threshold_slider = gr.Slider(
                                    minimum=0.4,
                                    maximum=1,
                                    value=0.5,
                                    step=0.05,
                                    label="P-threshold",
                                    info="""Filter the confidence score for a prediction score to be considered""",
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

                                region_segment_model_dropdown = gr.Dropdown(
                                    choices=["Riksarkivet/rtm_region"],
                                    value="Riksarkivet/rtm_region",
                                    label="Region segmentation model",
                                    info="More models will be added",
                                )

                    with gr.Row():
                        clear_button = gr.Button("Clear", variant="secondary", elem_id="clear_button")

                        region_segment_button = gr.Button(
                            "Run",
                            variant="primary",
                            elem_id="region_segment_button",
                        )

                        region_segment_button_var = gr.State(value="region_segment_button")

                with gr.Column(scale=2):
                    with gr.Box():
                        with gr.Row():
                            with gr.Column(scale=2):
                                gr.Examples(
                                    examples=images_for_demo.examples_list,
                                    inputs=[name_files_placeholder, input_region_image],
                                    label="Example images",
                                    examples_per_page=5,
                                )
                            with gr.Column(scale=3):
                                output_region_image = gr.Image(label="Segmented regions", type="numpy", height=600)

        ##############################################
        with gr.Tab("2. Line segmentation"):
            image_placeholder_lines = gr.Image(
                label="Segmented lines",
                # type="numpy",
                interactive="False",
                visible=True,
                height=600,
            )

            with gr.Row(visible=False) as control_line_segment:
                with gr.Column(scale=2):
                    with gr.Group():
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
                            with gr.Accordion("Settings", open=False):
                                with gr.Row():
                                    line_pred_score_threshold_slider = gr.Slider(
                                        minimum=0.3,
                                        maximum=1,
                                        value=0.4,
                                        step=0.05,
                                        label="Pred_score threshold",
                                        info="""Filter the confidence score for a prediction score to be considered""",
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
                                        choices=["Riksarkivet/rtmdet_lines"],
                                        value="Riksarkivet/rtmdet_lines",
                                        label="Line segment model",
                                        info="More models will be added",
                                    )
                    with gr.Row():
                        # placeholder_line_button = gr.Button(
                        #     "",
                        #     variant="secondary",
                        #     scale=1,
                        # )
                        gr.Markdown("&nbsp;")

                        line_segment_button = gr.Button(
                            "Run",
                            variant="primary",
                            # elem_id="center_button",
                            scale=1,
                        )

                with gr.Column(scale=3):
                    output_line_from_region = gr.Image(
                        label="Segmented lines", type="numpy", interactive="False", height=600
                    )

        ###############################################
        with gr.Tab("3. Text recognition"):
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
                    with gr.Group():
                        image_inputs_lines_to_transcribe = gr.Image(
                            label="Transcribed lines", type="numpy", interactive="False", visible=False, height=470
                        )
                        with gr.Row():
                            with gr.Accordion("Settings", open=False):
                                transcriber_model = gr.Dropdown(
                                    choices=["Riksarkivet/satrn_htr", "microsoft/trocr-base-handwritten"],
                                    value="Riksarkivet/satrn_htr",
                                    label="Text recognition model",
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
                        copy_textarea = gr.Button("Copy text", variant="secondary", visible=True, scale=1)

                        transcribe_button = gr.Button("Run", variant="primary", visible=True, scale=1)

                with gr.Column(scale=3):
                    with gr.Row():
                        transcribed_text = gr.Textbox(
                            label="Transcribed text",
                            info="Transcribed text is being streamed back from the Text recognition model",
                            lines=26,
                            value="",
                            show_copy_button=True,
                            elem_id="textarea_stepwise_3",
                        )

        #####################################
        with gr.Tab("4. Explore results"):
            image_placeholder_explore_results = gr.Image(
                label="Cropped transcribed lines",
                # type="numpy",
                interactive="False",
                visible=True,
                height=600,
            )

            with gr.Row(visible=False, equal_height=False) as control_results_transcribe:
                with gr.Column(scale=1, visible=True):
                    with gr.Group():
                        with gr.Box():
                            temp_gallery_input = gr.Variable()

                            gallery_inputs_lines_to_transcribe = gr.Gallery(
                                label="Cropped transcribed lines",
                                elem_id="gallery_lines",
                                columns=[3],
                                rows=[3],
                                # object_fit="contain",
                                height=150,
                                preview=True,
                                container=False,
                            )
                        with gr.Row():
                            dataframe_text_index = gr.Textbox(
                                label="Text from DataFrame selection",
                                placeholder="Select row from the DataFrame.",
                                interactive=False,
                            )
                        with gr.Row():
                            gt_text_index = gr.Textbox(
                                label="Ground Truth",
                                placeholder="Provide the ground truth, if available.",
                                interactive=True,
                            )
                    with gr.Row():
                        diff_token_output = gr.HighlightedText(
                            label="Text diff",
                            combine_adjacent=True,
                            show_legend=True,
                            color_map={"+": "red", "-": "green"},
                        )

                    with gr.Row(equal_height=False):
                        cer_output = gr.Textbox(label="Character Error Rate")
                        gr.Markdown("")
                        calc_cer_button = gr.Button("Calculate CER", variant="primary", visible=True)

                with gr.Column(scale=1, visible=True):
                    mapping_dict = gr.Variable()
                    transcribed_text_df_finish = gr.Dataframe(
                        headers=["Transcribed text", "Prediction score"],
                        max_rows=14,
                        col_count=(2, "fixed"),
                        wrap=True,
                        interactive=False,
                        overflow_row_behaviour="paginate",
                        height=600,
                    )

    # custom track

    def diff_texts(text1, text2):
        d = Differ()
        return [(token[2:], token[0] if token[0] != " " else None) for token in d.compare(text1, text2)]

    def compute_cer(dataframe_text_index, gt_text_index):
        if gt_text_index is not None and gt_text_index.strip() != "":
            return round(cer_metric.compute(predictions=[dataframe_text_index], references=[gt_text_index]), 4)
        else:
            return "Ground truth not provided"

    calc_cer_button.click(
        compute_cer,
        inputs=[dataframe_text_index, gt_text_index],
        outputs=cer_output,
        api_name=False,
    )

    calc_cer_button.click(
        diff_texts,
        inputs=[dataframe_text_index, gt_text_index],
        outputs=[diff_token_output],
        api_name=False,
    )

    region_segment_button.click(
        custom_track.region_segment,
        inputs=[input_region_image, reg_pred_score_threshold_slider, reg_containments_threshold_slider],
        outputs=[output_region_image, regions_cropped_gallery, image_placeholder_lines, control_line_segment],
        api_name=False,
    )

    regions_cropped_gallery.select(
        custom_track.get_select_index_image,
        regions_cropped_gallery,
        input_region_from_gallery,
        api_name=False,
    )

    transcribed_text_df_finish.select(
        fn=custom_track.get_select_index_df,
        inputs=[transcribed_text_df_finish, mapping_dict],
        outputs=[gallery_inputs_lines_to_transcribe, dataframe_text_index],
        api_name=False,
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
        api_name=False,
    )

    copy_textarea.click(
        fn=None,
        _js="""document.querySelector("#textarea_stepwise_3 > label > button").click()""",
        api_name=False,
    )

    transcribe_button.click(
        custom_track.transcribe_text,
        inputs=[inputs_lines_to_transcribe],
        outputs=[
            transcribed_text,
            transcribed_text_df_finish,
            mapping_dict,
            # Hide
            control_results_transcribe,
            image_placeholder_explore_results,
        ],
        api_name=False,
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
            transcribed_text,
            control_htr,
            inputs_lines_to_transcribe,
            image_placeholder_htr,
            output_region_image,
            image_inputs_lines_to_transcribe,
            control_results_transcribe,
            image_placeholder_explore_results,
            image_placeholder_lines,
        ],
        api_name=False,
    )

    SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
    if SECRET_KEY:
        region_segment_button.click(fn=TrafficDataHandler.store_metric_data, inputs=region_segment_button_var)
