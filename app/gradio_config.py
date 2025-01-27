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
.svg-image {
  height: auto;
  width: 100%;
  margin: auto;
}

.transcription {
  font-size: large;
}

/* style of textline svg elements */
.textline {
  fill: transparent;
  stroke: blue;
  stroke-width: 10;
  stroke-opacity: 0.2;
}

.highlighted polygon {
  fill:blue;
  fill-opacity: 0.2;
}

span.highlighted {
  background-color: rgba(0%, 0%, 100%, 0.2);
  font-size: large;
}

hr.region-divider {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

"""
