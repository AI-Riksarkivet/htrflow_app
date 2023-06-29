from typing import Protocol

import mmcv
import numpy as np

from htr_pipeline.utils.parser_xml import XmlParser
from src.htr_pipeline.inferencer import Inferencer
from src.htr_pipeline.utils.helper import timer_func
from src.htr_pipeline.utils.preprocess_img import Preprocess
from src.htr_pipeline.utils.process_xml import XMLHelper


class Pipeline:
    def __init__(self, inferencer: Inferencer) -> None:
        self.inferencer = inferencer
        self.xml = XMLHelper()
        self.preprocess_img = Preprocess()

    @timer_func
    def running_htr_pipeline(
        self,
        input_image: np.ndarray,
        pred_score_threshold_regions: float = 0.4,
        pred_score_threshold_lines: float = 0.4,
        containments_threshold: float = 0.5,
    ) -> str:
        input_image = self.preprocess_img.binarize_img(input_image)
        image = mmcv.imread(input_image)

        rendered_xml = self.xml.image_to_page_xml(
            image, pred_score_threshold_regions, pred_score_threshold_lines, containments_threshold, self.inferencer
        )

        return rendered_xml

    @timer_func
    def visualize_xml(self, input_image: np.ndarray) -> np.ndarray:
        self.xml_visualizer_and_parser = XmlParser()
        bin_input_image = self.preprocess_img.binarize_img(input_image)
        xml_image = self.xml_visualizer_and_parser.visualize_xml(bin_input_image)
        return xml_image

    @timer_func
    def parse_xml_to_txt(self) -> None:
        self.xml_visualizer_and_parser.xml_to_txt()


class PipelineInterface(Protocol):
    def __init__(self, inferencer: Inferencer) -> None:
        ...

    def running_htr_pipeline(
        self,
        input_image: np.ndarray,
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
