import gradio as gr


def get_tab_updates(selected_language, TAB_LABELS):
    """Helper to generate tab updates for the selected language."""
    labels = TAB_LABELS[selected_language]
    return [gr.update(label=label) for label in labels]
