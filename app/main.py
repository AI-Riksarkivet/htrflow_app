import logging
import os

import gradio as gr
from gradio_i18n import Translate, gettext as _

from app.gradio_config import css, theme
from app.tabs.submit import collection_submit_state, submit, pipeline_description, pipeline_dropdown, get_pipeline_description
from app.tabs.visualizer import collection as collection_viz_state
from app.tabs.visualizer import visualizer

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


MATOMO_URL = os.environ.get("MATOMO_URL", "https://matomo.riksarkivet.se/")
MATOMO_SITE_ID = os.environ.get("MATOMO_SITE_ID", "25")
MATOMO_DOMAINS = os.environ.get("MATOMO_DOMAINS", "*.riksarkivet.se,huggingface.co")

if os.environ.get("DEV_MODE") == "true":
    matomo = ""
else:
    matomo = f"""
<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  _paq.push(['setDomains', [{", ".join(f"'{d.strip()}'" for d in MATOMO_DOMAINS.split(","))}]]);
  _paq.push(['enableCrossDomainLinking']);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {{
    var u="{MATOMO_URL}";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '{MATOMO_SITE_ID}']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  }})();
</script>
<noscript><p><img referrerpolicy="no-referrer-when-downgrade" src="{MATOMO_URL}matomo.php?idsite={MATOMO_SITE_ID}&amp;rec=1" style="border:0;" alt="" /></p></noscript>
<!-- End Matomo Code -->
"""

with gr.Blocks(
    title="HTR-demo",
) as demo:
    with Translate("app/translations.yaml", placeholder_langs=["en", "sv"]) as lang:
        with gr.Row():
            with gr.Column(scale=20):
                gr.Markdown(load_markdown(None, "main_title"), elem_classes="title-h1")
            with gr.Column(scale=1, min_width=80):
                lang_selector = gr.Dropdown(
                    choices=[("EN", "en"), ("SV", "sv")],
                    value="en",
                    container=False,
                    show_label=False,
                )

        lang_selector.change(fn=lambda x: x, inputs=[lang_selector], outputs=[lang])

        with gr.Sidebar(label="Menu"):
            gr.HTML(load_markdown(None, "main_sub_title_hum"))
            sidebar_content = gr.Markdown(load_markdown("en", "sidebar"))

        def update_sidebar(language):
            return load_markdown(language, "sidebar")

        lang_selector.change(fn=update_sidebar, inputs=[lang_selector], outputs=[sidebar_content])

        # Update pipeline description when language changes
        lang_selector.change(
            fn=get_pipeline_description,
            inputs=[pipeline_dropdown, lang_selector],
            outputs=[pipeline_description]
        )

        with gr.Tabs(elem_classes="top-navbar") as navbar:
            with gr.Tab(label=_("Transcribe")) as tab_submit:
                submit.render()
            with gr.Tab(label=_("Results"), id="result") as tab_visualizer:
                visualizer.render()

    def sync_gradio_object_state(input_value, state_value):
        """Synchronize the Collection."""
        state_value = input_value
        return state_value if state_value is not None else gr.skip()

    # Auto-navigate to Results tab after HTR processing
    collection_submit_state.change(
        lambda collection: gr.Tabs(selected="result") if collection else gr.skip(),
        inputs=collection_submit_state,
        outputs=navbar
    )

    # Sync collection from Upload to Results tab
    tab_visualizer.select(
        inputs=[collection_submit_state, collection_viz_state],
        outputs=[collection_viz_state],
        fn=sync_gradio_object_state,
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        enable_monitoring=False,
        theme=theme,
        css=css,
        head=matomo,
        footer_links=["api", "settings"],
        root_path=os.environ.get("GRADIO_ROOT_PATH", ""),
        mcp_server=True
    )
