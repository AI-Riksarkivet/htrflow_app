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
            pass
        with gr.Tab("Stepwise"):
            with gr.Row():
                with gr.Row(equal_height=False):
                    gr.Markdown(TextHowTo.stepwise_htr_tool)
                with gr.Row():
                    gr.Markdown(TextHowTo.stepwise_htr_tool_tab_intro)
                with gr.Row():
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
                    gr.Markdown("output")

            pass
        with gr.Tab("Duplicating for own use"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextHowTo.duplicatin_space_htr_text)
                    gr.Markdown(TextHowTo.figure_htr_hardware)

                with gr.Column():
                    gr.Markdown(TextHowTo.duplicatin_for_privat)
