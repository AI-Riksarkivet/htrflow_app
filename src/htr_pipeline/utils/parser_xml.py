import xml.etree.ElementTree as ET


class XmlParser:
    def __init__(self, page_xml="./page_xml.xml"):
        self.tree = ET.parse(page_xml, parser=ET.XMLParser(encoding="utf-8"))
        self.root = self.tree.getroot()
        self.namespace = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}"

    def xml_to_txt(self, output_file="page_txt.txt"):
        with open(output_file, "w", encoding="utf-8") as f:
            for textregion in self.root.findall(f".//{self.namespace}TextRegion"):
                for textline in textregion.findall(f".//{self.namespace}TextLine"):
                    text = textline.find(f"{self.namespace}TextEquiv").find(f"{self.namespace}Unicode").text
                    f.write(text + "\n")
                f.write("\n")


if __name__ == "__main__":
    pass
