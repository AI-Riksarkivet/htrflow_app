import os

import cv2
import gradio as gr
import numpy as np
import pandas as pd

from src.htr_pipeline.inferencer import Inferencer, InferencerInterface
from src.htr_pipeline.pipeline import Pipeline, PipelineInterface
from src.htr_pipeline.utils.helper import gradio_info


class SingletonModelLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonModelLoader, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "inferencer"):
            self.inferencer = Inferencer(local_run=True)
        if not hasattr(self, "pipeline"):
            self.pipeline = Pipeline(self.inferencer)


def handling_callback_stop_inferencer():
    from src.htr_pipeline.utils import pipeline_inferencer

    pipeline_inferencer.terminate = False


# fast track
class FastTrack:
    def __init__(self, model_loader):
        self.pipeline: PipelineInterface = model_loader.pipeline

    def segment_to_xml(self, image, radio_button_choices):
        handling_callback_stop_inferencer()

        gr.Info("Excuting HTR on image")
        xml_xml = "page_xml.xml"
        xml_txt = "page_txt.txt"

        if os.path.exists(f"./{xml_xml}"):
            os.remove(f"./{xml_xml}")

        rendered_xml = self.pipeline.running_htr_pipeline(image)

        with open(xml_xml, "w") as f:
            f.write(rendered_xml)

        if os.path.exists(f"./{xml_txt}"):
            os.remove(f"./{xml_txt}")

        self.pipeline.parse_xml_to_txt()

        returned_file_extension = self.file_extenstion_to_return(radio_button_choices, xml_xml, xml_txt)

        return returned_file_extension, gr.update(visible=True)

    def visualize_image_viewer(self, image):
        xml_img, text_polygon_dict = self.pipeline.visualize_xml(image)
        return xml_img, text_polygon_dict

    def file_extenstion_to_return(self, radio_button_choices, xml_xml, xml_txt):
        if len(radio_button_choices) < 2:
            if radio_button_choices[0] == "Txt":
                returned_file_extension = xml_txt
            else:
                returned_file_extension = xml_xml
        else:
            returned_file_extension = [xml_txt, xml_xml]
        return returned_file_extension

    def get_text_from_coords(self, text_polygon_dict, evt: gr.SelectData):
        x, y = evt.index[0], evt.index[1]

        for text, polygon_coords in text_polygon_dict.items():
            if (
                cv2.pointPolygonTest(np.array(polygon_coords), (x, y), False) >= 0
            ):  # >= 0 means on the polygon or inside
                return text

    def segment_to_xml_api(self, image):
        rendered_xml = self.pipeline.running_htr_pipeline(image)
        return rendered_xml


# Custom track
class CustomTrack:
    def __init__(self, model_loader):
        self.inferencer: InferencerInterface = model_loader.inferencer

    @gradio_info("Running Segment Region")
    def region_segment(self, image, pred_score_threshold, containments_treshold):
        predicted_regions, regions_cropped_ordered, _, _ = self.inferencer.predict_regions(
            image, pred_score_threshold, containments_treshold
        )
        return predicted_regions, regions_cropped_ordered, gr.update(visible=False), gr.update(visible=True)

    @gradio_info("Running Segment Line")
    def line_segment(self, image, pred_score_threshold, containments_threshold):
        predicted_lines, lines_cropped_ordered, _ = self.inferencer.predict_lines(
            image, pred_score_threshold, containments_threshold
        )
        return (
            predicted_lines,
            image,
            lines_cropped_ordered,
            lines_cropped_ordered,  #
            lines_cropped_ordered,  # temp_gallery
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=True),
        )

    def transcribe_text(self, images):
        gr.Info("Running Transcribe Lines")
        transcription_temp_list_with_score = []
        mapping_dict = {}

        total_images = len(images)
        current_index = 0

        bool_to_show_placeholder = gr.update(visible=True)
        bool_to_show_control_results_transcribe = gr.update(visible=False)

        for image in images:
            current_index += 1

            if current_index == total_images:
                bool_to_show_control_results_transcribe = gr.update(visible=True)
                bool_to_show_placeholder = gr.update(visible=False)

            transcribed_text, prediction_score_from_htr = self.inferencer.transcribe(image)
            transcription_temp_list_with_score.append((transcribed_text, prediction_score_from_htr))

            df_trans_explore = pd.DataFrame(
                transcription_temp_list_with_score, columns=["Transcribed text", "Pred score"]
            )

            joined_transcription_temp_list = "\n".join([tup[0] for tup in transcription_temp_list_with_score])

            mapping_dict[transcribed_text] = image

            yield joined_transcription_temp_list, df_trans_explore, mapping_dict, bool_to_show_control_results_transcribe, bool_to_show_placeholder

    def get_select_index_image(self, images_from_gallery, evt: gr.SelectData):
        return images_from_gallery[evt.index]["name"]

    def get_select_index_df(self, transcribed_text_df_finish, mapping_dict, evt: gr.SelectData):
        df_list = transcribed_text_df_finish["Transcribed text"].tolist()
        key_text = df_list[evt.index[0]]
        sorted_image = mapping_dict[key_text]
        new_first = [sorted_image]
        new_list = [img for txt, img in mapping_dict.items() if txt != key_text]
        new_first.extend(new_list)
        return new_first, key_text

    def download_df_to_txt(self, transcribed_df):
        text_in_list = transcribed_df["Transcribed text"].tolist()

        file_name = "./transcribed_text.txt"
        text_file = open(file_name, "w")

        for text in text_in_list:
            text_file.write(text + "\n")
        text_file.close()

        return file_name, gr.update(visible=True)

    # def transcribe_text_another_model(self, df, images):
    #     transcription_temp_list = []
    #     for image in images:
    #         transcribed_text = inferencer.transcribe_different_model(image)
    #         transcription_temp_list.append(transcribed_text)
    #         df_trans = pd.DataFrame(transcription_temp_list, columns=["Transcribed_text"])
    #         yield df_trans, df_trans, gr.update(visible=False)


if __name__ == "__main__":
    pass
