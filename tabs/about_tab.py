import gradio as gr

from helper.text.text_about import TextAbout
from helper.text.text_help import TextHowTo

with gr.Blocks() as about_tab:
    with gr.Tabs():
        with gr.Tab("HTRFLOW"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextAbout.htrflow_col1)
                with gr.Column():
                    gr.Markdown(TextAbout.htrflow_col2)
            with gr.Row():
                gr.Markdown(TextAbout.htrflow_row1)
            with gr.Row():
                with gr.Tabs():
                    with gr.Tab("Binarization"):
                        gr.Markdown(TextAbout.htrflow_tab1)
                    with gr.Tab("Region segmentation"):
                        gr.Markdown(TextAbout.htrflow_tab2)
                    with gr.Tab("Line segmentation"):
                        gr.Markdown(TextAbout.htrflow_tab3)
                    with gr.Tab("Text recognition"):
                        gr.Markdown(TextAbout.htrflow_tab4)

        with gr.Tab("FAQ & Discussion"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextHowTo.text_faq)
                with gr.Column():
                    gr.Markdown(TextHowTo.text_discussion)

        with gr.Tab("Contributions"):
            with gr.Row():
                gr.Markdown(TextAbout.contributions)

        with gr.Tab("Changelog & Roadmap"):
            with gr.Row():
                with gr.Column():
                    with gr.Accordion("Current Changelog", open=True):
                        gr.Markdown(TextAbout.current_changelog)
                    with gr.Accordion("Old Changelog", open=False):
                        gr.Markdown(TextAbout.old_changelog)
                with gr.Column():
                    gr.Markdown(TextAbout.roadmap)

        with gr.Tab("Duplicating for own use & API"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextHowTo.duplicatin_space_htr_text)
                    gr.Markdown(TextHowTo.figure_htr_hardware)
                    gr.Markdown(TextHowTo.duplicatin_for_privat)

                with gr.Column():
                    gr.Markdown(TextHowTo.htr_tool_api_text)
                    gr.Code(
                        value=TextHowTo.code_for_api,
                        language="python",
                        interactive=False,
                        show_label=False,
                    )

                    gr.Markdown(TextHowTo.output_code_for_api_text)

                    gr.Code(
                        value=TextHowTo.output_code_for_api,
                        language=None,
                        interactive=False,
                        show_label=False,
                    )
