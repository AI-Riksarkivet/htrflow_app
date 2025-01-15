import time
import gradio as gr
from htrflow.pipeline.pipeline import Pipeline
from htrflow.pipeline.steps import auto_import
import yaml


MAX_IMAGES = 5  # Maximum allowed images


with gr.Blocks() as submit:
    with gr.Column(variant="panel"):
        with gr.Group():
            with gr.Row():
                with gr.Column(scale=1):
                    batch_image_gallery = gr.Gallery(
                        file_types=["image"],
                        label="Upload the images you want to transcribe",
                        interactive=True,
                        height=400,
                        object_fit="cover",
                        columns=5,
                    )

                with gr.Column(scale=1):
                    custom_template_yaml = gr.Code(
                        value="",
                        language="yaml",
                        label="Pipeline",
                        interactive=True,
                    )
        with gr.Row():
            run_button = gr.Button("Submit", variant="primary", scale=0, min_width=160)

    @batch_image_gallery.upload(
        inputs=batch_image_gallery,
        outputs=[batch_image_gallery],
    )
    def validate_images(images):
        if len(images) > 5:
            gr.Warning(f"Maximum images you can upload is set to: {MAX_IMAGES}")
            return gr.update(value=None)
        return images

    def my_function(custom_template_yaml, batch_image_gallery, progress=gr.Progress()):
        config = yaml.safe_load(custom_template_yaml)

        image, _ = batch_image_gallery[0]

        pipe = Pipeline.from_config(config)
        print(batch_image_gallery)
        collections = auto_import(image)

        label = "HTRflow demo"

        for collection in collections:
            if "labels" in config:
                collection.set_label_format(**config["labels"])
            if label:
                collection.label = label
            collection = pipe.run(collection)

        # progress(0, desc="Starting...")
        # time.sleep(1)
        # for i in progress.tqdm(range(100)):
        #     if i == 20:
        #         gr.Info("hej morgan")
        #     if i == 50:
        #         gr.Info("hej morgan2")
        #     time.sleep(0.1)
        # gr.Info("hej morgan nu är jag klar")
        print(collection)
        return gr.skip()

    run_button.click(
        fn=my_function,
        inputs=[custom_template_yaml, batch_image_gallery],
        outputs=batch_image_gallery,
    )
