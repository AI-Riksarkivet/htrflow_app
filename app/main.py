import shutil
import gradio as gr
import os
from app.gradio_config import css, theme
from app.tabs.submit import (
    submit,
    custom_template_yaml,
    collection_submit_state,
)
from app.tabs.visualizer import visualizer, collection as collection_viz_state

from app.tabs.templating import (
    templating_block,
    TEMPLATE_IMAGE_FOLDER,
    TEMPLATE_YAML_FOLDER,
    template_output_yaml_code,
)
from gradio_modal import Modal

from htrflow.models.huggingface.trocr import TrOCR

gr.set_static_paths(paths=[TEMPLATE_IMAGE_FOLDER])
gr.set_static_paths(paths=[TEMPLATE_YAML_FOLDER])

# TODO: fix api/ endpoints..
# TODO add colab
# TDOO addd eexmaple for api


def load_markdown(language, section, content_dir="app/content"):
    """Load markdown content from files."""
    if language is None:
        file_path = os.path.join(content_dir, f"{section}.md")
    else:
        file_path = os.path.join(content_dir, language, f"{section}.md")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"## Content missing for {file_path} in {language}"


matomo = """
<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['setDomains', ['*.riksarkivet.se', 'huggingface.co']]);
  _paq.push(['enableCrossDomainLinking']);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="https://matomo.riksarkivet.se/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '25']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
<noscript><p><img referrerpolicy="no-referrer-when-downgrade" src="https://matomo.riksarkivet.se/matomo.php?idsite=25&amp;rec=1" style="border:0;" alt="" /></p></noscript>
<!-- End Matomo Code -->
"""

with gr.Blocks(title="HTRflow", theme=theme, css=css, head=matomo) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            help_button = gr.Button("Help", scale=0)
            with Modal(visible=False) as help_modal:
                # TODO: tutorial material?
                with gr.Tab("How to use App"):
                    gr.Markdown(load_markdown(None, "how_it_works"))
                with gr.Tab("Contact"):
                    pass

        with gr.Column(scale=2):
            gr.Markdown(load_markdown(None, "main_title"))
        with gr.Column(scale=1):
            gr.Markdown(load_markdown(None, "main_sub_title"))

    with gr.Tabs(elem_classes="top-navbar") as navbar:
        with gr.Tab(label="Templating") as tab_templating:
            templating_block.render()

        with gr.Tab(label="Submit Job") as tab_submit:
            submit.render()

        with gr.Tab(label="Result") as tab_visualizer:
            visualizer.render()

    @demo.load()
    def inital_trocr_load():
        TrOCR("Riksarkivet/trocr-base-handwritten-hist-swe-2")

    @demo.load()
    def inital_yaml_code():
        tmp_dir = "tmp/"
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

    @demo.load(
        inputs=[template_output_yaml_code],
        outputs=[template_output_yaml_code],
    )
    def inital_yaml_code(template_output_yaml_code):
        return template_output_yaml_code

    def sync_gradio_objects(input_value, state_value):
        """Synchronize the YAML state if there is a mismatch."""
        return input_value if input_value != state_value else gr.skip()

    def sync_gradio_object_state(input_value, state_value):
        """Synchronize the Collection."""
        state_value = input_value
        return state_value if state_value is not None else gr.skip()

    tab_templating.select(
        inputs=[custom_template_yaml, template_output_yaml_code],
        outputs=[template_output_yaml_code],
        fn=sync_gradio_objects,
    )

    tab_submit.select(
        inputs=[template_output_yaml_code, custom_template_yaml],
        outputs=[custom_template_yaml],
        fn=sync_gradio_objects,
    )

    tab_visualizer.select(
        inputs=[collection_submit_state, collection_viz_state],
        outputs=[collection_viz_state],
        fn=sync_gradio_object_state,
    )

    help_button.click(lambda: Modal(visible=True), None, help_modal)

demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        enable_monitoring=True,
        # show_error=True,
    )
