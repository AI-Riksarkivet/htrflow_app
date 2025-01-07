import time

import gradio as gr

with gr.Blocks() as adv_htrflow_pipeline:
    with gr.Row(variant="panel"):
        with gr.Column():
            # TODO: We want to either crop or draw polygon or bbox and send it to the custom model. Or just as the image is.
            # TODO: For the viewer we should be able to select from the output of the model what for values we want to
            # TODO: add batch predictions here..
            # TODO: add load from s3, local, hf daasets( however everything could go through hf_datasets).

            image_mask = gr.ImageMask(interactive=True)

            with gr.Group():
                with gr.Row(visible=True) as yaml_pipeline:
                    with gr.Accordion(label="Insert Yaml", open=False):
                        custom_template_yaml = gr.Code(
                            value="Paste your custom pipeline here",
                            language="yaml",
                            label="yaml",
                            interactive=True,
                        )
                    test = gr.Dropdown(  # TODO: This should be a dropdown to decide input image or mask or s3 or local path
                        ["Upload", "Draw", "s3", "local"],
                        value="Upload",
                        multiselect=False,
                        label="Upload method",
                        container=False,
                        scale=0,
                        interactive=True,
                    )

            with gr.Row():
                run_button = gr.Button("Submit", variant="primary", scale=0)
                cancel_button = gr.Button(
                    "stop", variant="stop", scale=0
                )  # TODO: This should be a cancel button and be hidden until the run button is clicked
                d = gr.DownloadButton(
                    "Download the file", visible=True, scale=0
                )  # TODO: This should be hidden until the run button is clicked

                textbox = gr.Textbox(
                    scale=0
                )  # This is for debugging runnr when run button is clicked and the stop button is clicked

                # TODO: add a upload to hf datasets
                # TODO: add a hf login button to login to upload datasets

        with gr.Column():
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

        test.select(lambda: gr.update(visible=True), None, image_mask)

        def foo():
            for i in range(300):
                yield i
                time.sleep(0.5)

        click_event = run_button.click(fn=foo, inputs=None, outputs=textbox)
        cancel_button.click(fn=None, inputs=None, outputs=None, cancels=[click_event])
