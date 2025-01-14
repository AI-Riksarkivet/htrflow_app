import gradio as gr


with gr.Blocks() as adv_htrflow_pipeline:
    with gr.Row(variant="panel"):
        with gr.Column(scale=3):

            image_batch_input = gr.Gallery(
                file_types=["image"],
                label="Upload images",
                interactive=True,
                object_fit="cover",
                preview=True,
                columns=5,
            )

            with gr.Row(visible=True) as yaml_pipeline:
                with gr.Accordion(label="Run Template", open=False):

                    custom_template_yaml = gr.Code(
                        value="Paste your custom pipeline here",
                        language="yaml",
                        label="yaml",
                        # show_label=False,
                        interactive=True,
                        lines=5,
                    )

            with gr.Row():
                run_button = gr.Button("Submit", variant="primary", scale=0)
                cancel_button = gr.Button(
                    "stop", variant="stop", scale=0, visible=False
                )
                d = gr.DownloadButton(
                    "Download the file", visible=False, scale=0
                )  # TODO: This should be hidden until the run button is clicked

                textbox_ = gr.Textbox(scale=0, visible=False)

        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("HTR ouput"):
                    gr.CheckboxGroup(
                        ["Reading Order", "Line", "Region", "Word"],
                        info="Checkboxgroup should be basedon output structure from htrflow",
                    )

                    gr.Image(
                        interactive=False,
                        show_fullscreen_button=True,
                        show_share_button=True,
                    )

                with gr.Tab("Table"):
                    pass
                with gr.Tab("Analysis"):
                    # TODO add https://www.gradio.app/docs/gradio/highlightedtext and graph of run graph
                    pass

        def foo():
            gr.Info("hello morgan")
            return gr.update(visible=True), "test"

        click_event = run_button.click(
            fn=foo, inputs=None, outputs=[cancel_button, textbox_]
        ).then(fn=lambda: gr.update(visible=False), inputs=None, outputs=cancel_button)

        cancel_button.click(
            fn=lambda: gr.update(visible=False),
            inputs=None,
            outputs=cancel_button,
            cancels=[click_event],
        )
