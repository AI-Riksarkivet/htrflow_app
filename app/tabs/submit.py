import time
import gradio as gr

default_template_yaml = """
steps:

# Region segmentation
- step: Segmentation
    settings:
    model: yolo
    model_settings:
        model: Riksarkivet/yolov9-regions-1
        revision: 7c44178d85926b4a096c55c89bf224855a201fbf
    generation_settings:
        batch_size: 32
        half: true
        conf: 0.5  # confidence threshold - keep all boxes with conf > 0.5

# Line segmentation
- step: Segmentation
    settings:
    model: yolo
    model_settings:
        model: Riksarkivet/yolov9-lines-within-regions-1
        revision: ea2f8987cba316abc62762f3030266ec8875338d
    generation_settings:
        batch_size: 16
        half: true

- step: FilterRegionsByShape
    settings:
    min_ratio: 0.5  # keep lines that have at least a 1:2 (=0.5) width-to-height ratio

- step: TextRecognition
    settings:
    model: ORTWordLevelTrocr
    model_settings:
        model: ./model
    generation_settings:
        batch_size: 64
        num_beams: 1
        max_new_tokens: 64

- step: ReadingOrderMarginalia
    settings:
    two_page: true

# Remove garbage lines: anything below 0.7 in confidence
- step: RemoveLowTextConfidenceLines
    settings:
    threshold: 0.7

# Remove garbage regions: any region with mean confidence < 0.75 AFTER the below-0.7 lines have been removed
- step: RemoveLowTextConfidenceRegions
    settings:
    threshold: 0.75

- step: Export
    settings:
    dest: output/job
    format: alto
    template_dir: /app/config
    template_name: alto-with-RA-pageID

- step: Export
    settings:
    dest: output/job
    format: json
    indent: null

# Sets label format to regionX_lineY_wordZ
labels:
    level_labels:
    - region
    - line
    - word
    sep: _
    template: "{label}{number}"
"""

with gr.Blocks() as submit:
    # Row 1: Please upload the image message
    #with gr.Row():
    #    docs_link = gr.HTML(
    #        value=''
    #    )
#
    # Row 2: Image Upload and Editor
    with gr.Row(variant="panel"):
        image_editor = gr.ImageEditor(
            label="Upload the image you want to transcribe",
            sources="upload",
            interactive=True,
            layers=False,
            eraser=False,
            brush=False,
            height=400,
            transforms="crop",
            crop_size="16,5",
            visible=False,
        )
        image_mask = gr.Gallery(
            file_types=["image"],
            label="Upload the image you want to transcribe",
            interactive=True,
            height=400,
            object_fit="cover",
            columns=5,
        )

    # Row 3: Run Template Accordion
    with gr.Row():
        with gr.Accordion(label="Pipeline yaml (expand to customize settings)", open=False):
            # Add the documentation link with an emoji first
            docs_link = gr.HTML(
                value='<p>Bellow is the pipeline yaml that will be used. <a href="https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html#example-pipelines" target="_blank">📚 Click here 📚</a> for a detailed description on how to customize the configuration</p>'
            )
            # Then, the code block with the template YAML
            custom_template_yaml = gr.Code(
                value=default_template_yaml,  # Set the default template YAML here
                language="yaml",
                label="yaml",
                interactive=True,
                lines=5,
            )

    # Row 4: Submit and Cancel Buttons
    with gr.Row():
        run_button = gr.Button("Submit", variant="primary", scale=0)
        cancel_button = gr.Button("Stop", variant="stop", scale=0, visible=False)
        d = gr.DownloadButton("Download the file", visible=False, scale=0)
        textbox_ = gr.Textbox(scale=0, visible=False)

    # Cancel button functionality
    cancel_button.click(
        fn=lambda: gr.update(visible=False),
        inputs=None,
        outputs=cancel_button,
    )

    # Image Editor Upload handling
    image_editor.upload(
        fn=None,
        inputs=None,
        outputs=None,
        js=""" 
        () => {
            const button = document.querySelector('button[aria-label="Transform button"][title="Transform button"]');
            if (button) {
                button.click();
                console.log('Transform button clicked.');
            } else {
                console.error('Transform button not found.');
            }
        }
        """,
    ).then(
        fn=lambda: gr.update(crop=None), inputs=None, outputs=image_editor
    )
