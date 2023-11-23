from typing import Protocol

import mmcv
import numpy as np

from src.htr_pipeline.inferencer import Inferencer
from src.htr_pipeline.utils.helper import timer_func
from src.htr_pipeline.utils.parser_xml import XmlParser
from src.htr_pipeline.utils.pipeline_inferencer import PipelineInferencer
from src.htr_pipeline.utils.preprocess_img import Preprocess
from src.htr_pipeline.utils.process_segmask import SegMaskHelper
from src.htr_pipeline.utils.visualize_xml import XmlViz
from src.htr_pipeline.utils.xml_helper import XMLHelper


class Pipeline:
    def __init__(self, inferencer: Inferencer) -> None:
        self.inferencer = inferencer
        self.preprocess_img = Preprocess()
        self.pipeline_inferencer = PipelineInferencer(SegMaskHelper(), XMLHelper())

    @timer_func
    def running_htr_pipeline(
        self,
        input_image: np.ndarray,
        htr_tool_transcriber_model_dropdown,
        pred_score_threshold_regions: float = 0.4,
        pred_score_threshold_lines: float = 0.4,
        containments_threshold: float = 0.5,
    ) -> str:
        input_image = self.preprocess_img.binarize_img(input_image)
        image = mmcv.imread(input_image)

        rendered_xml = self.pipeline_inferencer.image_to_page_xml(
            image,
            htr_tool_transcriber_model_dropdown,
            pred_score_threshold_regions,
            pred_score_threshold_lines,
            containments_threshold,
            self.inferencer,
        )

        return rendered_xml

    @timer_func
    def visualize_xml(self, input_image: np.ndarray) -> np.ndarray:
        xml_viz = XmlViz()
        bin_input_image = self.preprocess_img.binarize_img(input_image)
        xml_image, text_polygon_dict = xml_viz.visualize_xml(bin_input_image)
        return xml_image, text_polygon_dict

    @timer_func
    def parse_xml_to_txt(self) -> None:
        xml_visualizer_and_parser = XmlParser()
        xml_visualizer_and_parser.xml_to_txt()


class PipelineInterface(Protocol):
    def __init__(self, inferencer: Inferencer) -> None:
        ...

    def running_htr_pipeline(
        self,
        input_image: np.ndarray,
        htr_tool_transcriber_model_dropdown: str,
        pred_score_threshold_regions: float = 0.4,
        pred_score_threshold_lines: float = 0.4,
        containments_threshold: float = 0.5,
    ) -> str:
        ...

    def visualize_xml(self, input_image: np.ndarray) -> np.ndarray:
        ...

    def parse_xml_to_txt(self) -> None:
        ...


if __name__ == "__main__":
    prediction_model = Inferencer()
    pipeline = Pipeline(prediction_model)
