"""
MCP API endpoint for HTRflow handwritten text recognition.

Provides outcome-oriented tools that transcribe handwritten documents
and return all results as file URLs in a single call — structured
transcription data, interactive gallery viewer, and archival export.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Optional, Union, Literal
import uuid

import gradio as gr
from htrflow.volume.volume import Collection

from app.tabs.submit import run_htrflow, get_yaml
from app.tabs.visualizer import rename_files_in_directory

# Create MCP export directory in the app directory (accessible by Gradio)
MCP_EXPORT_DIR = Path(__file__).parent / "mcp_exports"
MCP_EXPORT_DIR.mkdir(exist_ok=True)


def _get_base_url() -> str:
    """Get base URL from SPACE_HOST or GRADIO_ROOT_PATH."""
    space_host = os.getenv("SPACE_HOST")
    if space_host:
        host = space_host.split(",")[0].strip()
        return f"https://{host}"

    root_path = os.getenv("GRADIO_ROOT_PATH", "").strip("/")
    if root_path:
        return f"/{root_path}"

    return ""


PIPELINE_MAP = {
    ("swedish", "single_page"): "Swedish - Single page and snippets",
    ("swedish", "spread"): "Swedish - Spreads",
    ("norwegian", "single_page"): "Norwegian - Single page and snippets",
    ("norwegian", "spread"): "Norwegian - Single page and snippets",
    ("english", "single_page"): "English - Single page and snippets",
    ("english", "spread"): "English - Single page and snippets",
    ("medieval", "single_page"): "Medieval - Single page and snippets",
    ("medieval", "spread"): "Medieval - Single page and snippets",
}


def _resolve_pipeline(language: str, layout: str) -> str:
    """Resolve language + layout to internal pipeline name."""
    return PIPELINE_MAP.get((language, layout), "Swedish - Single page and snippets")


def _build_file_url(file_path: str) -> str:
    """Construct a Gradio file download URL."""
    base_url = _get_base_url()
    file_url = f"/gradio_api/file={file_path}"
    return f"{base_url}{file_url}" if base_url else file_url


def _get_htr_viewer_template() -> str:
    """Load the HTR viewer HTML template from file."""
    template_path = (
        Path(__file__).parent / "tabs" / "visualizer" / "generate_viewer_template.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def _prepare_images_for_htrflow(
    image_urls: Union[str, list[str]],
) -> list[tuple[str, str]]:
    """Convert image URLs to format expected by run_htrflow."""
    if isinstance(image_urls, str):
        image_urls = [image_urls]
    return [(url, url.split("/")[-1]) for url in image_urls]


def _get_yaml_config(pipeline: str, custom_yaml: Optional[str]) -> str:
    """Get YAML configuration for pipeline."""
    if custom_yaml:
        return custom_yaml
    return get_yaml(pipeline)


def _run_htr_pipeline(
    image_urls: Union[str, list[str]],
    pipeline: str,
    custom_yaml: Optional[str],
    progress: gr.Progress = None,
) -> Collection:
    """
    Core HTR pipeline execution — the expensive AI/GPU step.

    Args:
        image_urls: Image URL(s) to process
        pipeline: Pipeline name
        custom_yaml: Custom YAML config (overrides pipeline)
        progress: Progress tracker

    Returns:
        Processed Collection object
    """
    yaml_config = _get_yaml_config(pipeline, custom_yaml)
    batch_images = _prepare_images_for_htrflow(image_urls)

    if progress:
        progress(0, desc="Starting HTR transcription")

    # run_htrflow is a generator that yields (collection, gr.skip())
    result = next(
        run_htrflow(
            yaml_config, batch_images, progress=progress if progress else gr.Progress()
        )
    )
    return result[0]  # Extract collection from tuple


def _save_pages_json(collection: Collection, export_id: str) -> str:
    """Save per-page line data as JSON file and return its URL.

    Produces a lightweight JSON with id, text, and confidence per line,
    grouped by page. The agent can fetch this URL to read the transcription.
    """
    pages = []
    for i, page in enumerate(collection.pages):
        page_lines = list(page.traverse(lambda node: node.is_line()))
        lines = []
        for line in page_lines:
            if line.text:
                text_result = line.get("text_result")
                confidence = (
                    text_result.scores[0]
                    if (
                        text_result
                        and hasattr(text_result, "scores")
                        and text_result.scores
                    )
                    else 1.0
                )
                lines.append(
                    {
                        "id": line.label,
                        "text": line.text,
                        "confidence": round(float(confidence), 3),
                    }
                )
        pages.append({"page": i + 1, "lines": lines})

    json_path = MCP_EXPORT_DIR / f"pages_{export_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False)
    return _build_file_url(str(json_path))


def _build_viewer_pages_data(
    collection: Collection, image_urls: list[str]
) -> list[dict]:
    """Build the full per-page data needed by the gallery viewer template.

    Unlike _extract_pages_lines (lightweight for API), this includes bboxes,
    polygons, and image URLs needed for the interactive HTML viewer.
    """
    viewer_pages = []

    for i, page in enumerate(collection.pages):
        regions_raw = list(
            page.traverse(
                lambda node: node.children and all(child.is_line() for child in node)
            )
        )

        lines = []
        for region in regions_raw:
            for line in region:
                if line.is_line():
                    text_result = line.get("text_result")
                    confidence = (
                        text_result.scores[0]
                        if (
                            text_result
                            and hasattr(text_result, "scores")
                            and text_result.scores
                        )
                        else 1.0
                    )
                    lines.append(
                        {
                            "label": line.label,
                            "text": line.text or "",
                            "bbox": {
                                "xmin": int(line.bbox[0]),
                                "ymin": int(line.bbox[1]),
                                "xmax": int(line.bbox[2]),
                                "ymax": int(line.bbox[3]),
                            },
                            "polygon": " ".join(
                                [f"{int(p[0])},{int(p[1])}" for p in line.polygon]
                            ),
                            "confidence": float(confidence),
                        }
                    )

        # Use page's own image path if available, otherwise map from input URLs
        page_path = getattr(page, "path", None)
        if page_path and os.path.exists(str(page_path)):
            img_url = _build_file_url(str(page_path))
        elif i < len(image_urls):
            img_url = image_urls[i]
        else:
            img_url = image_urls[-1]

        viewer_pages.append(
            {
                "image_url": img_url,
                "width": page.width,
                "height": page.height,
                "lines": lines,
            }
        )

    return viewer_pages


def _generate_viewer(
    collection: Collection, viewer_pages_data: list[dict], export_id: str
) -> str:
    """Generate interactive gallery viewer HTML and return its URL."""
    document_name = collection.label or f"document_{export_id}"

    template = _get_htr_viewer_template()
    html = template.replace("DOCUMENT_NAME_HERE", document_name)
    html = html.replace("PAGES_DATA_HERE", json.dumps(viewer_pages_data))

    html_path = MCP_EXPORT_DIR / f"viewer_{document_name}_{export_id}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return _build_file_url(str(html_path))


def _export_collection(
    collection: Collection, export_format: str, export_id: str
) -> str:
    """Export collection to file and return download URL."""
    format_map = {"alto_xml": "alto", "page_xml": "page", "json": "json"}
    output_format = format_map[export_format]

    export_base_dir = MCP_EXPORT_DIR / export_id
    export_base_dir.mkdir(exist_ok=True)
    export_dir = export_base_dir / output_format

    collection.save(directory=str(export_dir), serializer=output_format)
    exported_files = rename_files_in_directory(str(export_dir), output_format)

    if len(exported_files) > 1:
        zip_path = export_base_dir / f"htrflow_export_{output_format}.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", str(export_dir))
        file_path = str(zip_path)
    else:
        file_path = exported_files[0]

    return _build_file_url(file_path)


@gr.mcp.tool()
def htr_upload_image(filename: str = "image.jpg") -> str:
    """Upload a user-attached image to the server and get a URL for htr_transcribe.

    Use when: User attaches or uploads a local image file and you need a
    server-accessible URL to pass to htr_transcribe.

    NOT needed when: User already provides an http/https URL directly.

    Args:
        filename: The filename from the user's upload (e.g. "letter.jpg")

    Returns:
        Step-by-step instructions for uploading the file and constructing the image_url.
    """
    base_url = _get_base_url() or "http://localhost:7860"

    return f"""To upload '{filename}' for HTR transcription:

1. POST the file to: {base_url}/gradio_api/upload
   Content-Type: multipart/form-data
   Body: files=[("files", ("{filename}", file_bytes, "image/jpeg"))]

2. Extract server path from JSON response:
   Response: ["/tmp/gradio/abc123/{filename}"]
   server_path = response.json()[0]

3. Construct the image_url:
   image_url = "{base_url}/gradio_api/file=" + server_path

4. Collect ALL image_urls, then pass them in a SINGLE htr_transcribe call:
   htr_transcribe(image_urls=[image_url_1, image_url_2, ...])
   IMPORTANT: Do NOT call htr_transcribe separately per image."""


@gr.mcp.tool()
def htr_transcribe(
    image_urls: list[str],
    export_format: Literal["alto_xml", "page_xml", "json"] = "alto_xml",
    language: Literal["swedish", "norwegian", "english", "medieval"] = "swedish",
    layout: Literal["single_page", "spread"] = "single_page",
) -> dict:
    """Transcribe handwritten historical documents and return all results in one call.

    Runs the full HTR (Handwritten Text Recognition) AI pipeline once and returns
    URLs to all generated files. The pipeline is expensive — call this tool ONCE
    with ALL images in the image_urls list. Do NOT call it multiple times for
    images that belong to the same request.

    All outputs are generated from a single pipeline run with minimal overhead.
    The language and layout apply to all images in the batch.

    If the user attached local files, first call htr_upload_image for each file
    to get server-accessible URLs, then pass ALL URLs in a single htr_transcribe call.

    Args:
        image_urls: IMPORTANT: Pass ALL image URLs in a single list. Do NOT call
                    this tool separately per image. Each URL is either a public
                    http/https URL or a Gradio file URL obtained via htr_upload_image.
        export_format: Format for the archival export file.
                       - "alto_xml": ALTO XML (default). Standard archival format.
                       - "page_xml": PAGE XML. Standard archival format.
                       - "json": JSON. Structured data export.
        language: Language of the handwritten documents.
                  - "swedish": Swedish historical documents (default)
                  - "norwegian": Norwegian historical documents
                  - "english": English historical documents
                  - "medieval": Medieval manuscripts
        layout: Physical layout of the document pages.
                - "single_page": Single page or snippet (default)
                - "spread": Two-page book opening / spread

    Returns:
        dict with URLs to all generated files (you can fetch any of these):
            pages_url: URL to a JSON file containing the structured transcription.
                The JSON is a list of pages, each with a list of lines:
                [{page: 1, lines: [{id, text, confidence}, ...]}, ...]
                Fetch this URL to read the transcribed text and confidence scores.
            viewer_url: URL to an interactive HTML gallery viewer. The viewer
                shows document images with polygon overlays on detected text
                lines, confidence highlighting, page navigation for multi-page
                documents, and copy/download text actions. Share this URL with
                the user to explore the transcription visually.
            export_url: URL to download the archival export file in the
                requested export_format. For multi-page documents with multiple
                export files, this is a ZIP archive.
            export_format: The format of the export file (echoed back).

    Examples:
        User: "What does this letter say?"
        → htr_transcribe(image_urls=["https://example.com/letter.jpg"])

        User: "Transcribe these 3 pages and export as PAGE XML"
        → htr_transcribe(image_urls=["url1", "url2", "url3"],
                         export_format="page_xml")

        User: "Read this Swedish manuscript spread"
        → htr_transcribe(image_urls=["https://example.com/spread.jpg"],
                         language="swedish", layout="spread")
    """
    pipeline = _resolve_pipeline(language, layout)
    collection = _run_htr_pipeline(image_urls, pipeline, None, progress=None)

    export_id = str(uuid.uuid4())[:8]

    pages_url = _save_pages_json(collection, export_id)
    viewer_pages_data = _build_viewer_pages_data(collection, image_urls)
    viewer_url = _generate_viewer(collection, viewer_pages_data, export_id)
    export_url = _export_collection(collection, export_format, export_id)

    return {
        "pages_url": pages_url,
        "viewer_url": viewer_url,
        "export_url": export_url,
        "export_format": export_format,
    }
