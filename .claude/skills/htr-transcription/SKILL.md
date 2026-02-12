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

After transcription, present results as an **inline artifact** for the viewer
and **downloadable links** for data exports.

#### 4a. Inline viewer artifact

Download the viewer HTML, then inline all external dependencies (OpenSeadragon
JS and images) so the artifact is fully self-contained (the artifact sandbox
blocks external requests).

```bash
curl -sL "{viewer_url}" -o /home/claude/viewer.html
```

Then run this Python script to embed dependencies:

```python
import re, base64, urllib.request

with open("/home/claude/viewer.html", "r") as f:
    html = f.read()

# Inline OpenSeadragon JS (CDN script -> inline script)
osd_match = re.search(r'<script src="(https://cdn[^"]+openseadragon[^"]+)">\s*</script>', html)
if osd_match:
    with urllib.request.urlopen(osd_match.group(1)) as resp:
        osd_js = resp.read().decode()
    html = html.replace(osd_match.group(0), f"<script>{osd_js}</script>")

# Embed all Gradio image URLs as base64 data URIs
for url in set(re.findall(
    r'https://riksarkivet-htr-demo\.hf\.space/gradio_api/file=[^\s"]+\.(?:jpg|png)', html
)):
    with urllib.request.urlopen(url) as resp:
        img_data = resp.read()
    ext = "jpeg" if url.endswith(".jpg") else "png"
    data_uri = f"data:image/{ext};base64,{base64.b64encode(img_data).decode()}"
    html = html.replace(url, data_uri)

with open("/mnt/user-data/outputs/viewer.html", "w") as f:
    f.write(html)
```

Then call `present_files` with `/mnt/user-data/outputs/viewer.html` to render
the interactive viewer as an inline artifact.

#### 4b. Export links

Provide the remaining URLs as clickable download links:

> - **Transcription data**: [pages_url] (per-line JSON)
> - **Export**: [export_url] (archival export)

Do NOT reproduce document text as plain text in your response — present
the artifact and links instead.

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