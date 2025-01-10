import xml.etree.ElementTree as ET
from io import BytesIO

import cv2
import gradio as gr
import numpy as np
import requests
from PIL import Image


def parse_alto_xml(xml_file):
    """Parse the ALTO XML file to extract polygons and text content for each TextLine."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {"alto": "http://www.loc.gov/standards/alto/ns-v4#"}

    annotations = []
    transcriptions = {}

    for text_block in root.findall(".//alto:TextBlock", ns):
        for text_line in text_block.findall("alto:TextLine", ns):
            shape = text_line.find("alto:Shape", ns)

            if shape is not None:
                polygon = shape.find("alto:Polygon", ns)
                if polygon is not None:
                    polygon_points = polygon.attrib["POINTS"]
                    points = [
                        tuple(map(int, point.split(",")))
                        for point in polygon_points.split()
                    ]
            else:
                hpos = int(text_line.attrib["HPOS"])
                vpos = int(text_line.attrib["VPOS"])
                width = int(text_line.attrib["WIDTH"])
                height = int(text_line.attrib["HEIGHT"])
                points = [
                    (hpos, vpos),
                    (hpos + width, vpos),
                    (hpos + width, vpos + height),
                    (hpos, vpos + height),
                ]

            content = " ".join(
                [
                    string.attrib["CONTENT"]
                    for string in text_line.findall("alto:String", ns)
                ]
            )
            label = text_line.attrib["ID"]

            annotations.append((points, label))
            transcriptions[label] = content

    text_area_content = "\n".join(transcriptions[label] for label in transcriptions)

    return annotations, transcriptions, text_area_content


def visualize_polygons_on_image(
    image, annotations, alpha=0.5, include_reading_order=False
):
    """Visualize polygons on the image with an optional reading order overlay."""
    overlay = image.copy()
    for _, (polygon, label) in enumerate(annotations):
        color = (
            np.random.randint(0, 255),
            np.random.randint(0, 255),
            np.random.randint(0, 255),
        )
        cv2.fillPoly(overlay, [np.array(polygon, dtype=np.int32)], color)

        if include_reading_order:
            centroid = np.mean(np.array(polygon), axis=0).astype(int)
            cv2.putText(
                overlay,
                str(label),
                tuple(centroid),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


def visualize(
    xml_file, image_source, image_id, uploaded_image, include_reading_order=False
):
    if image_source == "Use IIIF image":
        if not image_id:
            raise gr.Error("Please enter an Image ID.")
        image_url = f"https://iiifintern.ra.se/arkis!{image_id}/full/max/0/default.jpg"
        response = requests.get(image_url)
        if response.status_code != 200:
            raise gr.Error(f"Failed to download image from {image_url}")
        image = np.array(Image.open(BytesIO(response.content)))
    else:
        if uploaded_image is None:
            raise gr.Error("Please upload an image.")
        image = uploaded_image

    annotations, transcriptions, text_area_content = parse_alto_xml(xml_file)
    annotated_image = visualize_polygons_on_image(
        image, annotations, include_reading_order=include_reading_order
    )

    return annotated_image, annotations, transcriptions, text_area_content


def get_transcription_from_coords(annotations, transcriptions, evt: gr.SelectData):
    """Get the transcription for the polygon clicked in the annotated image."""
    x, y = evt.index[0], evt.index[1]
    for points, label in annotations:
        polygon = np.array(points, dtype=np.int32)
        if cv2.pointPolygonTest(polygon, (x, y), False) >= 0:
            return transcriptions.get(label, "No transcription available.")
    return "No transcription available."


with gr.Blocks(title="XML Visualization App") as app:
    with gr.Tab("Visualize"):
        annotations_state = gr.State()
        transcriptions_state = gr.State()

        with gr.Row():
            with gr.Column():
                xml_input = gr.File(label="Upload ALTO XML File", file_types=[".xml"])
            with gr.Column():
                image_source = gr.Radio(
                    choices=["Use IIIF image", "Upload your own image"],
                    label="Image Source",
                    value="Use IIIF image",
                )
                image_id_input = gr.Textbox(
                    label="Image ID",
                    placeholder="Enter image ID (e.g., 30003365_00001)",
                    visible=True,
                )
                image_upload = gr.Image(
                    label="Upload Image", type="numpy", visible=False
                )
                include_reading_order_input = gr.Checkbox(label="Include Reading Order")
                process_button = gr.Button("Visualize Alto", scale=0, variant="primary")

        def update_image_source(choice):
            if choice == "Use IIIF image":
                return [gr.update(visible=True), gr.update(visible=False)]
            else:
                return [gr.update(visible=False), gr.update(visible=True)]

        image_source.change(
            update_image_source,
            inputs=image_source,
            outputs=[image_id_input, image_upload],
        )

        with gr.Row():
            with gr.Column(scale=3):
                annotated_image_output = gr.Image(
                    label="Annotated Image", interactive=True
                )
            with gr.Column(scale=2):
                transcription_output = gr.TextArea(
                    label="Transcription",
                    interactive=False,
                    show_copy_button=True,
                    lines=30,
                )
                transcription_selected = gr.Textbox(
                    label="Selected Polygon", interactive=False, show_copy_button=True
                )

        process_button.click(
            visualize,
            inputs=[
                xml_input,
                image_source,
                image_id_input,
                image_upload,
                include_reading_order_input,
            ],
            outputs=[
                annotated_image_output,
                annotations_state,
                transcriptions_state,
                transcription_output,
            ],
        )

        annotated_image_output.select(
            get_transcription_from_coords,
            inputs=[annotations_state, transcriptions_state],
            outputs=transcription_selected,
        )

app.queue()
app.launch()
