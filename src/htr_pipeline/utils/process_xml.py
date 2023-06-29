import os
import re
from datetime import datetime

import jinja2
from tqdm import tqdm

from src.htr_pipeline.inferencer import InferencerInterface
from src.htr_pipeline.utils.process_segmask import SegMaskHelper


class XMLHelper:
    def __init__(self):
        self.process_seg_mask = SegMaskHelper()

    def image_to_page_xml(
        self,
        image,
        pred_score_threshold_regions,
        pred_score_threshold_lines,
        containments_threshold,
        inferencer: InferencerInterface,
        xml_file_name="page_xml.xml",
    ):
        img_height = image.shape[0]
        img_width = image.shape[1]
        img_file_name = xml_file_name

        template_data = self.prepare_template_data(img_file_name, img_width, img_height)

        template_data["textRegions"] = self._process_regions(
            image,
            inferencer,
            pred_score_threshold_regions,
            pred_score_threshold_lines,
            containments_threshold,
        )

        rendered_xml = self._render_xml(template_data)

        return rendered_xml

    def _transform_coords(self, input_string):
        pattern = r"\[\s*([^\s,]+)\s*,\s*([^\s\]]+)\s*\]"
        replacement = r"\1,\2"
        return re.sub(pattern, replacement, input_string)

    def _render_xml(self, template_data):
        template_loader = jinja2.FileSystemLoader(searchpath="./src/htr_pipeline/utils/templates")
        template_env = jinja2.Environment(loader=template_loader, trim_blocks=True)
        template = template_env.get_template("page_xml_2013.xml")
        rendered_xml = template.render(template_data)
        rendered_xml = self._transform_coords(rendered_xml)
        return rendered_xml

    def prepare_template_data(self, img_file_name, img_width, img_height):
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
        return {
            "created": date_time,
            "imageFilename": img_file_name,
            "imageWidth": img_width,
            "imageHeight": img_height,
            "textRegions": list(),
        }

    def _process_regions(
        self,
        image,
        inferencer: InferencerInterface,
        pred_score_threshold_regions,
        pred_score_threshold_lines,
        containments_threshold,
        htr_threshold=0.7,
    ):
        _, regions_cropped_ordered, reg_polygons_ordered, reg_masks_ordered = inferencer.predict_regions(
            image,
            pred_score_threshold=pred_score_threshold_regions,
            containments_threshold=containments_threshold,
            visualize=False,
        )

        region_data_list = []
        for i, (text_region, reg_pol, mask) in tqdm(
            enumerate(zip(regions_cropped_ordered, reg_polygons_ordered, reg_masks_ordered))
        ):
            region_id = "region_" + str(i)
            region_data = dict()
            region_data["id"] = region_id
            region_data["boundary"] = reg_pol

            text_lines, htr_scores = self._process_lines(
                text_region,
                inferencer,
                pred_score_threshold_lines,
                containments_threshold,
                mask,
                region_id,
            )

            if text_lines is None:
                continue

            region_data["textLines"] = text_lines
            mean_htr_score = sum(htr_scores) / len(htr_scores)

            if mean_htr_score > htr_threshold:
                region_data_list.append(region_data)

        return region_data_list

    def _process_lines(
        self,
        text_region,
        inferencer: InferencerInterface,
        pred_score_threshold_lines,
        containments_threshold,
        mask,
        region_id,
        htr_threshold=0.7,
    ):
        _, lines_cropped_ordered, line_polygons_ordered = inferencer.predict_lines(
            text_region,
            pred_score_threshold=pred_score_threshold_lines,
            containments_threshold=containments_threshold,
            visualize=False,
            custom_track=False,
        )

        if lines_cropped_ordered is None:
            return None, None

        line_polygons_ordered_trans = self.process_seg_mask._translate_line_coords(mask, line_polygons_ordered)

        htr_scores = list()
        text_lines = list()

        for j, (line, line_pol) in enumerate(zip(lines_cropped_ordered, line_polygons_ordered_trans)):
            line_id = "line_" + region_id + "_" + str(j)
            line_data = dict()
            line_data["id"] = line_id
            line_data["boundary"] = line_pol

            line_data["unicode"], htr_score = inferencer.transcribe(line)
            htr_scores.append(htr_score)

            if htr_score > htr_threshold:
                text_lines.append(line_data)

        return text_lines, htr_scores
