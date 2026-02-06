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


@gr.mcp.tool()
def htr_upload_image(filename: str = "image.jpg") -> str:
    """Get instructions for uploading an image to use with HTR transcription.

    When user attaches an image, use this tool to understand how to
    convert it to a public URL for htrflow_transcribe_document.

    Args:
        filename: The filename from the user's upload path (optional)

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


@gr.mcp.tool()
def htr_transcribe_workflow(
    language: str = "swedish", layout: str = "single_page", return_format: str = "text"
) -> str:
    """REQUIRED FIRST STEP: Get workflow guide before any HTR transcription.

    ⚠️ IMPORTANT: ALWAYS call this tool FIRST when user wants to transcribe handwritten text.
    This provides the complete workflow and prevents common mistakes.

    WHEN TO USE:
    - User asks to transcribe/read/extract text from handwritten documents
    - User uploads an image and mentions handwriting/manuscripts/historical documents
    - BEFORE calling htrflow_transcribe_document or any other HTR tool

    Args:
        language: Target language (swedish/norwegian/english/medieval)
        layout: Document layout (single_page/spread)
        return_format: Desired output (text/analysis_data/alto_xml/page_xml/json)

    Returns:
        Step-by-step workflow instructions for the transcription process
    """
    base_url = _get_base_url() or "http://localhost:7860"

    return f"""HTR TRANSCRIPTION WORKFLOW - Follow these steps in order:

═══════════════════════════════════════════════════════════════
STEP 1: ASK USER FOR PREFERENCES (if not specified)
═══════════════════════════════════════════════════════════════
Ask the user:
1. What language is the document? (swedish/{language}/norwegian/english/medieval)
2. What layout type? (single_page/{layout}/spread)
3. What output format do they want?
   - text: Just the transcribed text
   - analysis_data: Full data with coordinates + confidence scores (for visualization)
   - alto_xml/page_xml: XML files for archival systems
   - json: JSON export file

═══════════════════════════════════════════════════════════════
STEP 2: HANDLE IMAGE UPLOAD
═══════════════════════════════════════════════════════════════
If user provides a local file path or attachment:
1. Call htr_upload_image tool to get detailed upload instructions
2. Upload file to {base_url}/gradio_api/upload
3. Extract server path from JSON response
4. Construct URL: {base_url}/gradio_api/file={{server_path}}

If user provides http/https URL: use it directly

═══════════════════════════════════════════════════════════════
STEP 3: CALL TRANSCRIPTION TOOL
═══════════════════════════════════════════════════════════════
Call htrflow_transcribe_document with:
- image_urls: The URL from Step 2
- document_language: From Step 1 (default: {language})
- document_layout: From Step 1 (default: {layout})
- return_format: From Step 1 (default: {return_format})

═══════════════════════════════════════════════════════════════
STEP 4: PRESENT RESULTS
═══════════════════════════════════════════════════════════════
Based on return_format:
- text: Show the transcription directly to user
- analysis_data: Offer to call htr_generate_viewer to create interactive HTML
- XML/JSON: Provide the download URL returned by the tool

═══════════════════════════════════════════════════════════════
WORKFLOW COMPLETE - User can now read, download, or visualize results
═══════════════════════════════════════════════════════════════
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
    """Transcribe handwritten historical documents using HTRflow specialized models.

    ⚠️ PREREQUISITE: Call htr_transcribe_workflow FIRST to get the complete workflow!

    WHEN TO USE THIS TOOL:
    - User has uploaded/provided image URLs of handwritten documents
    - You have already called htr_transcribe_workflow to understand the process
    - Image URLs are properly formatted (http/https URLs accessible by the server)

    DO NOT USE for:
    - Modern printed text (use OCR tools instead)
    - Before calling htr_transcribe_workflow first
    - When user hasn't provided image URLs yet
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


# ═══════════════════════════════════════════════════════════════
# NEW OUTCOME-ORIENTED TOOLS (Token-Optimized)
# ═══════════════════════════════════════════════════════════════


@gr.mcp.tool()
def htr_transcribe_text(
    image_url: str,
    language: Literal["swedish", "norwegian", "english", "medieval"] = "swedish",
    layout: Literal["single_page", "spread"] = "single_page",
) -> str:
    """Transcribe handwritten historical document and return plain text.

    Use when: User wants to read what the document says.

    Args:
        image_url: Direct URL to document image (http/https, must be accessible by server)
        language: Document language (swedish=default, norwegian, english, medieval)
        layout: Page layout (single_page=default, spread=two-page book opening)

    Returns:
        Plain text transcription of the document.

    Example:
        User: "What does this Swedish letter say?"
        → htr_transcribe_text("https://example.com/letter.jpg", "swedish")
        → Returns: "Kära Maria, Jag skriver..."
    """
    pipeline_map = {
        ("swedish", "single_page"): "Swedish - Single page and snippets",
        ("swedish", "spread"): "Swedish - Spreads",
        ("norwegian", "single_page"): "Norwegian - Single page and snippets",
        ("norwegian", "spread"): "Norwegian - Single page and snippets",
        ("english", "single_page"): "English - Single page and snippets",
        ("english", "spread"): "English - Single page and snippets",
        ("medieval", "single_page"): "Medieval - Single page and snippets",
        ("medieval", "spread"): "Medieval - Single page and snippets",
    }

    pipeline = pipeline_map.get((language, layout), "Swedish - Single page and snippets")
    collection = _run_htr_pipeline(image_url, pipeline, None, progress=None)

    text_lines = []
    for page in collection.pages:
        lines = list(page.traverse(lambda node: node.is_line()))
        for line in lines:
            if line.text:
                text_lines.append(line.text)

    return "\n".join(text_lines)


@gr.mcp.tool()
def htr_transcribe_and_visualize(
    image_url: str,
    language: Literal["swedish", "norwegian", "english", "medieval"] = "swedish",
    layout: Literal["single_page", "spread"] = "single_page",
) -> dict:
    """Transcribe document and generate interactive visualization.

    Use when: User wants to see transcription WITH line-by-line visualization,
    confidence scores, or clickable regions.

    Args:
        image_url: Direct URL to document image (must be accessible by server)
        language: Document language (default: swedish)
        layout: Page layout (default: single_page)

    Returns:
        {
            "viewer_url": "https://.../viewer_abc123.html",
            "text_preview": "First 500 characters...",
            "stats": {
                "num_lines": 45,
                "num_pages": 1,
                "avg_confidence": 0.94
            },
            "message": "Open viewer_url to see interactive transcription"
        }

    Example:
        User: "Transcribe this and show me where the text is"
        → htr_transcribe_and_visualize("https://example.com/doc.jpg")
        → Returns viewer URL + stats (small response ~300 tokens)
    """
    pipeline_map = {
        ("swedish", "single_page"): "Swedish - Single page and snippets",
        ("swedish", "spread"): "Swedish - Spreads",
        ("norwegian", "single_page"): "Norwegian - Single page and snippets",
        ("norwegian", "spread"): "Norwegian - Single page and snippets",
        ("english", "single_page"): "English - Single page and snippets",
        ("english", "spread"): "English - Single page and snippets",
        ("medieval", "single_page"): "Medieval - Single page and snippets",
        ("medieval", "spread"): "Medieval - Single page and snippets",
    }

    pipeline = pipeline_map.get((language, layout), "Swedish - Single page and snippets")
    collection = _run_htr_pipeline(image_url, pipeline, None, progress=None)

    # Convert to dict and save as JSON (no token cost!)
    analysis_data = _collection_to_dict(collection)

    export_id = str(uuid.uuid4())[:8]
    json_filename = f"htr_analysis_{export_id}.json"
    json_path = MCP_EXPORT_DIR / json_filename

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f)

    # Generate HTML viewer (reads from file, not from parameter)
    document_name = collection.label or f"document_{export_id}"

    # Extract lines for viewer
    lines = []
    page = analysis_data["pages"][0]
    for region in page["regions"]:
        lines.extend(region["lines"])

    # Load template and generate HTML
    template = _get_htr_viewer_template()
    html = template.replace("DOCUMENT_NAME_HERE", document_name)
    html = html.replace("IMAGE_URL_HERE", image_url)
    html = html.replace("WIDTH_HERE HEIGHT_HERE", f'{page["width"]} {page["height"]}')
    html = html.replace("LINES_ARRAY_HERE", json.dumps(lines))

    # Save HTML to file
    html_filename = f"viewer_{document_name}_{export_id}.html"
    html_path = MCP_EXPORT_DIR / html_filename

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Construct URLs
    base_url = _get_base_url()
    viewer_url = f"{base_url}/gradio_api/file={html_path}" if base_url else f"/gradio_api/file={html_path}"

    # Calculate stats
    total_confidence = sum(
        line["confidence"]
        for page in analysis_data["pages"]
        for region in page["regions"]
        for line in region["lines"]
    )
    avg_confidence = total_confidence / max(analysis_data["num_lines"], 1)

    # Get text preview
    text_lines = []
    for page in collection.pages:
        lines_obj = list(page.traverse(lambda node: node.is_line()))
        for line in lines_obj:
            if line.text:
                text_lines.append(line.text)
    full_text = "\n".join(text_lines)
    text_preview = full_text[:500] + ("..." if len(full_text) > 500 else "")

    return {
        "viewer_url": viewer_url,
        "text_preview": text_preview,
        "stats": {
            "num_lines": analysis_data["num_lines"],
            "num_pages": analysis_data["num_pages"],
            "avg_confidence": round(avg_confidence, 3),
        },
        "message": "Open viewer_url in your browser to see the interactive transcription with clickable regions",
    }


@gr.mcp.tool()
def htr_transcribe_and_export(
    image_url: str,
    export_format: Literal["alto_xml", "page_xml", "json"],
    language: Literal["swedish", "norwegian", "english", "medieval"] = "swedish",
    layout: Literal["single_page", "spread"] = "single_page",
) -> dict:
    """Transcribe document and export to standard archival format.

    Use when: User needs ALTO XML, PAGE XML, or JSON for digital humanities
    tools, archives, or further processing.

    Args:
        image_url: Direct URL to document image (must be accessible by server)
        export_format: Output format (alto_xml, page_xml, json)
        language: Document language (default: swedish)
        layout: Page layout (default: single_page)

    Returns:
        {
            "download_url": "https://.../export_abc123.xml",
            "format": "alto_xml",
            "file_size_kb": 125,
            "message": "Download file from download_url"
        }

    Example:
        User: "Export this as ALTO XML"
        → htr_transcribe_and_export("https://example.com/doc.jpg", "alto_xml")
        → Returns download URL
    """
    pipeline_map = {
        ("swedish", "single_page"): "Swedish - Single page and snippets",
        ("swedish", "spread"): "Swedish - Spreads",
        ("norwegian", "single_page"): "Norwegian - Single page and snippets",
        ("norwegian", "spread"): "Norwegian - Single page and snippets",
        ("english", "single_page"): "English - Single page and snippets",
        ("english", "spread"): "English - Single page and snippets",
        ("medieval", "single_page"): "Medieval - Single page and snippets",
        ("medieval", "spread"): "Medieval - Single page and snippets",
    }

    pipeline = pipeline_map.get((language, layout), "Swedish - Single page and snippets")
    collection = _run_htr_pipeline(image_url, pipeline, None, progress=None)

    # Export to requested format
    format_map = {"alto_xml": "alto", "page_xml": "page", "json": "json"}
    output_format = format_map[export_format]

    export_id = str(uuid.uuid4())[:8]
    export_base_dir = MCP_EXPORT_DIR / export_id
    export_base_dir.mkdir(exist_ok=True)
    export_dir = export_base_dir / output_format

    collection.save(directory=str(export_dir), serializer=output_format)
    exported_files = rename_files_in_directory(str(export_dir), output_format)

    # Determine the file to return
    if len(exported_files) > 1:
        zip_path = export_base_dir / f"htrflow_export_{output_format}.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", str(export_dir))
        file_path = str(zip_path)
    else:
        file_path = exported_files[0]

    # Get file size
    file_size_kb = round(Path(file_path).stat().st_size / 1024, 1)

    # Construct URL
    base_url = _get_base_url()
    file_url = f"/gradio_api/file={file_path}"
    download_url = f"{base_url}{file_url}" if base_url else file_url

    return {
        "download_url": download_url,
        "format": export_format,
        "file_size_kb": file_size_kb,
        "message": f"Download {export_format} file from download_url",
    }
