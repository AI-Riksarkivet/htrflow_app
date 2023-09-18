import gradio as gr


class GradioConfig:
    def __init__(self, tooltip_dict):
        self.tooltip_dict = tooltip_dict
        self.theme = gr.themes.Base(
            primary_hue="blue",
            secondary_hue="blue",
            neutral_hue="slate",
            font=[
                gr.themes.GoogleFont("Open Sans"),
                "ui-sans-serif",
                "system-ui",
                "sans-serif",
            ],
        )
        self.css = """
        footer {display: none !important;}
        #image_upload {min-height:450}
        #image_upload [data-testid="image"], #image_upload [data-testid="image"] > div{min-height: 450px}
        #gallery {height: 400px} 
        .fixed-height.svelte-g4rw9.svelte-g4rw9 {min-height: 400px;}

        #gallery_lines > div.preview.svelte-1b19cri > div.thumbnails.scroll-hide.svelte-1b19cri {display: none;}

                """

    def generate_tooltip_css(self):
        temp_css_list = [self.css]
        for button_id, tooltip_text in self.tooltip_dict.items():
            temp_css_list.append(self.template_tooltip_css(button_id, tooltip_text))

        return "\n".join(temp_css_list)

    def template_tooltip_css(self, button_id, tooltip_text):
        return f"""
        /* For tooltip */
        #{button_id} {{
            position: relative;
        }}

        #{button_id}::before {{
            visibility: hidden; 
            content: '';
            position: absolute;
            bottom: 100%; /* Position on top of the parent element */
            left: 50%;
            margin-left: 5px; /* Adjust for the desired space between the button and tooltip */
            transform: translateY(-50%);
            border-width: 7px;
            border-style: solid;
            border-color: rgba(51, 51, 51, 0) transparent transparent rgba(51, 51, 51, 0); 
            transition: opacity 0.4s ease-in-out, border-color 0.4s ease-in-out;
            opacity: 0;
            z-index: 999;
        }}

        #{button_id}::after {{
            visibility: hidden; 
            content: '{tooltip_text}';
            position: absolute;
            bottom: 100%; /* Position on top of the parent element */
            left: 42%;
            background-color: rgba(51, 51, 51, 0);
            color: white;
            padding: 5px;
            border-radius: 3px;
            z-index: 998;
            opacity: 0;
            transition: opacity 0.4s ease-in-out, background-color 0.4s ease-in-out;
            margin-bottom: 20px !important; /* Increased from 18px to 23px to move tooltip 5px upwards */
            margin-left: 0px; /* Adjust for the arrow width and the desired space between the arrow and tooltip */
            white-space: normal; /* Allows the text to wrap */
            width: 200px; /* Maximum line length before wrapping */
            box-sizing: border-box;
        }}

        #{button_id}.showTooltip::before {{
            visibility: visible;
            opacity: 1;
            border-color: rgba(51, 51, 51, 0.7) transparent transparent rgba(51, 51, 51, 0.7);
        }}

        #{button_id}.showTooltip::after {{
            visibility: visible;
            opacity: 1;
            background-color: rgba(51, 51, 51, 0.7);
        }}
        """

    def add_interaction_to_buttons(self):
        button_ids_list = ", ".join([f"'#{id}'" for id, _ in self.tooltip_dict.items()])
        button_ids = button_ids_list.replace("'", "")
        return f"""
        function monitorButtonHover() {{

            const buttons = document.querySelectorAll('{button_ids}');
            buttons.forEach(function(button) {{
                button.addEventListener('mouseenter', function() {{
                    this.classList.add('showTooltip');
                }});

                button.addEventListener('mouseleave', function() {{
                    this.classList.remove('showTooltip');
                }});
            }})
        }}
        """

        #     gradioURL = window.location.href
        # if (!gradioURL.endsWith('?__theme=dark')) {{
        #     window.location.replace(gradioURL + '?__theme=dark');
        # }}


buttons_with_tooltip = {
    "run_pipeline_button": "Runs HTR on the image. Takes approx 1-2 mins per image (depending on hardware).",
    "clear_button": "Clears all states and resets the entire workflow in the stepwise tool.",
    "region_segment_button": "Segments text regions in the chosen image with the chosen settings.",
    "line_segment_button": "Segments chosen regions from the image gallery into lines segments.",
    "transcribe_button": "Transcribes each line segment into text and streams back the data.",
}
gradio_config = GradioConfig(buttons_with_tooltip)

theme = gradio_config.theme
css = gradio_config.generate_tooltip_css()
js = gradio_config.add_interaction_to_buttons()


if __name__ == "__main__":
    tooltip = GradioConfig({"run_pipeline_button": "this is a tooltop", "clear_button": "this is a tooltop"})
    css = tooltip.generate_tooltip_css()
    js = tooltip.add_interaction_to_buttons()

    print(css)
    print(js)
