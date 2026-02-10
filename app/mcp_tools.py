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


def _extract_text(collection: Collection) -> str:
    """Extract plain text from a Collection."""
    text_lines = []
    for page in collection.pages:
        lines = list(page.traverse(lambda node: node.is_line()))
        for line in lines:
            if line.text:
                text_lines.append(line.text)
    return "\n".join(text_lines)


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

4. Pass image_url to htr_transcribe with desired output format:
   - htr_transcribe(image_url, output="text")      → plain text
   - htr_transcribe(image_url, output="viewer")     → interactive viewer URL
   - htr_transcribe(image_url, output="alto_xml")   → ALTO XML download URL
   - htr_transcribe(image_url, output="page_xml")   → PAGE XML download URL
   - htr_transcribe(image_url, output="json")        → JSON download URL"""


@gr.mcp.tool()
def htr_transcribe(
    image_url: str,
    output: Literal["text", "viewer", "alto_xml", "page_xml", "json"] = "text",
    language: Literal["swedish", "norwegian", "english", "medieval"] = "swedish",
    layout: Literal["single_page", "spread"] = "spread",
) -> Union[str, dict]:
    """Transcribe a handwritten historical document using AI models.

    This is the main transcription tool. It runs the HTR (Handwritten Text Recognition)
    pipeline and returns results in the format specified by the output argument.

    If the user attached a local file, first call htr_upload_image to get an image_url.

    Args:
        image_url: URL to the document image. Either a public http/https URL,
                   or a Gradio file URL obtained via htr_upload_image.
        output: What to return after transcription. Choices:
                - "text": Plain text transcription (default). Best for reading content.
                - "viewer": Interactive HTML viewer URL with polygons, confidence scores,
                  and line-by-line highlighting. Best for visual inspection.
                - "alto_xml": ALTO XML file download URL. Standard archival format.
                - "page_xml": PAGE XML file download URL. Standard archival format.
                - "json": JSON file download URL. Structured data export.
        language: Language of the handwritten document. Choices:
                  - "swedish": Swedish historical documents (default)
                  - "norwegian": Norwegian historical documents
                  - "english": English historical documents
                  - "medieval": Medieval manuscripts
        layout: Physical layout of the document page. Choices:
                - "single_page": Single page or snippet (default)
                - "spread": Two-page book opening / spread

    Returns:
        Depends on the output argument:

        output="text" → str
            Plain text transcription, one line per text line.

        output="viewer" → dict
            {"viewer_url": str, "text_preview": str,
             "stats": {"num_lines": int, "num_pages": int, "avg_confidence": float},
             "message": str}

        output="alto_xml" | "page_xml" | "json" → dict
            {"download_url": str, "format": str, "file_size_kb": float, "message": str}

    Examples:
        User: "What does this letter say?"
        → htr_transcribe("https://example.com/letter.jpg")

        User: "Transcribe this and show me the line regions"
        → htr_transcribe("https://example.com/doc.jpg", output="viewer")

        User: "Export as ALTO XML for our archive"
        → htr_transcribe("https://example.com/doc.jpg", output="alto_xml")

        User: "Read this Swedish manuscript spread"
        → htr_transcribe("https://example.com/spread.jpg", output="text",
                         language="swedish", layout="spread")
    """
    pipeline = _resolve_pipeline(language, layout)
    collection = _run_htr_pipeline(image_url, pipeline, None, progress=None)

    # --- output="text" ---
    if output == "text":
        return _extract_text(collection)

    # --- output="viewer" ---
    if output == "viewer":
        analysis_data = _collection_to_dict(collection)

        export_id = str(uuid.uuid4())[:8]
        json_path = MCP_EXPORT_DIR / f"htr_analysis_{export_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f)

        document_name = collection.label or f"document_{export_id}"

        lines = []
        page = analysis_data["pages"][0]
        for region in page["regions"]:
            lines.extend(region["lines"])

        template = _get_htr_viewer_template()
        html = template.replace("DOCUMENT_NAME_HERE", document_name)
        html = html.replace("IMAGE_URL_HERE", image_url)
        html = html.replace(
            "WIDTH_HERE HEIGHT_HERE", f"{page['width']} {page['height']}"
        )
        html = html.replace("LINES_ARRAY_HERE", json.dumps(lines))

        html_path = MCP_EXPORT_DIR / f"viewer_{document_name}_{export_id}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        viewer_url = _build_file_url(str(html_path))

        total_confidence = sum(
            line["confidence"]
            for page in analysis_data["pages"]
            for region in page["regions"]
            for line in region["lines"]
        )
        avg_confidence = total_confidence / max(analysis_data["num_lines"], 1)

        full_text = _extract_text(collection)
        text_preview = full_text[:500] + ("..." if len(full_text) > 500 else "")

        return {
            "viewer_url": viewer_url,
            "text_preview": text_preview,
            "stats": {
                "num_lines": analysis_data["num_lines"],
                "num_pages": analysis_data["num_pages"],
                "avg_confidence": round(avg_confidence, 3),
            },
            "message": "Open viewer_url in browser to see interactive transcription",
        }

    # --- output="alto_xml" | "page_xml" | "json" ---
    format_map = {"alto_xml": "alto", "page_xml": "page", "json": "json"}
    output_format = format_map[output]

    export_id = str(uuid.uuid4())[:8]
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

    file_size_kb = round(Path(file_path).stat().st_size / 1024, 1)
    download_url = _build_file_url(file_path)

    return {
        "download_url": download_url,
        "format": output,
        "file_size_kb": file_size_kb,
        "message": f"Download {output} file from download_url",
    }
