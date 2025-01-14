from jinja2 import Environment, FileSystemLoader


def get_yaml_button_fn(
    method,
    output_formats,
    reading_order,
    simple_segment_model=None,
    simple_htr_model=None,
    simple_htr_model_type=None,
    simple_segment_model_type=None,
    nested_segment_model_1=None,
    nested_segment_model_2=None,
    nested_htr_model=None,
    nested_segment_model_1_type=None,
    nested_segment_model_2_type=None,
    nested_htr_model_type=None,
):
    env = Environment(loader=FileSystemLoader("app/templates"))

    if output_formats is None:
        output_formats = ["txt"]

    template_name = "steps_template.yaml.j2"
    try:
        if method == "Simple layout":
            steps = [
                {
                    "step": "Segmentation",
                    "model": simple_segment_model_type,
                    "model_settings": {"model": simple_segment_model},
                },
                {
                    "step": "TextRecognition",
                    "model": simple_htr_model_type,
                    "model_settings": {"model": simple_htr_model},
                },
            ]
        elif method == "Nested segmentation":
            steps = [
                {
                    "step": "Segmentation",
                    "model": nested_segment_model_1_type,
                    "model_settings": {"model": nested_segment_model_1},
                },
                {
                    "step": "Segmentation",
                    "model": nested_segment_model_2_type,
                    "model_settings": {"model": nested_segment_model_2},
                },
                {
                    "step": "TextRecognition",
                    "model": nested_htr_model_type,
                    "model_settings": {"model": nested_htr_model},
                },
            ]
        else:
            return "Invalid method or not yet supported."

        steps.append({"step": reading_order})

        # TODO: fix reading order
        # - step: ReadingOrderMarginalia
        # settings:
        #     two_page: always

        # TODO: fix labeling format
        # # Sets label format to regionX_lineY_wordZ
        # labels:
        # level_labels:
        #     - region
        #     - line
        #     - word
        # sep: _
        # template: "{label}{number}"

        steps.extend(
            {
                "step": "Export",
                "settings": {"format": format, "dest": f"{format}-outputs"},
            }
            for format in output_formats
        )

        template = env.get_template(template_name)

        yaml_value = template.render(steps=steps)
        return yaml_value

    except Exception as e:
        return f"Error generating YAML: {str(e)}"
