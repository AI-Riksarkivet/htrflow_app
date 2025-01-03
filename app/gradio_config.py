import gradio as gr

theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="blue",
    neutral_hue="slate",
    # font=[
    #     gr.themes.GoogleFont("Open Sans"),
    #     "ui-sans-serif",
    #     "system-ui",
    #     "sans-serif",
    # ],
)

css = """
body > gradio-app > div > div > div.wrap.svelte-1rjryqp > footer > a {
    display: none !important;
}
body > gradio-app > div > div > div.wrap.svelte-1rjryqp > footer > div {
    display: none !important;
}
#langdropdown {width: 100px;}

"""
