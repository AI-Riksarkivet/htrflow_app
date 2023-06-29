import math
import os
import random
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


class XmlParser:
    def __init__(self, page_xml="./page_xml.xml"):
        self.tree = ET.parse(page_xml, parser=ET.XMLParser(encoding="utf-8"))
        self.root = self.tree.getroot()
        self.namespace = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}"

    def visualize_xml(
        self,
        background_image,
        font_size=9,
        text_offset=10,
        font_path_tff="./src/htr_pipeline/utils/templates/arial.ttf",
    ):
        image = Image.fromarray(background_image).convert("RGBA")
        image_width = int(self.root.find(f"{self.namespace}Page").attrib["imageWidth"])
        image_height = int(self.root.find(f"{self.namespace}Page").attrib["imageHeight"])

        text_offset = -text_offset
        base_font_size = font_size
        font_path = font_path_tff

        max_bbox_width = 0  # Initialize maximum bounding box width

        for textregion in self.root.findall(f".//{self.namespace}TextRegion"):
            coords = textregion.find(f"{self.namespace}Coords").attrib["points"].split()
            points = [tuple(map(int, point.split(","))) for point in coords]
            x_coords, y_coords = zip(*points)
            min_x, max_x = min(x_coords), max(x_coords)
            bbox_width = max_x - min_x  # Width of the current bounding box
            max_bbox_width = max(max_bbox_width, bbox_width)  # Update maximum bounding box width

        scaling_factor = max_bbox_width / 400.0  # Use maximum bounding box width for scaling
        font_size_scaled = int(base_font_size * scaling_factor)
        font = ImageFont.truetype(font_path, font_size_scaled)

        for textregion in self.root.findall(f".//{self.namespace}TextRegion"):
            fill_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 100)
            for textline in textregion.findall(f".//{self.namespace}TextLine"):
                coords = textline.find(f"{self.namespace}Coords").attrib["points"].split()
                points = [tuple(map(int, point.split(","))) for point in coords]

                poly_image = Image.new("RGBA", image.size)
                poly_draw = ImageDraw.Draw(poly_image)
                poly_draw.polygon(points, fill=fill_color)

                text = textline.find(f"{self.namespace}TextEquiv").find(f"{self.namespace}Unicode").text

                x_coords, y_coords = zip(*points)
                min_x, max_x = min(x_coords), max(x_coords)
                min_y = min(y_coords)
                text_width, text_height = poly_draw.textsize(text, font=font)  # Get text size
                text_position = (
                    (min_x + max_x) // 2 - text_width // 2,
                    min_y + text_offset,
                )  # Center text horizontally

                poly_draw.text(text_position, text, fill=(0, 0, 0), font=font)
                image = Image.alpha_composite(image, poly_image)

        return image

    def xml_to_txt(self, output_file="page_txt.txt"):
        with open(output_file, "w", encoding="utf-8") as f:
            for textregion in self.root.findall(f".//{self.namespace}TextRegion"):
                for textline in textregion.findall(f".//{self.namespace}TextLine"):
                    text = textline.find(f"{self.namespace}TextEquiv").find(f"{self.namespace}Unicode").text
                    f.write(text + "\n")
                f.write("\n")
