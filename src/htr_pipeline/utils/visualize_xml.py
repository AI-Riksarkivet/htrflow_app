import random
import xml.etree.ElementTree as ET

import cv2
import numpy as np


class XmlViz:
    def __init__(self, page_xml="./page_xml.xml"):
        self.tree = ET.parse(page_xml, parser=ET.XMLParser(encoding="utf-8"))
        self.root = self.tree.getroot()
        self.namespace = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}"

    def visualize_xml(self, background_image):
        overlay = background_image.copy()
        text_polygon_dict = {}

        for textregion in self.root.findall(f".//{self.namespace}TextRegion"):
            fill_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for textline in textregion.findall(f".//{self.namespace}TextLine"):
                coords = textline.find(f"{self.namespace}Coords").attrib["points"].split()
                points = [tuple(map(int, point.split(","))) for point in coords]
                cv2.fillPoly(overlay, [np.array(points)], fill_color)

                text = textline.find(f"{self.namespace}TextEquiv").find(f"{self.namespace}Unicode").text
                text_polygon_dict[text] = points

        # Blend the overlay with the original image
        cv2.addWeighted(overlay, 0.5, background_image, 0.5, 0, background_image)

        return background_image, text_polygon_dict


if __name__ == "__main__":
    pass
