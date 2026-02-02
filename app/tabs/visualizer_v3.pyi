import gradio as gr
from htrflow.volume.volume import Collection
from gradio_i18n import gettext as _

from gradio.events import Dependency

class HTRVisualizer(gr.HTML):
    """Unified HTR visualization with synchronized image and transcription panels"""

    def __init__(self, max_height="70vh", layout="auto", **kwargs):
        """
        Args:
            max_height: Maximum height for the visualizer (default: "70vh")
            layout: Layout mode - "horizontal" (side-by-side), "vertical" (stacked), or "auto" (responsive)
        """
        html_template = """
        <div class="htr-visualizer" data-layout="${layout}">
            <div class="image-panel" style="max-height: ${maxHeight};">
                <svg class="image-svg" viewBox="0 0 ${value.width} ${value.height}" xmlns="http://www.w3.org/2000/svg">
                    <image height="${value.height}" width="${value.width}" href="/gradio_api/file=${value.path}" />
                    ${value.lines.map((line, idx) => `
                        <a class="textline" data-line-id="${idx}">
                            <polygon points="${line.polygonPoints}"/>
                        </a>
                    `).join('')}
                </svg>
            </div>
            <div class="transcription-panel" style="max-height: ${maxHeight};">
                ${value.regions.map((region, regionIdx) => `
                    <div class="transcription-region">
                        ${region.map((line) => `
                            <span class="transcription-line" data-line-id="${line.id}">
                                ${line.text}
                            </span><br>
                        `).join('')}
                    </div>
                    ${regionIdx < value.regions.length - 1 ? '<hr class="region-divider">' : ''}
                `).join('')}
            </div>
        </div>
        """

        css_template = """
        .htr-visualizer {
            display: flex;
            gap: 0.75rem;
            width: 100%;
        }

        .htr-visualizer[data-layout="horizontal"] {
            flex-direction: row;
        }

        .htr-visualizer[data-layout="vertical"] {
            flex-direction: column;
        }

        .htr-visualizer[data-layout="auto"] {
            flex-direction: row;
        }

        @media (max-width: 768px) {
            .htr-visualizer[data-layout="auto"] {
                flex-direction: column;
            }
        }

        .image-panel {
            flex: 2;
            overflow: auto;
            border: 1px solid var(--border-color-primary);
            border-radius: var(--radius-lg);
            background: var(--background-fill-primary);
            box-sizing: border-box;
        }

        .image-svg {
            width: 100%;
            height: auto;
            display: block;
        }

        .textline polygon {
            fill: transparent;
            stroke: var(--color-accent);
            stroke-width: 8;
            stroke-opacity: 0.3;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .textline:hover polygon,
        .textline.highlighted polygon {
            fill: var(--color-accent);
            fill-opacity: 0.25;
            stroke-width: 10;
            stroke-opacity: 0.5;
        }

        .textline.selected polygon {
            fill: var(--color-accent);
            fill-opacity: 0.4;
            stroke: var(--color-accent);
            stroke-width: 12;
            stroke-opacity: 0.7;
        }

        .transcription-panel {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid var(--border-color-primary);
            border-radius: var(--radius-lg);
            padding: 1rem;
            background: var(--background-fill-primary);
            color: var(--body-text-color);
            font-size: var(--text-lg);
            line-height: 1.8;
            box-sizing: border-box;
        }

        .transcription-region {
            margin-bottom: 0.5rem;
        }

        .transcription-line {
            display: inline;
            padding: 2px 0;
            transition: all 0.2s ease;
            cursor: pointer;
            border-radius: 2px;
        }

        .transcription-line:hover,
        .transcription-line.highlighted {
            background-color: var(--color-accent-soft);
            padding: 2px 4px;
        }

        .transcription-line.selected {
            background-color: var(--color-accent);
            color: var(--color-accent-text-dark);
            font-weight: 600;
            padding: 2px 4px;
        }

        .region-divider {
            margin: 1rem 0;
            border: none;
            border-top: 1px solid var(--border-color-primary);
        }

        /* Scrollbar styling with theme colors */
        .image-panel::-webkit-scrollbar,
        .transcription-panel::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        .image-panel::-webkit-scrollbar-track,
        .transcription-panel::-webkit-scrollbar-track {
            background: var(--background-fill-secondary);
            border-radius: 4px;
        }

        .image-panel::-webkit-scrollbar-thumb,
        .transcription-panel::-webkit-scrollbar-thumb {
            background: var(--border-color-accent);
            border-radius: 4px;
        }

        .image-panel::-webkit-scrollbar-thumb:hover,
        .transcription-panel::-webkit-scrollbar-thumb:hover {
            background: var(--border-color-accent-dark);
        }
        """

        js_on_load = """
        const imagePanel = element.querySelector('.image-panel');
        const transcriptionPanel = element.querySelector('.transcription-panel');
        let selectedLineId = null;

        // Highlight function for hover
        function highlightLine(lineId, isHovering) {
            const imageLines = element.querySelectorAll(`[data-line-id="${lineId}"]`);
            imageLines.forEach(el => {
                if (isHovering) {
                    el.classList.add('highlighted');
                } else {
                    el.classList.remove('highlighted');
                }
            });
        }

        // Select function for click
        function selectLine(lineId) {
            // Clear previous selection
            element.querySelectorAll('.selected').forEach(el => {
                el.classList.remove('selected');
            });

            // Set new selection
            if (lineId !== null) {
                const elements = element.querySelectorAll(`[data-line-id="${lineId}"]`);
                elements.forEach(el => el.classList.add('selected'));

                // Scroll transcription to selected line
                const transcriptionLine = transcriptionPanel.querySelector(`.transcription-line[data-line-id="${lineId}"]`);
                if (transcriptionLine) {
                    transcriptionLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }

            selectedLineId = lineId;
            props.selectedLine = lineId;
        }

        // Add hover listeners to all lines
        element.querySelectorAll('[data-line-id]').forEach(lineEl => {
            const lineId = lineEl.dataset.lineId;

            lineEl.addEventListener('mouseenter', () => {
                highlightLine(lineId, true);
            });

            lineEl.addEventListener('mouseleave', () => {
                highlightLine(lineId, false);
            });

            lineEl.addEventListener('click', () => {
                const newSelection = selectedLineId === lineId ? null : lineId;
                selectLine(newSelection);
                trigger('line_selected', { lineId: newSelection });
            });
        });
        """

        super().__init__(
            value={"width": 100, "height": 100, "path": "", "lines": [], "regions": []},
            html_template=html_template,
            css_template=css_template,
            js_on_load=js_on_load,
            maxHeight=max_height,
            layout=layout,
            **kwargs
        )

    def api_info(self):
        return {
            "type": "object",
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"},
                "path": {"type": "string"},
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "polygonPoints": {"type": "string"},
                            "id": {"type": "integer"}
                        }
                    }
                },
                "regions": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "text": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component


def prepare_visualizer_data(collection: Collection, current_page_index: int):
    """Convert collection page to format expected by HTRVisualizer"""
    page = collection[current_page_index]
    lines = list(page.traverse(lambda node: node.is_line()))

    # Prepare regions with line IDs
    regions_raw = page.traverse(
        lambda node: node.children and all(child.is_line() for child in node)
    )

    line_counter = 0
    region_data = []
    for region in regions_raw:
        region_lines = []
        for line in region:
            region_lines.append({
                "id": line_counter,
                "text": line.text
            })
            line_counter += 1
        region_data.append(region_lines)

    return {
        "width": page.width,
        "height": page.height,
        "path": page.path,
        "lines": [
            {
                "polygonPoints": " ".join([f"{p[0]},{p[1]}" for p in line.polygon]),
                "id": idx
            }
            for idx, line in enumerate(lines)
        ],
        "regions": region_data
    }


def toggle_navigation_button(collection: Collection):
    visible = len(collection.pages) > 1
    return gr.update(visible=visible)


def activate_left_button(current_page_index):
    interactive = current_page_index > 0
    return gr.update(interactive=interactive)


def activate_right_button(collection: Collection, current_page_index):
    interactive = current_page_index + 1 < len(collection.pages)
    return gr.update(interactive=interactive)


def right_button_click(collection: Collection, current_page_index):
    max_index = len(collection.pages) - 1
    return min(max_index, current_page_index + 1)


def left_button_click(current_page_index):
    return max(0, current_page_index - 1)


def update_image_caption(collection: Collection, current_page_index):
    n_pages = len(collection.pages)
    return f"**Image {current_page_index + 1} of {n_pages}:** `{collection[current_page_index].label}`"


with gr.Blocks() as visualizer:
    gr.Markdown(
        _("Hover over text regions to highlight, click to select. Both panels scroll independently within a fixed height.")
    )

    visualizer_component = HTRVisualizer(
        max_height="70vh",
        layout="auto",
    )

    image_caption = gr.Markdown()
    with gr.Row(elem_classes="button-group-viz"):
        left = gr.Button(
            _("← Previous"), visible=False, interactive=False, scale=0
        )
        right = gr.Button(_("Next →"), visible=False, scale=0)

    collection = gr.State()
    current_page_index = gr.State(0)

    # Wiring of navigation buttons
    left.click(left_button_click, current_page_index, current_page_index)
    right.click(
        right_button_click, [collection, current_page_index], current_page_index
    )

    # Updates on collection change
    collection.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component
    )
    collection.change(lambda _: 0, current_page_index, current_page_index)
    collection.change(toggle_navigation_button, collection, left)
    collection.change(toggle_navigation_button, collection, right)
    collection.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )

    # Updates on page change
    current_page_index.change(
        prepare_visualizer_data,
        inputs=[collection, current_page_index],
        outputs=visualizer_component
    )
    current_page_index.change(activate_left_button, current_page_index, left)
    current_page_index.change(
        activate_right_button, [collection, current_page_index], right
    )
    current_page_index.change(
        update_image_caption,
        inputs=[collection, current_page_index],
        outputs=image_caption,
    )