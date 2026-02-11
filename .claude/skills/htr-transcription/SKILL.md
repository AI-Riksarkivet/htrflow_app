---
name: htr-transcription
description: >
  Guide for using HTRflow MCP tools to transcribe handwritten documents.
  Use when: transcribe handwriting, HTR, handwritten document,
  OCR historical document, read old handwriting, digitize manuscript,
  transcribe old letters, recognize handwritten text.
---

# HTR Transcription

Transcribe handwritten historical documents using the HTRflow MCP server.
Returns an interactive viewer, per-line transcription JSON, and archival exports.

## Tools

- `htr_transcribe` — Transcribe images and return result URLs

## Workflow

### 1. Determine image source

- **http/https URLs** (IIIF links, public image URLs): Use directly — skip to step 3.
- **Local files or attachments**: Must be uploaded to the Gradio server first — proceed to step 2.

### 2. Upload files to the Gradio server

`htr_transcribe` runs on a remote server. It can only access URLs it can
reach. Local file paths and user attachments are not accessible to the
server — you must upload them first.

The base URL is the MCP server host (e.g. `https://riksarkivet-htr-demo.hf.space`).

For each file:

1. POST the file:
   ```bash
   curl -s -X POST "{base_url}/gradio_api/upload" \
     -F "files=@filename.jpg"
   ```

2. Extract server path from JSON response:
   ```json
   ["/tmp/gradio/abc123def/filename.jpg"]
   ```

3. Construct the image URL:
   ```
   {base_url}/gradio_api/file=/tmp/gradio/abc123def/filename.jpg
   ```

Upload ALL files and collect ALL image URLs before proceeding to step 3.

### 3. Transcribe

Call `htr_transcribe` once with ALL image URLs in a single call.

**Batching rule**: Never call `htr_transcribe` multiple times for separate
images. Each call runs an expensive GPU pipeline — batch everything.

### 4. Present results

Return the URLs as clickable links:

> Here are your transcription results:
> - **Viewer**: [viewer_url] (interactive gallery with text overlays)
> - **Transcription data**: [pages_url]
> - **Export (ALTO XML)**: [export_url]

Present all returned URLs as **artifacts and downloadable links**:
- `viewer_url` — embed the interactive gallery viewer as an artifact
- `pages_url` — share as downloadable link (transcription JSON)
- `export_url` — share as downloadable link (archival export)

Do NOT reproduce document text as plain text in your response — present
the artifacts and links instead.

## Options

### Language

| Value       | Use when                            |
|-------------|-------------------------------------|
| `swedish`   | Swedish handwriting (default)       |
| `norwegian` | Norwegian handwriting               |
| `english`   | English handwriting                 |
| `medieval`  | Medieval scripts                    |

### Layout

| Value        | Use when                                         |
|--------------|--------------------------------------------------|
| `single_page`| Single pages, snippets, cropped regions (default)|
| `spread`     | Two-page book openings (Swedish only)            |

### Export format

| Value      | Description                             |
|------------|-----------------------------------------|
| `alto_xml` | ALTO XML — standard archival (default)  |
| `page_xml` | PAGE XML — alternative archival format  |
| `json`     | JSON — structured data format           |

### Custom pipeline

`custom_yaml` accepts a raw HTRflow YAML config string. Overrides
`language` and `layout`. Use only when user explicitly provides one.

Example — English modern handwriting with a custom TrOCR model:

```yaml
steps:
- step: Segmentation
  settings:
    model: yolo
    model_settings:
      model: Riksarkivet/yolov9-lines-within-regions-1
- step: TextRecognition
  settings:
    model: TrOCR
    model_settings:
      model: microsoft/trocr-base-handwritten
    generation_settings:
       batch_size: 16
- step: OrderLines
```
