import gradio as gr
from gradio_modal import Modal
import pandas as pd

from app.assets.examples import DemoImages

images_for_demo = DemoImages()


output_image_placehholder = gr.Image(
    label="Output image",
    height=400,
    show_share_button=True,
)
markdown_selected_option = gr.Markdown(value="&nbsp;", container=True)


def htr_image_placehholder(txt, method, image):
    needs_yaml_to_forward_tohtrflow_ = """steps:
"""
    print(method)

    return txt, method, image


with gr.Blocks() as examples:
    with gr.Row(variant="panel"):
        with gr.Column():
            example_text_input_placeholder = gr.Markdown(visible=False, container=False)
            example_method_input_placeholder = gr.Markdown(visible=False, container=False)
            example_text_output_placeholder = gr.Markdown(visible=False, container=False)

            user_image_input = gr.Image(visible=False, container=False)

            gr.Examples(  # TODO: add so example has a alto xml file on hf datasets
                fn=htr_image_placehholder,
                examples=images_for_demo.examples_list,
                inputs=[
                    example_text_input_placeholder,
                    example_method_input_placeholder,
                    user_image_input,
                ],
                outputs=[example_text_output_placeholder, markdown_selected_option, output_image_placehholder],
                cache_examples=True,
                cache_mode="eager",
                label="Example images",
                examples_per_page=6,
            )

        with gr.Column():
            with gr.Tabs():
                with gr.Tab("Viewer"):
                    with gr.Group():
                        with gr.Row():
                            output_image_placehholder.render()
                        with gr.Row():
                            markdown_selected_option.render()
                            show_output_modal = gr.Button("Show output", variant="secondary", scale=0)
                        with gr.Row():
                            output_dataframe_pipeline = gr.Textbox(label="Click text", info="click on image bla bla..")
                with gr.Tab("YAML, DF, Graph?") as htrflow_output_table_tab:
                    with gr.Group():
                        with gr.Row():
                            output_dataframe_pipeline = gr.Image(label="Output image", interactive=False, height="100")
                        with gr.Row():
                            output_dataframe_pipeline = gr.Dataframe(label="Output image", col_count=2)

                with Modal(visible=False) as output_modal:
                    output_files_pipeline = gr.Files(label="Output files", height=100, visible=True, scale=0)
                    output_yaml_code = gr.Code(language="yaml", label="yaml", interactive=True, visible=True, scale=0)
                    # TODO: yaml should parse from datasets.. and show the yaml code

        show_output_modal.click(lambda: Modal(visible=True), None, output_modal)
