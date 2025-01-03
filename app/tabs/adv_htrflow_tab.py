import gradio as gr

with gr.Blocks() as adv_htrflow_pipeline:
    with gr.Row(variant="panel"):
        with gr.Column():
            gr.Markdown("<h2>Templates</h2>")
            # TODO: We want to either crop or draw polygon or bbox and send it to the custom model. Or just as the image is.
            # TODO: For the viewer we should be able to select from the output of the model what for values we want to
            gr.ImageMask()

            with gr.Group():
                with gr.Row(visible=True) as yaml_pipeline:
                    custom_template_yaml = gr.Code(
                        value="Paste your custom pipeline here",
                        language="yaml",
                        label="yaml",
                        interactive=True,
                    )

            with gr.Row():
                gr.Button("Submit", variant="primary", scale=0)

        with gr.Column():
            gr.Markdown("<h2>Viewer</h2>")
            with gr.Tabs():
                with gr.Tab("HTR ouput"):
                    gr.CheckboxGroup(
                        ["Reading Order", "Line", "Region", "Word"],
                        info="Checkboxgroup should be basedon output structure from htrflow",
                    )

                    gr.Image()
                with gr.Tab("Graph Excution"):
                    pass
                with gr.Tab("Table"):
                    pass
                with gr.Tab("Analysis"):
                    pass
