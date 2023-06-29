from typing import Protocol, Tuple

import gradio as gr
import mmcv
import numpy as np

from src.htr_pipeline.models import HtrModels
from src.htr_pipeline.utils.filter_segmask import FilterSegMask
from src.htr_pipeline.utils.helper import timer_func
from src.htr_pipeline.utils.order_of_object import OrderObject
from src.htr_pipeline.utils.preprocess_img import Preprocess
from src.htr_pipeline.utils.process_segmask import SegMaskHelper


class Inferencer:
    def __init__(self, local_run=False):
        htr_models = HtrModels(local_run)
        self.seg_model = htr_models.load_region_model()
        self.line_model = htr_models.load_line_model()
        self.htr_model_inferencer = htr_models.load_htr_model()

        self.process_seg_mask = SegMaskHelper()
        self.postprocess_seg_mask = FilterSegMask()
        self.ordering = OrderObject()
        self.preprocess_img = Preprocess()

    @timer_func
    def predict_regions(self, input_image, pred_score_threshold=0.5, containments_threshold=0.5, visualize=True):
        input_image = self.preprocess_img.binarize_img(input_image)

        image = mmcv.imread(input_image)
        result = self.seg_model(image, return_datasample=True)
        result_pred = result["predictions"][0]

        filtered_result_pred = self.postprocess_seg_mask.filter_on_pred_threshold(
            result_pred, pred_score_threshold=pred_score_threshold
        )

        if len(filtered_result_pred.pred_instances.masks) == 0:
            raise gr.Error("No Regions were predicted by the model")

        else:
            result_align = self.process_seg_mask.align_masks_with_image(filtered_result_pred, image)
            result_clean = self.postprocess_seg_mask.remove_overlapping_masks(
                predicted_mask=result_align, containments_threshold=containments_threshold
            )

            if visualize:
                result_viz = self.seg_model.visualize(
                    inputs=[image], preds=[result_clean], return_vis=True, no_save_vis=True
                )[0]
            else:
                result_viz = None

            regions_cropped, polygons = self.process_seg_mask.crop_masks(result_clean, image)
            order = self.ordering.order_regions_marginalia(result_clean)

            regions_cropped_ordered = [regions_cropped[i] for i in order]
            polygons_ordered = [polygons[i] for i in order]
            masks_ordered = [result_clean.pred_instances.masks[i] for i in order]

            return result_viz, regions_cropped_ordered, polygons_ordered, masks_ordered

    @timer_func
    def predict_lines(
        self,
        image,
        pred_score_threshold=0.5,
        containments_threshold=0.5,
        line_spacing_factor=0.5,
        visualize=True,
        custom_track=True,
    ):
        result_tl = self.line_model(image, return_datasample=True)
        result_tl_pred = result_tl["predictions"][0]

        filtered_result_tl_pred = self.postprocess_seg_mask.filter_on_pred_threshold(
            result_tl_pred, pred_score_threshold=pred_score_threshold
        )

        if len(filtered_result_tl_pred.pred_instances.masks) == 0 and custom_track:
            raise gr.Error("No Lines were predicted by the model")

        elif len(filtered_result_tl_pred.pred_instances.masks) == 0 and not custom_track:
            return None, None, None

        else:
            result_tl_align = self.process_seg_mask.align_masks_with_image(filtered_result_tl_pred, image)
            result_tl_clean = self.postprocess_seg_mask.remove_overlapping_masks(
                predicted_mask=result_tl_align, containments_threshold=containments_threshold
            )

            if visualize:
                result_viz = self.seg_model.visualize(
                    inputs=[image], preds=[result_tl_clean], return_vis=True, no_save_vis=True
                )[0]
            else:
                result_viz = None

            lines_cropped, lines_polygons = self.process_seg_mask.crop_masks(result_tl_clean, image)
            ordered_indices = self.ordering.order_lines(
                line_image=result_tl_clean, line_spacing_factor=line_spacing_factor
            )

            lines_cropped_ordered = [lines_cropped[i] for i in ordered_indices]
            lines_polygons_ordered = [lines_polygons[i] for i in ordered_indices]

            return result_viz, lines_cropped_ordered, lines_polygons_ordered

    @timer_func
    def transcribe(self, line_cropped):
        result_rec = self.htr_model_inferencer(line_cropped)
        return result_rec["predictions"][0]["text"], result_rec["predictions"][0]["scores"]

    # def transcribe_different_model(self, image):
    #     processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    #     model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

    #     # prepare image
    #     pixel_values = processor(image, return_tensors="pt").pixel_values

    #     # generate (no beam search)
    #     generated_ids = model.generate(pixel_values)

    #     # decode
    #     generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    #     return generated_text


class InferencerInterface(Protocol):
    def predict_regions(
        self,
        image: np.array,
        pred_score_threshold: float,
        containments_threshold: float,
        visualize: bool = False,
    ) -> Tuple:
        ...

    def predict_lines(
        self,
        text_region: np.array,
        pred_score_threshold: float,
        containments_threshold: float,
        visualize: bool = False,
        custom_track: bool = False,
    ) -> Tuple:
        ...

    def transcribe(
        self,
        line: np.array,
    ) -> Tuple[str, float]:
        ...


if __name__ == "__main__":
    prediction_model = Inferencer()
