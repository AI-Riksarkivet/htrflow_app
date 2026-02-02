import gradio as gr

theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="blue",
    neutral_hue="slate",
    font=[
        gr.themes.GoogleFont("Open Sans"),
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
    ],
    # text_size="md",
)

css = """
/* SVG visualizations */
.svg-image {
  height: auto;
  width: 100%;
  margin: auto;
}

/* Transcription display */
.transcription {
  font-size: large;
  position: sticky;
  top: 20px;
}

/* Textline polygon styling */
.textline {
  fill: transparent;
  stroke: blue;
  stroke-width: 10;
  stroke-opacity: 0.2;
}

.highlighted polygon {
  fill: blue;
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

/* Button grouping for visualizer */
.button-group-viz {
  margin: auto;
  display: flex;
  justify-content: center;
  gap: 1rem;
  text-align: center;
}

.button-group-viz button {
  max-width: 150px;
}

/* Pipeline information styling */
.pipeline-help {
  padding: 5px 0 0 0;
  font-weight: var(--block-info-text-weight);
  font-size: var(--block-info-text-size);
  color: var(--block-info-text-color);
}

.pipeline-help a {
  color: var(--secondary-400);
}

.pipeline-help a:hover {
  color: var(--secondary-500);
}

.pipeline-info {
  padding: 0;
  margin: 0;
  font-weight: var(--block-info-text-weight);
  color: var(--block-info-text-color);
}

/* Title styling */
.title-h1 {
  text-align: center;
  display: block;
}
"""
