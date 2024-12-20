import io

import datasets
from PIL import Image


class DemoImages:
    def __init__(self, url="Riksarkivet/test_images_demo", cache_dir=".app/assets/images/.cache_images"):
        if not hasattr(self, "images_datasets"):
            self.images_datasets = datasets.load_dataset(url, cache_dir=cache_dir, split="train")
            self.example_df = self.images_datasets.to_pandas()
            self.examples_list = self.convert_bytes_to_images()

    def convert_bytes_to_images(self):
        examples_list = []
        for index, row in self.example_df.iterrows():
            image_bytes = row["image"]["bytes"]
            image = Image.open(io.BytesIO(image_bytes))

            path_to_image = f"./app/assets/images/image_{index}.jpg"
            image.save(path_to_image)

            description = row["text"]

            examples_list.append([description, "Nested segmentation", path_to_image])

        return examples_list
