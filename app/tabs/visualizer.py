import gradio as gr
import pandas as pd
import numpy as np
import time
from collections import defaultdict
from typing import List, Dict, Any

from htrflow.volume.volume import Collection, ImageNode, PageNode
from htrflow.utils.draw import draw_polygons
from htrflow.utils import imgproc
from htrflow.results import Segment


def load_visualize_state_from_submit(col: Collection, progress):
    results = []

    total_steps = len(col.pages)

    for page_idx, page_node in enumerate(col):
        page_node.to_original_size()
        page_image = page_node.image.copy()

        progress((page_idx + 1) / total_steps, desc="Running Visualizer")

        line_polygons = []
        line_crops = []
        recog_conf_values = {}

        for i, node in enumerate(page_node.traverse(filter=lambda n: n.is_line())):
            if node.polygon:
                line_polygons.append(node.polygon)

            try:
                cropped_line_img = imgproc.crop(page_image, node.bbox)
                cropped_line_img = np.clip(cropped_line_img, 0, 255).astype(np.uint8)
                line_crops.append(cropped_line_img)
            except Exception:
                continue

            if node.text_result:
                recog_conf_values[i] = list(
                    zip(node.text_result.texts, node.text_result.scores)
                )

        annotated_image = draw_polygons(image=page_image, polygons=line_polygons)
        annotated_page_node = np.clip(annotated_image, 0, 255).astype(np.uint8)

        results.append(
            {
                "page_image": page_node,
                "annotated_page_node": annotated_page_node,
                "line_crops": line_crops,
                "recog_conf_values": _convert_conf_values_to_df(recog_conf_values),
            }
        )

    return results


def _convert_conf_values_to_df(
    conf_values: Dict[int, List[tuple[str, float]]]
) -> pd.DataFrame:
    """Convert recognition confidence values to a pandas DataFrame."""
    return pd.DataFrame(
        [
            {"Transcription": text, "Confidence Score": f"{score:.4f}"}
            for values in conf_values.values()
            for text, score in values
        ]
    )


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
                    "Visualize", scale=0, min_width=200, variant="primary"
                )

                progress_bar = gr.Textbox(visible=False, show_label=False)

            with gr.Column():
                cropped_image_gallery = gr.Gallery(
                    interactive=False,
                    preview=True,
                    label="Cropped Polygons",
                    height=400,
                )
                df_for_cropped_images = gr.Dataframe(
                    label="Cropped Transcriptions",
                    headers=["Transcription", "Confidence Score"],
                    interactive=False,
                )

    def on_visualize_button_clicked(collection_viz, progress=gr.Progress()):
        """
        This function:
        - Receives the collection (collection_viz).
        - Processes it into 'results' (list of dicts with annotated_page_node, line_crops, dataframe).
        - Returns:
            1) 'results' as state
            2) List of annotated_page_node images (one per page) to populate viz_image_gallery
        """
        if not collection_viz:
            return None, []

        results = load_visualize_state_from_submit(collection_viz, progress)
        annotated_images = [r["annotated_page_node"] for r in results]
        return results, annotated_images, gr.skip()

    visualize_button.click(lambda: gr.update(visible=True), outputs=progress_bar).then(
        fn=on_visualize_button_clicked,
        inputs=collection_viz_state,
        outputs=[result_collection_viz_state, viz_image_gallery, progress_bar],
    ).then(lambda: gr.update(visible=False), outputs=progress_bar)

    @viz_image_gallery.change(
        inputs=result_collection_viz_state,
        outputs=[cropped_image_gallery, df_for_cropped_images],
    )
    def update_c_gallery_and_dataframe(results):
        selected = results[0]
        return selected["line_crops"], selected["recog_conf_values"]

    @viz_image_gallery.select(
        inputs=result_collection_viz_state,
        outputs=[cropped_image_gallery, df_for_cropped_images],
    )
    def on_dataframe_select(evt: gr.SelectData, results):
        """
        evt.index => the index of the selected image in the gallery
        results => the state object from result_collection_viz_state

        Return the line crops and the recognized text for that index.
        """
        if results is None or evt.index is None:
            return [], pd.DataFrame(columns=["Transcription", "Confidence Score"])

        idx = evt.index
        selected = results[idx]

        return selected["line_crops"], selected["recog_conf_values"]

    @df_for_cropped_images.select(
        outputs=[cropped_image_gallery],
    )
    def on_dataframe_select(evt: gr.SelectData):
        return gr.update(selected_index=evt.index[0])

    @cropped_image_gallery.select(
        inputs=df_for_cropped_images, outputs=df_for_cropped_images
    )
    def return_image_from_gallery(df, evt: gr.SelectData):
        selected_index = evt.index

        def highlight_row(row):
            return [
                (
                    "border: 1px solid blue; font-weight: bold"
                    if row.name == selected_index
                    else ""
                )
                for _ in row
            ]

        styler = df.style.apply(highlight_row, axis=1)

        return styler
