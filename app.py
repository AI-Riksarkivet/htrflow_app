import gradio as gr

from helper.gradio_config import css, theme
from helper.text.text_about import TextAbout
from helper.text.text_app import TextApp
from helper.text.text_howto import TextHowTo
from helper.text.text_roadmap import TextRoadmap
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
                    with gr.Row(equal_height=False):
                        with gr.Column():
                            gr.Markdown(TextHowTo.htr_tool)
                        with gr.Column():
                            gr.Markdown(TextHowTo.both_htr_tool_video)
                            gr.Video(
                                value="https://github.com/Borg93/htr_gradio_file_placeholder/raw/main/htr_tool_media_cut.mp4",
                                label="How to use HTR Tool",
                            )
                            gr.Markdown(TextHowTo.reach_out)

                with gr.Tab("Stepwise HTR Tool"):
                    with gr.Row(equal_height=False):
                        gr.Markdown(TextHowTo.stepwise_htr_tool)
                    with gr.Row():
                        gr.Markdown(TextHowTo.stepwise_htr_tool_tab_intro)
                    with gr.Row():
                        with gr.Accordion("The tabs for the Stepwise HTR Tool:", open=True):
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

                with gr.Tab("API & Duplicate for Privat use"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextHowTo.htr_tool_api_text)
                            gr.Code(
                                value=TextHowTo.code_for_api,
                                language="python",
                                interactive=False,
                                show_label=False,
                            )
                        with gr.Column():
                            gr.Markdown(TextHowTo.duplicatin_space_htr_text)
                            gr.Markdown(TextHowTo.figure_htr_hardware)
                            gr.Markdown(TextHowTo.duplicatin_for_privat)

        with gr.Tab("About"):
            with gr.Tabs():
                with gr.Tab("Project"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextAbout.intro_and_pipeline_overview_text)
                        with gr.Column():
                            gr.Markdown(TextAbout.text_src_code_data_models)
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

                with gr.Tab("Contribution"):
                    with gr.Row():
                        gr.Markdown(TextRoadmap.text_contribution)

                with gr.Tab("Roadmap"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(TextRoadmap.roadmap)
                        with gr.Column():
                            gr.Markdown(TextRoadmap.discussion)

    # demo.load(None, None, None, _js=js)


demo.queue(concurrency_count=2, max_size=2)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False, show_error=True)
