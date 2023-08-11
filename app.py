import gradio as gr

from helper.gradio_config import css, js, theme
from helper.text import TextAbout, TextApp, TextHowTo, TextRiksarkivet, TextRoadmap
from tabs.htr_tool import htr_tool_tab
from tabs.stepwise_htr_tool import stepwise_htr_tool_tab

with gr.Blocks(title="HTR Riksarkivet", theme=theme, css=css) as demo:
    gr.Markdown(TextApp.title_markdown)

    with gr.Tabs():
        with gr.Tab("HTR Tool"):
            htr_tool_tab.render()

        with gr.Tab("Stepwise HTR Tool"):
            stepwise_htr_tool_tab.render()
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
                        gr.Markdown(TextRiksarkivet.riksarkivet)

    # callback.setup([fast_track_input_region_image], "flagged_data_points")
    # flagging_button.click(lambda *args: callback.flag(args), [fast_track_input_region_image], None, preprocess=False)
    # flagging_button.click(lambda: (gr.update(value="Flagged")), outputs=flagging_button)
    # fast_track_input_region_image.change(lambda: (gr.update(value="Flag")), outputs=flagging_button)

    demo.load(None, None, None, _js=js)


demo.queue(concurrency_count=5, max_size=20)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=True)
