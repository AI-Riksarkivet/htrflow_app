import logging
import os

import gradio as gr
from htrflow.models.huggingface.trocr import TrOCR

from app.gradio_config import css, theme
from app.tabs.export import collection as collection_export_state
from app.tabs.export import export
from app.tabs.submit import collection_submit_state, submit
from app.tabs.visualizer import collection as collection_viz_state
from app.tabs.visualizer import visualizer

# Suppress transformers logging
logging.getLogger("transformers").setLevel(logging.ERROR)


TEMPLATE_YAML_FOLDER = "app/assets/templates"
gr.set_static_paths(paths=[TEMPLATE_YAML_FOLDER])


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


def activate_tab(collection):
    return gr.update(interactive=collection is not None)


# Please remove this line when running locally
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

with gr.Blocks(
    title="HTRflow",
    theme=theme,
    css=css,
    head=matomo,
) as demo:

    gr.Markdown(load_markdown(None, "main_title"))

    with gr.Sidebar(label="Menu"):
        gr.Markdown(load_markdown(None, "main_sub_title_hum"))
        gr.Markdown(load_markdown(None, "sidebar"))

    with gr.Tabs(elem_classes="top-navbar") as navbar:
        with gr.Tab(label="1. Upload") as tab_submit:
            submit.render()
        with gr.Tab(
            label="2. Result", interactive=False, id="result"
        ) as tab_visualizer:
            visualizer.render()

        with gr.Tab(label="3. Export", interactive=False) as tab_export:
            export.render()

    @demo.load()
    def inital_trocr_load():
        TrOCR("Riksarkivet/trocr-base-handwritten-hist-swe-2")

    def sync_gradio_object_state(input_value, state_value):
        """Synchronize the Collection."""
        state_value = input_value
        return state_value if state_value is not None else gr.skip()

    collection_submit_state.change(
        activate_tab, collection_submit_state, tab_visualizer
    )
    collection_submit_state.change(activate_tab, collection_submit_state, tab_export)
    collection_submit_state.change(lambda: gr.Tabs(selected="result"), outputs=navbar)

    tab_visualizer.select(
        inputs=[collection_submit_state, collection_viz_state],
        outputs=[collection_viz_state],
        fn=sync_gradio_object_state,
    )

    tab_export.select(
        inputs=[collection_submit_state, collection_export_state],
        outputs=[collection_export_state],
        fn=sync_gradio_object_state,
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", server_port=7860, enable_monitoring=False, show_api=False
    )
