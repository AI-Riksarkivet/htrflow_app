import time

import gradio as gr

with gr.Blocks() as adv_htrflow_pipeline:
    with gr.Row(variant="panel"):
        with gr.Column(scale=2):
            image_mask2 = gr.ImageEditor(
                label="Uploaded image",
                interactive=True,
                layers=False,
                eraser=False,
                brush=False,
                height=500,
                canvas_size=(300, 300),
            )

            image_mask = gr.Gallery(
                file_types=["image"],
                label="Upload images",
                interactive=True,
                height=400,
                object_fit="cover",
                columns=5,
            )

            with gr.Group():
                with gr.Row(visible=True) as yaml_pipeline:
                    with gr.Accordion(label="Insert Yaml here:", open=True):
                        custom_template_yaml = gr.Code(
                            value="Paste your custom pipeline here",
                            language="yaml",
                            label="yaml",
                            # show_label=False,
                            interactive=True,
                            lines=3,
                        )
                    gr.Checkbox(value=True, label="Batch", container=True, scale=0)

                    # input_files_format_dropdown = gr.Dropdown(
                    #     ["Upload", "Batch", "Crop"],
                    #     value="Upload",
                    #     multiselect=False,
                    #     label="Upload method",
                    #     container=False,
                    #     scale=0,
                    #     interactive=True,
                    # )

            with gr.Row():
                run_button = gr.Button("Submit", variant="primary", scale=0)
                cancel_button = gr.Button("stop", variant="stop", scale=0)
                d = gr.DownloadButton(
                    "Download the file", visible=True, scale=0
                )  # TODO: This should be hidden until the run button is clicked

                textbox = gr.Textbox(
                    scale=0
                )  # This is for debugging runnr when run button is clicked and the stop button is clicked

                # TODO: add a upload to hf datasets
                # TODO: add a hf login button to login to upload datasets

        with gr.Column(scale=3):
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
                    # TODO add https://www.gradio.app/docs/gradio/highlightedtext and graph of run graph
                    pass

        # input_files_format_dropdown.select(lambda: gr.update(visible=True), None, image_mask)

        def foo():
            for i in range(300):
                yield i
                time.sleep(0.5)

        click_event = run_button.click(fn=foo, inputs=None, outputs=textbox)
        cancel_button.click(fn=None, inputs=None, outputs=None, cancels=[click_event])
