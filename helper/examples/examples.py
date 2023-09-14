import io

import datasets
from PIL import Image


class DemoImages:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DemoImages, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, url="Riksarkivet/test_images_demo", cache_dir="./helper/examples/.cache_images"):
        if not hasattr(self, "images_datasets"):
            self.images_datasets = datasets.load_dataset(url, cache_dir=cache_dir, split="train")
            self.example_df = self.images_datasets.to_pandas()
            self.examples_list = self.convert_bytes_to_images()

    def convert_bytes_to_images(self):
        examples_list = []
        # For each row in the dataframe
        for index, row in self.example_df.iterrows():
            image_bytes = row["image"]["bytes"]
            image = Image.open(io.BytesIO(image_bytes))

            # Set the path to save the image
            path_to_image = f"./helper/examples/images/image_{index}.jpg"

            # Save the image
            image.save(path_to_image)

            # Get the description
            description = row["text"]

            # Append to the examples list
            examples_list.append([description, path_to_image])

        return examples_list


if __name__ == "__main__":
    # test = DemoImages(cache_dir=".cache_images")

    # print(test.examples_list)

    images_datasets = datasets.load_dataset("Riksarkivet/test_images_demo", cache_dir="./helper/examples/.cache_images")
    print(images_datasets["train"]["image"][0])
