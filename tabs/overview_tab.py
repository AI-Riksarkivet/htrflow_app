import gradio as gr

from helper.text.text_overview import TextOverview

with gr.Blocks() as overview:
    with gr.Tabs():
        with gr.Tab("About"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextOverview.htrflow_col1)
                with gr.Column():
                    gr.Markdown(TextOverview.htrflow_col2)
            with gr.Row():
                gr.Markdown(TextOverview.htrflow_row1)
            with gr.Row():
                with gr.Tabs():
                    with gr.Tab("Binarization"):
                        gr.Markdown(TextOverview.htrflow_tab1)
                    with gr.Tab("Region segmentation"):
                        gr.Markdown(TextOverview.htrflow_tab2)
                    with gr.Tab("Line segmentation"):
                        gr.Markdown(TextOverview.htrflow_tab3)
                    with gr.Tab("Text recognition"):
                        gr.Markdown(TextOverview.htrflow_tab4)

        with gr.Tab("Contributions"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextOverview.contributions)
                    gr.Markdown(TextOverview.huminfra_image)

        with gr.Tab("Duplicating for own use & API"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextOverview.duplicate)

                with gr.Column():
                    gr.Markdown(TextOverview.api1)
                    gr.Code(
                        value=TextOverview.api_code1,
                        language="python",
                        interactive=False,
                        show_label=False,
                    )

                    gr.Markdown(TextOverview.api2)

                    gr.Code(
                        value=TextOverview.api_code2,
                        language=None,
                        interactive=False,
                        show_label=False,
                    )

        with gr.Tab("Changelog & Roadmap"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextOverview.changelog)
                    with gr.Accordion("Previous changes", open=False):
                        gr.Markdown(TextOverview.old_changelog)
                with gr.Column():
                    gr.Markdown(TextOverview.roadmap)

        with gr.Tab("FAQ & Contact"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(TextOverview.text_faq)
                with gr.Column():
                    gr.Markdown(TextOverview.text_discussion)
