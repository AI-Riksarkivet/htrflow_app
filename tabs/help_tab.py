import gradio as gr

from helper.text.text_help import TextHowTo

with gr.Blocks() as help_tab:
    with gr.Tabs():
        with gr.Tab("FAQ & Discussion"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextHowTo.text_faq)
                with gr.Column():
                    gr.Markdown(TextHowTo.discussion)

        with gr.Tab("Fast track"):
            gr.Markdown("WIP")
            pass
        with gr.Tab("Stepwise"):
            with gr.Row(equal_height=False):
                gr.Markdown(TextHowTo.stepwise_htr_tool)
            with gr.Row():
                gr.Markdown(TextHowTo.stepwise_htr_tool_tab_intro)
            with gr.Row():
                with gr.Tabs():
                    with gr.Tab("1. Region Segmentation"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(TextHowTo.stepwise_htr_tool_tab1)
                            with gr.Column():
                                gr.Markdown("image")
                    with gr.Tab("2. Line Segmentation"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(TextHowTo.stepwise_htr_tool_tab2)
                            with gr.Column():
                                gr.Markdown("image")
                    with gr.Tab("3. Transcribe Text"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(TextHowTo.stepwise_htr_tool_tab3)
                            with gr.Column():
                                gr.Markdown("image")
                    with gr.Tab("4. Explore Results"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(TextHowTo.stepwise_htr_tool_tab4)
                            with gr.Column():
                                gr.Markdown("image")
            with gr.Row():
                gr.Markdown(TextHowTo.stepwise_htr_tool_end)

        with gr.Tab("API"):
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
                    gr.Markdown(TextHowTo.output_code_for_api_text)

                    gr.Code(
                        value=TextHowTo.output_code_for_api,
                        language=None,
                        interactive=False,
                        show_label=False,
                    )

            pass
        with gr.Tab("Duplicating for own use"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextHowTo.duplicatin_space_htr_text)
                    gr.Markdown(TextHowTo.figure_htr_hardware)

                with gr.Column():
                    gr.Markdown(TextHowTo.duplicatin_for_privat)
