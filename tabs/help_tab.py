import gradio as gr

from helper.text.text_help import TextHowTo

with gr.Blocks() as help_tab:
    with gr.Tabs():
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
