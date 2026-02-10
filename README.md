---
title: HTRflow App
emoji: 🏢
colorFrom: purple
colorTo: green
sdk: gradio
app_file: app/main.py
pinned: true
license: apache-2.0
short_description: HTR (Handwritten Text Recognition) demo application
header: mini
thumbnail: >-
  https://cdn-uploads.huggingface.co/production/uploads/60a4e677917119d38f6bbff8/-qMf3PaegicobqW5hXyiA.png
sdk_version: 6.5.1
---

# HTRflow App

[HTRflow App](https://huggingface.co/spaces/Riksarkivet/htr_demo) is an interactive demo application by [Riksarkivet](https://riksarkivet.se) (the Swedish National Archives) that transcribes historical handwritten documents into digital text using AI. It uses [HTRflow](https://ai-riksarkivet.github.io/htrflow/latest/index.html) as its backend.

This is a demo application, not intended for production use, but it highlights the potential of HTR technology for cultural heritage institutions worldwide.

<p align="center">
  <img src="https://ai-riksarkivet.github.io/htrflow/latest/assets/background_htrflow_2.png" alt="HTRflow App Demo" width="80%">
</p>

---

## Guide

The app has two tabs: **Transcribe** and **Results**.

1. **Transcribe Tab:**
   - Upload one or multiple images, PDFs, or fetch images from a [Riksarkivet IIIF server](https://github.com/Riksarkivet/dataplattform/wiki/IIIF) URL.
   - Select a pipeline that matches your material (Swedish, Norwegian, English, or Medieval). For spreads (two-page openings), choose the spread variant.
   - Optionally edit the pipeline YAML configuration directly.
   - Click **Submit** to start the HTR job. The HTRflow backend segments the document, recognizes text lines, and produces a structured document model.

2. **Results Tab:**
   - View the transcription results with synchronized image and text panels.
   - Export the document in multiple formats: TXT, ALTO XML, PAGE XML, or JSON.

### Available Pipelines

| Pipeline | Language | Layout | Model |
|---|---|---|---|
| Swedish - Single page and snippets | Swedish | Single page | Riksarkivet/swelion_libre |
| Swedish - Spreads | Swedish | Two-page spread | Riksarkivet/swelion_libre |
| Norwegian - Single page and snippets | Norwegian | Single page | Språkbanken/TrOCR-norhand-v3 |
| English - Single page and snippets | English | Single page | Microsoft TrOCR |
| Medieval - Single page and snippets | Medieval | Single page | Medieval Data models |

---

## MCP Server

The app exposes an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server, allowing AI agents like Claude to transcribe documents programmatically.

### Tools

- **htr_upload_image** - Upload a local image file to the server and get a URL for transcription.
- **htr_transcribe** - Transcribe handwritten documents and return all results in one call:
  - `image_urls`: List of image URLs (supports batch processing)
  - `export_format`: `"alto_xml"` | `"page_xml"` | `"json"`
  - `language`: `"swedish"` | `"norwegian"` | `"english"` | `"medieval"`
  - `layout`: `"single_page"` | `"spread"`

Returns per-line transcription with confidence scores, an interactive gallery viewer URL, and an archival export file URL.

---

## Development

### Prerequisites

- Python 3.10+
- (Optional) Nvidia GPU for faster inference

### Installation

```bash
git clone https://github.com/Riksarkivet/htrflow_app.git
cd htrflow_app
```

Install [uv](https://docs.astral.sh/uv/) and set up the environment:

```bash
pip install uv
uv venv --python 3.10
source .venv/bin/activate
uv sync
```

### Running Locally

For development with hot reload:

```bash
gradio app/main.py
```

For a standard run:

```bash
uv run app/main.py
```

Open `http://localhost:7860` in your browser.

---

## Docker

### Build and Run

```bash
docker build --tag htrflow/htrflow-app .
docker run -it -d --name htrflow-app -p 7000:7860 htrflow/htrflow-app:latest
```

Visit `http://localhost:7000`.

### With GPU

```bash
docker run -it -d --name htrflow-app -p 7000:7860 --gpus all htrflow/htrflow-app:latest
```

---

## License

Apache 2.0. See the [LICENSE](./LICENSE) file for details.
