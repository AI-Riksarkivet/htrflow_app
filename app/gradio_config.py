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
  position: sticky;
  top: 20px;
}

.transcription-column {
  height: 100vh;
}

/* this is needed in order to make the transcription sticky */
.app {
  overflow: visible;
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

.pipeline-panel {
  background: none;
  border: solid 1px;
  border-color: var(--block-border-color);
}

.pipeline-help {
  padding: 5px 0 0 0;
  font-weight: var(--block-info-text-weight);
  font-size: var(--block-info-text-size);
  color: var(--block-info-text-color);
}

.pipeline-info {
  padding: 0 0 0 2px;
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

.pipeline-header {
  padding: 2px 0px 0px 2px;
  color: var(--body-text-color);
}

.pipeline-description {
  margin: auto;
  color: var(--body-text-color);
}

.button-group-viz {
 margin: auto;
 display: flex;
 justify-content: center;
 gap: 1rem;
 text-align: center;
}
"""
