import re
from datetime import datetime

import jinja2


class XMLHelper:
    def __init__(self, xml_file_name="page_xml.xml"):
        self.xml_file_name = xml_file_name
        self.searchpath = "./src/htr_pipeline/utils/templates"
        self.template = "page_xml_2013.xml"

    def render(self, template_data):
        rendered_xml = self._render_xml(template_data)
        return rendered_xml

    def _transform_coords(self, input_string):
        pattern = r"\[\s*([^\s,]+)\s*,\s*([^\s\]]+)\s*\]"
        replacement = r"\1,\2"
        return re.sub(pattern, replacement, input_string)

    def _render_xml(self, template_data):
        template_loader = jinja2.FileSystemLoader(searchpath=self.searchpath)
        template_env = jinja2.Environment(loader=template_loader, trim_blocks=True)
        template = template_env.get_template(self.template)
        rendered_xml = template.render(template_data)
        rendered_xml = self._transform_coords(rendered_xml)
        return rendered_xml

    def prepare_template_data(self, img_file_name, image):
        img_height = image.shape[0]
        img_width = image.shape[1]

        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
        return {
            "created": date_time,
            "imageFilename": img_file_name,
            "imageWidth": img_width,
            "imageHeight": img_height,
            "textRegions": list(),
        }

    def escape_xml_chars(self, textline):
        return (
            textline.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;")
        )


if __name__ == "__main__":
    pass
