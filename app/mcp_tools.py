"""
MCP API endpoint for HTRflow handwritten text recognition.

Provides a single outcome-oriented tool that transcribes handwritten documents
and returns results in the format most appropriate for the user's intent.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union, Literal

import gradio as gr
from htrflow.volume.volume import Collection

from app.tabs.submit import run_htrflow, get_yaml
from app.tabs.visualizer import rename_files_in_directory


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


def htrflow_transcribe_document(
    image_urls: Union[str, list[str]],
    document_language: Literal[
        "swedish", "norwegian", "english", "medieval"
    ] = "swedish",
    document_layout: Literal["single_page", "spread"] = "single_page",
    return_format: Literal["analysis_data", "alto_xml", "page_xml", "text", "json"] = "analysis_data",
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

    RETURN FORMAT GUIDE:
    - "analysis_data": Returns structured JSON with text, coordinates, confidence scores, and layout hierarchy.
      Use when user wants to analyze, search, or process the transcription programmatically.
    - "alto_xml" or "page_xml": Returns file path to XML conforming to ALTO/PAGE standards.
      Use when user needs output for document viewers, digital archives, or preservation systems.
    - "text": Returns plain text transcription only.
      Use when user just wants to read the content without metadata.
    - "json": Returns file path to JSON export.
      Use when user wants to download raw structured data.

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

        If return_format is "alto_xml", "page_xml", "text", or "json":
            Returns str: File path to the exported file or ZIP archive (for multiple pages)

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
        ("norwegian", "spread"): "Norwegian - Single page and snippets",  # No spread version
        ("english", "single_page"): "English - Single page and snippets",
        ("english", "spread"): "English - Single page and snippets",  # No spread version
        ("medieval", "single_page"): "Medieval - Single page and snippets",
        ("medieval", "spread"): "Medieval - Single page and snippets",  # No spread version
    }

    pipeline = pipeline_map.get((document_language, document_layout), "Swedish - Single page and snippets")

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
        format_map = {
            "alto_xml": "alto",
            "page_xml": "page",
            "json": "json"
        }
        output_format = format_map[return_format]

        temp_dir = Path(tempfile.mkdtemp())
        export_dir = temp_dir / output_format

        collection.save(directory=str(export_dir), serializer=output_format)
        exported_files = rename_files_in_directory(str(export_dir), output_format)

        if len(exported_files) > 1:
            zip_path = temp_dir / f"htrflow_export_{output_format}.zip"
            shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", str(export_dir))
            return str(zip_path)
        else:
            return exported_files[0]
