import gradio as gr

from app.texts_langs.text_overview import TextOverview

default_value_radio_overview = "Home"
overview_choices_eng = [
    "Home",
    "About App",
    "Guide",
    "Model & Data",
    "Contributions",
    "Duplicate App",
    "FAQ & Contact",
]


def toggle_visibility(selected_option):
    return [
        gr.update(visible=(selected_option == "Home")),
        gr.update(visible=(selected_option == "About App")),
        gr.update(visible=(selected_option == "Guide")),
        gr.update(visible=(selected_option == "Model & Data")),
        gr.update(visible=(selected_option == "Contributions")),
        gr.update(visible=(selected_option == "FAQ & Contact")),
        gr.update(visible=(selected_option == "Duplicate App")),
    ]


with gr.Blocks() as overview:
    with gr.Row():

        with gr.Column(visible=True, min_width=170, scale=0, variant="panel") as sidebar:
            options_overview = gr.Radio(
                overview_choices_eng,
                label="Side Navigation",
                container=False,
                value=default_value_radio_overview,
                elem_id="column-form",
                min_width=100,
                scale=0,
            )

        with gr.Column(variant="panel") as overview_main:
            with gr.Row(visible=True) as overview_home:
                with gr.Column():

                    gr.Markdown("## landing page to explain version")
                    gr.Markdown("## htrflow app 1.0.0")
                    gr.Markdown("## links to different stuff")
                    gr.Markdown("## Whats new..")

            with gr.Row(visible=False) as overview_about:
                with gr.Column():
                    gr.Markdown(TextOverview.htrflow_col1)
                    gr.Markdown(TextOverview.htrflow_col2)

            with gr.Row(visible=False) as overview_guide:
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

            with gr.Row(visible=False) as overview_model_data:
                with gr.Column():
                    gr.Markdown(TextOverview.htrflow_row1)
                    with gr.Tabs():
                        with gr.Tab("Binarization"):
                            gr.Markdown(TextOverview.htrflow_tab1)
                        with gr.Tab("Region segmentation"):
                            gr.Markdown(TextOverview.htrflow_tab2)
                        with gr.Tab("Line segmentation"):
                            gr.Markdown(TextOverview.htrflow_tab3)
                        with gr.Tab("Text recognition"):
                            gr.Markdown(TextOverview.htrflow_tab4)

            with gr.Row(visible=False) as overview_contribute:
                with gr.Column():
                    gr.Markdown(TextOverview.contributions)
                    gr.Markdown(TextOverview.huminfra_image)

            with gr.Row(visible=False) as overview_duplicate:
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

            with gr.Row(visible=False) as overview_faq:
                with gr.Column():
                    gr.Markdown(TextOverview.text_faq)
                with gr.Column():
                    gr.Markdown(TextOverview.text_discussion)
        with gr.Column(visible=True, min_width=0, scale=0) as empty:
            pass

    options_overview.change(
        lambda choice: toggle_visibility(choice),
        inputs=options_overview,
        outputs=[
            overview_home,
            overview_about,
            overview_guide,
            overview_model_data,
            overview_contribute,
            overview_duplicate,
            overview_faq,
        ],
    )
