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
                        value="""
    steps:
    - step: Segmentation
        settings:
        model: yolo
        model_settings:
            model: Riksarkivet/yolov9-lines-within-regions-1
    - step: TextRecognition
        settings:
        model: TrOCR
        model_settings:
            model: Riksarkivet/trocr-base-handwritten-hist-swe-2
    - step: OrderLines
    - step: Export
        settings:
        format: txt
        dest: outputs
                                    """,
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
                with gr.Tab("Table"):
                    pass
                with gr.Tab("Analysis"):
                    pass
