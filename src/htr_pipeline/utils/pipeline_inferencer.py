import gradio as gr
from tqdm import tqdm

from src.htr_pipeline.utils.process_segmask import SegMaskHelper
from src.htr_pipeline.utils.xml_helper import XMLHelper

terminate = False

# TODO check why region is so slow to start.. Is their error with loading the model?


class PipelineInferencer:
    def __init__(self, process_seg_mask: SegMaskHelper, xml_helper: XMLHelper):
        self.process_seg_mask = process_seg_mask
        self.xml_helper = xml_helper

    def image_to_page_xml(
        self, image, pred_score_threshold_regions, pred_score_threshold_lines, containments_threshold, inferencer
    ):
        template_data = self.xml_helper.prepare_template_data(self.xml_helper.xml_file_name, image)
        template_data["textRegions"] = self._process_regions(
            image, inferencer, pred_score_threshold_regions, pred_score_threshold_lines, containments_threshold
        )

        return self.xml_helper.render(template_data)

    def _process_regions(
        self,
        image,
        inferencer,
        pred_score_threshold_regions,
        pred_score_threshold_lines,
        containments_threshold,
        htr_threshold=0.6,
    ):
        global terminate

        _, regions_cropped_ordered, reg_polygons_ordered, reg_masks_ordered = inferencer.predict_regions(
            image,
            pred_score_threshold=pred_score_threshold_regions,
            containments_threshold=containments_threshold,
            visualize=False,
        )
        gr.Info(f"Found {len(regions_cropped_ordered)} Regions to parse")
        region_data_list = []
        for i, data in tqdm(enumerate(zip(regions_cropped_ordered, reg_polygons_ordered, reg_masks_ordered))):
            if terminate:
                break
            region_data = self._create_region_data(
                data, i, inferencer, pred_score_threshold_lines, containments_threshold, htr_threshold
            )
            if region_data:
                region_data_list.append(region_data)

        return region_data_list

    def _create_region_data(
        self, data, index, inferencer, pred_score_threshold_lines, containments_threshold, htr_threshold
    ):
        text_region, reg_pol, mask = data
        region_data = {"id": f"region_{index}", "boundary": reg_pol}

        text_lines, htr_scores = self._process_lines(
            text_region,
            inferencer,
            pred_score_threshold_lines,
            containments_threshold,
            mask,
            region_data["id"],
            htr_threshold,
        )

        if not text_lines:
            return None

        region_data["textLines"] = text_lines
        mean_htr_score = sum(htr_scores) / len(htr_scores) if htr_scores else 0

        return region_data if mean_htr_score > htr_threshold + 0.1 else None

    def _process_lines(
        self, text_region, inferencer, pred_score_threshold, containments_threshold, mask, region_id, htr_threshold=0.6
    ):
        _, lines_cropped_ordered, line_polygons_ordered = inferencer.predict_lines(
            text_region, pred_score_threshold, containments_threshold, visualize=False, custom_track=False
        )

        if not lines_cropped_ordered:
            return None, []

        line_polygons_ordered_trans = self.process_seg_mask._translate_line_coords(mask, line_polygons_ordered)

        text_lines = []
        htr_scores = []

        id_number = region_id.split("_")[1]
        total_lines_len = len(lines_cropped_ordered)

        gr.Info(f" Region {id_number}, found {total_lines_len} lines to parse and transcribe.")

        global terminate

        for index, (line, line_pol) in enumerate(zip(lines_cropped_ordered, line_polygons_ordered_trans)):
            if terminate:
                break
            line_data, htr_score = self._create_line_data(line, line_pol, index, region_id, inferencer, htr_threshold)

            if line_data:
                text_lines.append(line_data)
            htr_scores.append(htr_score)

            remaining_lines = total_lines_len - index - 1

            if (index + 1) % 10 == 0 and remaining_lines > 5:  # +1 because index starts at 0
                gr.Info(
                    f"Region {id_number}, parsed {index + 1} lines. Still {remaining_lines} lines left to transcribe."
                )

        return text_lines, htr_scores

    def _create_line_data(self, line, line_pol, index, region_id, inferencer, htr_threshold):
        line_data = {"id": f"line_{region_id}_{index}", "boundary": line_pol}

        transcribed_text, htr_score = inferencer.transcribe(line)
        line_data["unicode"] = self.xml_helper.escape_xml_chars(transcribed_text)
        line_data["pred_score"] = round(htr_score, 4)

        return line_data if htr_score > htr_threshold else None, htr_score


if __name__ == "__main__":
    pass
