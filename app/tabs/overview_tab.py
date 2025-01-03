import gradio as gr

from app.utils.lang_helper import get_tab_updates
from app.utils.md_helper import load_markdown

TAB_LABELS = {
    "ENG": ["Overview", "About App", "Guide", "Model & Data", "Contributions", "Duplicate App", "FAQ & Contact"],
    "SWE": ["Översikt", "Om appen", "Guide", "Modell & Data", "Bidrag", "Duplicera App", "FAQ & Kontakt"],
}

with gr.Blocks() as overview:
    overview_language = gr.State(value="ENG")

    with gr.Column(variant="panel"):
        with gr.Tabs(elem_classes="top-navbar") as navbar:
            with gr.Tab("Overview") as tab_overview:
                with gr.Column(variant="panel"):
                    md1 = gr.Markdown("some text")

            with gr.Tab("About App") as tab_about:
                with gr.Column():
                    about_md = gr.Markdown(load_markdown(overview_language.value, "htrflow/htrflow_col1"))

            with gr.Tab("Guide") as tab_guide:
                with gr.Column():
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Fast track")
                            gr.Video(
                                value="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/eating_spaghetti.mp4",
                                format="mp4",
                            )
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Stepwise")
                            gr.Video(
                                "https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/htr_tool_media_cut.mp4",
                                format="mp4",
                            )

            with gr.Tab("Model & Data") as tab_model_data:
                with gr.Column():
                    # gr.Markdown(TextOverview.htrflow_row1)
                    with gr.Tabs():
                        with gr.Tab("Binarization"):
                            gr.Markdown("")  # gr.Markdown(TextOverview.htrflow_tab1)
                        with gr.Tab("Region segmentation"):
                            gr.Markdown("")  # gr.Markdown(TextOverview.htrflow_tab2)
                        with gr.Tab("Line segmentation"):
                            gr.Markdown("")  # gr.Markdown(TextOverview.htrflow_tab3)
                        with gr.Tab("Text recognition"):
                            gr.Markdown("")  # gr.Markdown(TextOverview.htrflow_tab4)

            with gr.Tab("Contributions") as tab_contributions:
                with gr.Column():
                    gr.Markdown("")  # gr.Markdown(TextOverview.contributions)
                    gr.Markdown("")  # gr.Markdown(TextOverview.huminfra_image)

            with gr.Tab("Duplicate App") as tab_duplicate_app:
                with gr.Column():
                    gr.Markdown("")  # gr.Markdown(TextOverview.duplicate)

                with gr.Column():
                    gr.Markdown("")  # gr.Markdown(TextOverview.api1)
                    # gr.Code(
                    #    value=TextOverview.api_code1,
                    #    language="python",
                    #    interactive=False,
                    #    show_label=False,)

                    gr.Markdown("")  # gr.Markdown(TextOverview.api2)

                    # gr.Code(
                    #     value=TextOverview.api_code2,
                    #     language=None,
                    #     interactive=False,
                    #     show_label=False,
                    # )

            with gr.Tab("FAQ & Contact") as tab_faq_contact:
                with gr.Column():
                    gr.Markdown("")  # gr.Markdown(TextOverview.text_faq)
                with gr.Column():
                    gr.Markdown("")  # gr.Markdown(TextOverview.text_discussion)

    overview.load(
        inputs=[overview_language],
        outputs=[about_md],
    )

    def load_md_text(selected_language):
        return load_markdown(selected_language, "htrflow/htrflow_col1")

    @overview_language.change(
        inputs=[overview_language],
        outputs=[about_md],
    )
    def change_md_text(selected_language):
        return load_markdown(selected_language, "htrflow/htrflow_col1")

    @overview_language.change(
        inputs=[overview_language],
        outputs=[
            tab_overview,
            tab_about,
            tab_guide,
            tab_model_data,
            tab_contributions,
            tab_duplicate_app,
            tab_faq_contact,
        ],
    )
    def save_language_to_browser(selected_language):
        return (*get_tab_updates(selected_language, TAB_LABELS),)
