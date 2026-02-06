"""
MCP API endpoint for HTRflow handwritten text recognition.

Provides a single outcome-oriented tool that transcribes handwritten documents
and returns results in the format most appropriate for the user's intent.
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


@gr.mcp.resource("htr_upload_image://{filename}")
def htr_upload_image(filename: str) -> str:
    """
    Get instructions for uploading an image to use with HTR transcription.

    When user attaches an image, use this resource to understand how to
    convert it to a public URL for htrflow_transcribe_document.

    Args:
        filename: The filename from the user's upload path

    Returns:
        Instructions for handling image uploads
    """
    base_url = _get_base_url() or "http://localhost:7860"

    return f"""To process uploaded image '{filename}' for HTR transcription:

1. Upload the file via: POST {base_url}/gradio_api/upload
2. Extract server path from JSON response (e.g., "/tmp/gradio/abc123/file.jpg")
3. Construct full URL: {base_url}/gradio_api/file={{server_path}}
4. Pass this URL to htrflow_transcribe_document tool

Example:
```python
import requests
files = {{"files": (filename, image_data, "image/jpeg")}}
response = requests.post("{base_url}/gradio_api/upload", files=files)
server_path = response.json()[0]
image_url = f"{base_url}/gradio_api/file={{server_path}}"
```"""


def _get_htr_viewer_template() -> str:
    """Load the HTR viewer HTML template from file."""
    template_path = (
        Path(__file__).parent / "tabs" / "visualizer" / "generate_viewer_template.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@gr.mcp.tool()
def htr_generate_viewer(analysis_data: dict, image_url: str, document_name: str) -> str:
    """Generate complete interactive HTML viewer for HTR transcription results.

    Creates a split-view interface with synchronized image and text panels.
    Click on lines in either panel to highlight them in both views.

    Args:
        analysis_data: Dict with structure {"pages": [{"width": int, "height": int, "regions": [...]}]}
        image_url: Full URL to the document image
        document_name: Name of the document (for display and download filename)

    Returns:
        Complete HTML string ready to save or display
    """
    lines = []
    page = analysis_data["pages"][0]

    for region in page["regions"]:
        lines.extend(region["lines"])

    template = _get_htr_viewer_template()

    html = template.replace("DOCUMENT_NAME_HERE", document_name)
    html = html.replace("IMAGE_URL_HERE", image_url)
    html = html.replace("WIDTH_HERE HEIGHT_HERE", f"{page['width']} {page['height']}")
    html = html.replace("LINES_ARRAY_HERE", json.dumps(lines))

    return html


@gr.mcp.prompt()
def htr_transcribe_workflow(
    language: str = "swedish", layout: str = "single_page", return_format: str = "text"
) -> str:
    """Workflow guide for transcribing user-uploaded handwritten documents."""
    base_url = _get_base_url() or "http://localhost:7860"

    return f"""When user attaches an image for HTR transcription:

STEP 1: Handle the image upload
- If image_url starts with "/" or is a local path:
  * Upload to {base_url}/gradio_api/upload
  * Extract path from response
  * Construct URL: {base_url}/gradio_api/file={{path}}
- If image_url is already http/https: use directly

STEP 2: Call htrflow_transcribe_document
- document_language: {language} (or swedish/norwegian/english/medieval)
- document_layout: {layout} (single_page or spread)
- return_format: {return_format} (text/analysis_data/alto_xml/page_xml/json)

STEP 3: Present results appropriately
- text format: show transcription directly
- analysis_data: use htr_generate_viewer tool to create interactive HTML viewer
- XML/JSON formats: provide download URL

IMPORTANT: Ask user what output format they want BEFORE transcribing!
"""


def _collection_to_dict(collection: Collection) -> dict:
    """Convert Collection to serializable dict with full structure."""
    pages_data = []
    total_lines = 0

    for page in collection.pages:
        regions_raw = list(
            page.traverse(
                lambda node: node.children and all(child.is_line() for child in node)
            )
        )

        regions_data = []
        for region in regions_raw:
            lines_data = []

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

                    lines_data.append(
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
                    total_lines += 1

            if lines_data:
                regions_data.append(
                    {
                        "label": region.label,
                        "bbox": {
                            "xmin": int(region.bbox[0]),
                            "ymin": int(region.bbox[1]),
                            "xmax": int(region.bbox[2]),
                            "ymax": int(region.bbox[3]),
                        },
                        "polygon": " ".join(
                            [f"{int(p[0])},{int(p[1])}" for p in region.polygon]
                        ),
                        "lines": lines_data,
                    }
                )

        pages_data.append(
            {
                "label": page.label,
                "width": page.width,
                "height": page.height,
                "path": page.path,
                "regions": regions_data,
            }
        )

    return {
        "label": collection.label,
        "num_pages": len(collection.pages),
        "num_lines": total_lines,
        "pages": pages_data,
    }


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
    Core HTR pipeline execution - used by all MCP tools.

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


@gr.mcp.tool()
def htrflow_transcribe_document(
    image_urls: Union[str, list[str]],
    document_language: Literal[
        "swedish", "norwegian", "english", "medieval"
    ] = "swedish",
    document_layout: Literal["single_page", "spread"] = "single_page",
    return_format: Literal[
        "analysis_data", "alto_xml", "page_xml", "text", "json"
    ] = "analysis_data",
    custom_yaml: Optional[str] = None,
) -> Union[dict, str]:
    """
    Transcribe handwritten historical documents using HTRflow specialized models.

    WHEN TO USE THIS TOOL:
    - User asks to transcribe, read, or extract text from handwritten documents
    - User provides image URLs of historical manuscripts, letters, or archival materials
    - User wants to analyze layout, extract coordinates, or get confidence scores from handwriting
    - User needs standardized XML formats (ALTO/PAGE) for digital humanities tools

    DO NOT USE for:
    - Modern printed text (use OCR tools instead)
    - User hasn't provided image URLs yet
    - General questions about handwriting (answer directly)

    IMAGE UPLOAD HANDLING:
    If user attaches an image (local file path), you must first convert it to a URL:
    1. Upload via POST to /gradio_api/upload endpoint
    2. Extract server path from response
    3. Construct URL: {base_url}/gradio_api/file={server_path}
    See the htr_image:// MCP resource or transcribe_uploaded_document prompt for details.

    RETURN FORMAT GUIDE:
    - "analysis_data": Returns structured JSON with text, coordinates, confidence scores, and layout hierarchy.
      Use when user wants to analyze, search, or process the transcription programmatically.
      RETURNS: dict object (ready to use immediately)

    - "text": Returns plain text transcription only.
      Use when user just wants to read the content without metadata.
      RETURNS: str with plain text (ready to use immediately)

    - "alto_xml" or "page_xml": Returns download URL to XML file conforming to ALTO/PAGE standards.
      Use when user needs output for document viewers, digital archives, or preservation systems.
      RETURNS: str with full download URL (e.g., "https://example.com/gradio_api/file=/path/to/file.xml")

    - "json": Returns download URL to JSON export file.
      Use when user wants to download raw structured data.
      RETURNS: str with full download URL (e.g., "https://example.com/gradio_api/file=/path/to/file.json")

    Args:
        image_urls: Single image URL or list of image URLs pointing to document images.
                   Must be publicly accessible URLs (http:// or https://).
        document_language: Language of the handwritten text. Choices:
                          - "swedish": Swedish historical documents (default)
                          - "norwegian": Norwegian historical documents
                          - "english": English historical documents
                          - "medieval": Medieval manuscripts
        document_layout: Physical layout of the document. Choices:
                        - "single_page": Single page or snippets (default)
                        - "spread": Two-page spread (book opening)
        return_format: Output format based on user's intent. Choices:
                      - "analysis_data": JSON with full hierarchy, coordinates, confidence (default)
                      - "alto_xml": ALTO XML file path for archival systems
                      - "page_xml": PAGE XML file path for document viewers
                      - "text": Plain text transcription only
                      - "json": JSON file path for download
        custom_yaml: Advanced: Custom HTRflow YAML pipeline config. Only use if user provides
                    specific model settings. Overrides document_language and document_layout.

    Returns:
        If return_format is "analysis_data":
            Returns dict with structure:
            {
                "label": str,
                "num_pages": int,
                "num_lines": int,
                "pages": [{
                    "label": str,
                    "width": int,
                    "height": int,
                    "path": str,
                    "regions": [{
                        "label": str,
                        "bbox": {"xmin": int, "ymin": int, "xmax": int, "ymax": int},
                        "polygon": str,
                        "lines": [{
                            "text": str,
                            "bbox": {"xmin": int, "ymin": int, "xmax": int, "ymax": int},
                            "polygon": str,
                            "confidence": float
                        }]
                    }]
                }]
            }

        If return_format is "text":
            Returns str: Plain text transcription

        If return_format is "alto_xml", "page_xml", or "json":
            Returns str: Full download URL to the exported file or ZIP archive (for multiple pages).
            Example: "https://riksarkivet-htr-demo.hf.space/gradio_api/file=/path/to/file.xml"
            The URL can be used directly to download or fetch the file content.

    Example:
        User: "Can you transcribe this Swedish letter? https://example.com/letter.jpg"
        Tool call: htrflow_transcribe_document(
            image_urls="https://example.com/letter.jpg",
            document_language="swedish",
            document_layout="single_page",
            return_format="text"
        )

        User: "I need to analyze the layout and confidence scores of this manuscript"
        Tool call: htrflow_transcribe_document(
            image_urls="https://example.com/manuscript.jpg",
            document_language="medieval",
            return_format="analysis_data"
        )
    """
    # Map user-friendly parameters to internal pipeline names
    pipeline_map = {
        ("swedish", "single_page"): "Swedish - Single page and snippets",
        ("swedish", "spread"): "Swedish - Spreads",
        ("norwegian", "single_page"): "Norwegian - Single page and snippets",
        (
            "norwegian",
            "spread",
        ): "Norwegian - Single page and snippets",  # No spread version
        ("english", "single_page"): "English - Single page and snippets",
        (
            "english",
            "spread",
        ): "English - Single page and snippets",  # No spread version
        ("medieval", "single_page"): "Medieval - Single page and snippets",
        (
            "medieval",
            "spread",
        ): "Medieval - Single page and snippets",  # No spread version
    }

    pipeline = pipeline_map.get(
        (document_language, document_layout), "Swedish - Single page and snippets"
    )

    # Run HTR pipeline
    collection = _run_htr_pipeline(image_urls, pipeline, custom_yaml, progress=None)

    # Return based on requested format
    if return_format == "analysis_data":
        return _collection_to_dict(collection)

    elif return_format == "text":
        # Extract plain text
        text_lines = []
        for page in collection.pages:
            lines = list(page.traverse(lambda node: node.is_line()))
            for line in lines:
                if line.text:
                    text_lines.append(line.text)
        return "\n".join(text_lines)

    else:
        # Export to file format (alto_xml, page_xml, json)
        format_map = {"alto_xml": "alto", "page_xml": "page", "json": "json"}
        output_format = format_map[return_format]

        export_id = str(uuid.uuid4())[:8]
        export_base_dir = MCP_EXPORT_DIR / export_id
        export_base_dir.mkdir(exist_ok=True)
        export_dir = export_base_dir / output_format

        collection.save(directory=str(export_dir), serializer=output_format)
        exported_files = rename_files_in_directory(str(export_dir), output_format)

        # Determine the file to return
        if len(exported_files) > 1:
            zip_path = export_base_dir / f"htrflow_export_{output_format}.zip"
            shutil.make_archive(
                str(zip_path).replace(".zip", ""), "zip", str(export_dir)
            )
            file_path = str(zip_path)
        else:
            file_path = exported_files[0]

        # Construct full URL for file download
        base_url = _get_base_url()
        file_url = f"/gradio_api/file={file_path}"

        # Return full URL if we have a base URL, otherwise relative URL
        if base_url:
            return f"{base_url}{file_url}"
        else:
            return file_url
