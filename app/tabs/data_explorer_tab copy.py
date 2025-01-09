import gradio as gr
from gradio_modal import Modal

output_image_placehholder = gr.Image(label="Output image", height=400, show_share_button=True)


def show_warning(selection: gr.SelectData):
    gr.Warning(f"Your choice is #{selection.index}, with image: {selection.value['image']['path']}!")


with gr.Blocks() as data_explorer:
    with gr.Row(variant="panel"):
        with gr.Column(scale=1):
            output_dataframe_pipeline = gr.Textbox(label="Path", info="path s3 or path, hf-dataset.")
            with gr.Group():
                (
                    gr.Dropdown(
                        ["ran", "swam", "ate", "slept"],
                        value=["swam", "slept"],
                        multiselect=True,
                        label="Activity",
                        info="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed auctor, nisl eget ",
                    ),
                )
                gr.Slider(2, 20, value=4, label="Count", info="Choose between 2 and 20")
                gr.Slider(2, 20, value=4, label="Another", info="Choose between 2 and 20")
            output_dataframe_pipeline = gr.Textbox(label="search", info="search image bla bla..")
            gr.Button("Search", variant="primary", scale=0)
        with gr.Column(scale=4):
            with gr.Tabs():
                with gr.Tab("Gallery"):
                    image_gallery = gr.Gallery(
                        [
                            "https://unsplash.com/photos/4oaDBgVROGo/download?ixid=M3wxMjA3fDB8MXxhbGx8NHx8fHx8fDJ8fDE3MTA0NjI1MzZ8&force=true&w=640",
                            "https://unsplash.com/photos/4oaDBgVROGo/download?ixid=M3wxMjA3fDB8MXxhbGx8NHx8fHx8fDJ8fDE3MTA0NjI1MzZ8&force=true&w=640",
                            "https://unsplash.com/photos/4oaDBgVROGo/download?ixid=M3wxMjA3fDB8MXxhbGx8NHx8fHx8fDJ8fDE3MTA0NjI1MzZ8&force=true&w=640",
                            "https://unsplash.com/photos/4oaDBgVROGo/download?ixid=M3wxMjA3fDB8MXxhbGx8NHx8fHx8fDJ8fDE3MTA0NjI1MzZ8&force=true&w=640",
                        ]
                        * 10,
                        allow_preview=False,
                        label="Image Gallery",
                        preview=False,
                        columns=[7],
                        rows=[10],
                        show_download_button=True,
                        show_share_button=True,
                    )
                with gr.Tab("Embeddings"):
                    pass
                    # TODO: add a embedding plot here
                    # user needs to login hf and get a datasets with embeddings

        with Modal(visible=False) as gallery_modal:
            with gr.Row():
                with gr.Column(scale=0):
                    gr.Markdown("")
                with gr.Column(scale=4):
                    gr.Image()
                with gr.Column(scale=0):
                    gr.Markdown("")

            image_gallery.select(fn=show_warning, inputs=None).then(lambda: Modal(visible=True), None, gallery_modal)
