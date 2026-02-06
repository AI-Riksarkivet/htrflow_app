"""
MCP API endpoints for HTRflow handwritten text recognition.

Two tools with distinct use cases:
- htr_for_analysis: Returns structured JSON data for LLM analysis and exploration
- htr_export_format: Exports to standardized formats (ALTO/PAGE XML) for document viewers
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union

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

    result = next(
        run_htrflow(
            yaml_config, batch_images, progress=progress if progress else gr.Progress()
        )
    )
    return result[0]


def htr_for_analysis(
    image_urls: Union[str, list[str]],
    pipeline: str = "Swedish - Spreads",
    custom_yaml: Optional[str] = None,
    progress: gr.Progress = None,
) -> dict:
    """
    Transcribe handwritten documents and return structured data for analysis.

    Returns complete hierarchical data including text, coordinates, confidence scores,
    and layout information. Use this when you need to analyze the document structure,
    extract specific regions, or perform further processing with the LLM.

    Args:
        image_urls: Image URL(s) to process
        pipeline: Pipeline name - "Swedish - Spreads", "Swedish - Single page and snippets",
                  "Norwegian - Single page and snippets", "Medieval - Single page and snippets",
                  or "English - Single page and snippets"
        custom_yaml: Custom HTRflow YAML config (overrides pipeline)
        progress: Progress tracker

    Returns:
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
                    "bbox": {"xmin", "ymin", "xmax", "ymax"},
                    "polygon": str,
                    "lines": [{
                        "text": str,
                        "bbox": {"xmin", "ymin", "xmax", "ymax"},
                        "polygon": str,
                        "confidence": float
                    }]
                }]
            }]
        }
    """
    collection = _run_htr_pipeline(image_urls, pipeline, custom_yaml, progress)

    if progress:
        progress(0.95, desc="Structuring data")

    data = _collection_to_dict(collection)

    if progress:
        progress(1.0, desc="Complete")

    return data


def htr_export_format(
    image_urls: Union[str, list[str]],
    pipeline: str = "Swedish - Spreads",
    output_format: str = "alto",
    custom_yaml: Optional[str] = None,
    progress: gr.Progress = None,
) -> str:
    """
    Transcribe handwritten documents and export to standardized format.

    Exports results to formats supported by document analysis tools and viewers.
    ALTO and PAGE XML are standard formats for historical document digitization
    that preserve layout, text, and metadata for visualization in specialized viewers.

    Args:
        image_urls: Image URL(s) to process
        pipeline: Pipeline name - "Swedish - Spreads", "Swedish - Single page and snippets",
                  "Norwegian - Single page and snippets", "Medieval - Single page and snippets",
                  or "English - Single page and snippets"
        output_format: Export format - "txt", "alto", "page", or "json"
        custom_yaml: Custom HTRflow YAML config (overrides pipeline)
        progress: Progress tracker

    Returns:
        File path to exported file (single page) or ZIP archive (multiple pages)
    """
    valid_formats = ["txt", "alto", "page", "json"]
    if output_format not in valid_formats:
        raise ValueError(
            f"output_format must be one of {valid_formats}, got: {output_format}"
        )

    collection = _run_htr_pipeline(image_urls, pipeline, custom_yaml, progress)

    if progress:
        progress(0.9, desc=f"Exporting to {output_format} format")

    temp_dir = Path(tempfile.mkdtemp())
    export_dir = temp_dir / output_format

    collection.save(directory=str(export_dir), serializer=output_format)
    exported_files = rename_files_in_directory(str(export_dir), output_format)

    if len(exported_files) > 1:
        zip_path = temp_dir / f"export_{output_format}.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", str(export_dir))
        file_path = str(zip_path)
    else:
        file_path = exported_files[0]

    if progress:
        progress(1.0, desc="Export complete")

    return file_path


def htr_for_analysis_mcp(
    image_urls: Union[str, list[str]],
    pipeline: str = "Swedish - Spreads",
    custom_yaml: Optional[str] = None,
) -> dict:
    """
    Transcribe handwritten documents and return structured data for analysis.

    Returns complete hierarchical data including text, coordinates, confidence scores,
    and layout information. Use this when you need to analyze the document structure,
    extract specific regions, or perform further processing with the LLM.

    Args:
        image_urls: Image URL(s) to process
        pipeline: Pipeline name - "Swedish - Spreads", "Swedish - Single page and snippets",
                  "Norwegian - Single page and snippets", "Medieval - Single page and snippets",
                  or "English - Single page and snippets"
        custom_yaml: Custom HTRflow YAML config (overrides pipeline)

    Returns:
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
                    "bbox": {"xmin", "ymin", "xmax", "ymax"},
                    "polygon": str,
                    "lines": [{
                        "text": str,
                        "bbox": {"xmin", "ymin", "xmax", "ymax"},
                        "polygon": str,
                        "confidence": float
                    }]
                }]
            }]
        }
    """
    return htr_for_analysis(image_urls, pipeline, custom_yaml, progress=None)


def htr_export_format_mcp(
    image_urls: Union[str, list[str]],
    pipeline: str = "Swedish - Spreads",
    output_format: str = "alto",
    custom_yaml: Optional[str] = None,
) -> str:
    """
    Transcribe handwritten documents and export to standardized format.

    Exports results to formats supported by document analysis tools and viewers.
    ALTO and PAGE XML are standard formats for historical document digitization
    that preserve layout, text, and metadata for visualization in specialized viewers.

    Args:
        image_urls: Image URL(s) to process
        pipeline: Pipeline name - "Swedish - Spreads", "Swedish - Single page and snippets",
                  "Norwegian - Single page and snippets", "Medieval - Single page and snippets",
                  or "English - Single page and snippets"
        output_format: Export format - "txt", "alto", "page", or "json"
        custom_yaml: Custom HTRflow YAML config (overrides pipeline)

    Returns:
        File path to exported file (single page) or ZIP archive (multiple pages)
    """
    return htr_export_format(
        image_urls, pipeline, output_format, custom_yaml, progress=None
    )
