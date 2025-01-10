import gradio as gr


def display_dataset(dataset_repo):
    return gr.HTML(
        f"""<iframe
    src="https://huggingface.co/datasets/{dataset_repo}/embed/viewer/default/train"
    frameborder="0"
    width="100%"
    height="700px"
></iframe>"""
    )


with gr.Blocks() as data_explorer:
    with gr.Row(variant="panel"):
        with gr.Column(scale=0, min_width=160):
            input_datasets_path = gr.Textbox(
                label="HF datasets",
                placeholder="Gabriel/linkoping",
                scale=0,
                container=False,
            )
            view_dataset = gr.Button("View dataseet", variant="primary", scale=0)
            # gr.LoginButton("Login to HF", variant="secondary", scale=0)
        with gr.Column():
            iframe_output = gr.HTML()

        view_dataset.click(
            fn=display_dataset,
            inputs=input_datasets_path,
            outputs=[iframe_output],
        )
