import gradio as gr

from helper.text.text_howto import TextHowTo

with gr.Blocks() as help_tab:
    gr.Markdown("lorem ipsum...")
    with gr.Tabs():
        with gr.Tab("Discussion & FAQ"):
            pass

        with gr.Tab("Fast track"):
            pass
        with gr.Tab("Stepwise"):
            with gr.Row():
                with gr.Accordion("Info", open=False) as example_accord:
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
            pass
        with gr.Tab("Duplicating for own use"):
            pass
