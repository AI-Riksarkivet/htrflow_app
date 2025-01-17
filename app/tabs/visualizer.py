import gradio as gr
import pandas as pd
import numpy as np
from htrflow.volume.volume import Collection
from htrflow.utils.draw import draw_polygons
from htrflow.utils import imgproc

from htrflow.results import Segment


with gr.Blocks() as visualizer:
    with gr.Column(variant="panel"):
        with gr.Row():
            collection_viz_state = gr.State()
            result_collection_viz_state = gr.State()
            with gr.Column():
                viz_image_gallery = gr.Gallery(
                    file_types=["image"],
                    label="Visualized Images from HTRflow",
                    interactive=False,
                    height=400,
                    object_fit="cover",
                    columns=5,
                    preview=True,
                )

                visualize_button = gr.Button(
                    "Visualize", scale=0, min_width=200, variant="secondary"
                )

            with gr.Column():
                # image_visualizer_annotation = gr.Image(
                #     interactive=False,
                # )

                line2 = gr.Gallery(
                    interactive=False,
                )
                textlines = gr.Dataframe()

    # @viz_image_gallery.select(outputs=image_visualizer_annotation)
    # def return_image_from_gallery(evt: gr.SelectData):
    #     return evt.value["image"]["path"]

    @visualize_button.click(
        outputs=[result_collection_viz_state, viz_image_gallery, line2, textlines]
    )
    def testie_load_pickle():
        col = Collection.from_pickle(".cache/HTRflow_demo_output.pickle")

        results = []
        for page_idx, page_node in enumerate(col):
            page_image = page_node.image.copy()

            lines = list(page_node.traverse(lambda node: node.is_line()))

            recog_conf_values = {
                i: list(zip(tr.texts, tr.scores)) if (tr := ln.text_result) else []
                for i, ln in enumerate(lines)
            }

            recog_df = pd.DataFrame(
                [
                    {"Transcription": text, "Confidence Score": f"{score:.4f}"}
                    for values in recog_conf_values.values()
                    for text, score in values
                ]
            )

            line_polygons = []
            line_crops = []
            for ln in lines:
                seg: Segment = ln.data.get("segment")
                if not seg:
                    continue

                cropped_line_img = imgproc.crop(page_image, seg.bbox)
                cropped_line_img = np.clip(cropped_line_img, 0, 255).astype(np.uint8)
                line_crops.append(cropped_line_img)

                if seg.polygon is not None:
                    line_polygons.append(seg.polygon)

            annotated_image = draw_polygons(page_image, line_polygons)
            annotated_page_node = np.clip(annotated_image, 0, 255).astype(np.uint8)
            results.append(
                {
                    "page_image": page_node,
                    "annotated_page_node": annotated_page_node,
                    "line_crops": line_crops,
                    "recog_conf_values": recog_df,
                }
            )

        return (
            results,
            [results[0]["annotated_page_node"]],
            results[0]["line_crops"],
            results[0]["recog_conf_values"],
        )
