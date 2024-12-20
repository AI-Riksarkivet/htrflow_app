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

# .top-navbar .tab-container {justify-content: center;}
# .top-navbar .tab-container button {font-size:large !important;}
#langdropdown {width: 100px;}

#column-form .wrap {flex-direction: column; height:100vh;}

@media screen and (max-width: 1024px) {
    #column-form .wrap {
        flex-direction: column; 
        height: auto;
    }
}

#htrflowouttab-button {opacity: 0; cursor:auto;}

"""
