import os
import tarfile

import datasets
import pandas as pd

_CITATION = """\
@InProceedings{huggingface:dataset,
title = {Small htr examples images},
author={Gabriel Borg},
year={2023}
}
"""

_DESCRIPTION = """\
Demo dataset for the htr demo.
"""
_HOMEPAGE = "https://huggingface.co/datasets/Riksarkivet/test_images_demo"

_LICENSE = ""

_REPO = "https://huggingface.co/datasets/Riksarkivet/test_images_demo"


class ExampleImages(datasets.GeneratorBasedBuilder):
    """Small sample of image-text pairs"""

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "image": datasets.Image(),
                }
            ),
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        images_archive = dl_manager.download(f"{_REPO}/resolve/main/images.tar.gz")
        metadata_path = dl_manager.download(f"{_REPO}/resolve/main/images.txt")
        image_iters = dl_manager.iter_archive(images_archive)
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN, gen_kwargs={"images": image_iters, "metadata_path": metadata_path}
            ),
        ]

    def _generate_examples(self, images, metadata_path):
        """Generate images and text."""
        with open(metadata_path, encoding="utf-8") as f:
            metadata_list = f.read().split("\n")
        for idx, (img_obj, meta_txt) in enumerate(zip(images, metadata_list)):
            filepath, image = img_obj

            text_value = meta_txt.split("= ")[-1].strip()

            yield idx, {
                "image": {"path": filepath, "bytes": image.read()},
                "text": text_value,
            }


def txt_to_csv(file_name):
    text_file_path = f"{file_name}.txt"
    df = pd.read_csv(text_file_path, delimiter="=", header=None, names=["Key", "Label"], encoding="utf-8")
    df["Key"] = df["Key"].str.strip()
    df["Label"] = df["Label"].str.strip()
    print(df)
    df.to_csv(f"{file_name}.csv", index=False)


def sort_and_compress_images(images_folder, tar_file):
    sorted_images = sorted(os.listdir(images_folder))
    with tarfile.open(tar_file, "w:gz") as tar:
        for image_name in sorted_images:
            image_path = os.path.join(images_folder, image_name)
            tar.add(image_path, arcname=image_name)
    print("Images sorted and compressed into tar.gz archive.")


if __name__ == "__main__":
    txt_to_csv("info")
    sort_and_compress_images("images", "sorted_images.tar.gz")
