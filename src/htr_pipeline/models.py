import os

import torch
from huggingface_hub import snapshot_download
from mmdet.apis import DetInferencer

# from mmengine import Config
from mmocr.apis import TextRecInferencer


class HtrModels:
    def __init__(self, local_run=False):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        model_folder = "./models"
        self.region_config = f"{model_folder}/RmtDet_regions/rtmdet_m_textregions_2_concat.py"
        self.region_checkpoint = f"{model_folder}/RmtDet_regions/epoch_12.pth"

        self.line_config = f"{model_folder}/RmtDet_lines/rtmdet_m_textlines_2_concat.py"
        self.line_checkpoint = f"{model_folder}/RmtDet_lines/epoch_12.pth"

        self.mmocr_config = f"{model_folder}/SATRN/_base_satrn_shallow_concat.py"
        self.mmocr_checkpoint = f"{model_folder}/SATRN/epoch_5.pth"

        # Check if model files exist at the specified paths, if not, get the config
        if not (
            os.path.exists(self.region_checkpoint)
            and os.path.exists(self.line_checkpoint)
            and os.path.exists(self.mmocr_checkpoint)
        ):
            config_path = self.get_config()
            self.region_checkpoint = config_path["region_checkpoint"]
            self.line_checkpoint = config_path["line_checkpoint"]
            self.mmocr_checkpoint = config_path["mmocr_checkpoint"]

    def load_region_model(self):
        # build the model from a config file and a checkpoint file
        return DetInferencer(self.region_config, self.region_checkpoint, device=self.device)

    def load_line_model(self):
        return DetInferencer(self.line_config, self.line_checkpoint, device=self.device)

    def load_htr_model(self):
        inferencer = TextRecInferencer(self.mmocr_config, self.mmocr_checkpoint, device=self.device)
        return inferencer

    @staticmethod
    def get_config():
        path_models = snapshot_download(
            "Riksarkivet/HTR_pipeline_models",
            allow_patterns=["*.pth"],
            token="__INSERT__FINS_HUGGINFACE_TOKEN__",
            cache_dir="./",
        )
        config_path = {
            "region_checkpoint": os.path.join(path_models, "RmtDet_regions/epoch_12.pth"),
            "line_checkpoint": os.path.join(path_models, "RmtDet_lines/epoch_12.pth"),
            "mmocr_checkpoint": os.path.join(path_models, "SATRN/epoch_5.pth"),
        }

        return config_path


if __name__ == "__main__":
    pass
