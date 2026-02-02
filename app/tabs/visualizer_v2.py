import gradio as gr
from htrflow.volume.volume import Collection
from gradio_i18n import gettext as _


class AnnotatedImageViewer(gr.HTML):
    """Interactive annotated image viewer with text region highlighting"""

    def __init__(self, **kwargs):
        html_template = """
        <div class="annotated-viewer-container">
            <svg id="image-svg" viewBox="0 0 ${value.width} ${value.height}" xmlns="http://www.w3.org/2000/svg">
                <image height="${value.height}" width="${value.width}" href="/gradio_api/file=${value.path}" />
                ${value.lines.map((line, idx) => `
                    <a class="textline line-${idx}"
                       data-line-id="${idx}"
                       onmouseover="window.highlightLine(${idx}, true)"
                       onmouseout="window.highlightLine(${idx}, false)">
                        <polygon points="${line.polygonPoints}"/>
                    </a>
                `).join('')}
            </svg>
        </div>
        """

        css_template = """
        .annotated-viewer-container {
            width: 100%;
            height: 100%;
        }

        #image-svg {
            width: 100%;
            height: auto;
            display: block;
        }

        .textline polygon {
            fill: transparent;
            stroke: #3b82f6;
            stroke-width: 8;
            stroke-opacity: 0.3;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .textline:hover polygon {
            fill: #3b82f6;
            fill-opacity: 0.25;
            stroke-width: 10;
            stroke-opacity: 0.5;
        }

        .textline.highlighted polygon {
            fill: #3b82f6;
            fill-opacity: 0.3;
            stroke-width: 12;
            stroke-opacity: 0.7;
        }
        """

        js_on_load = """
        // Global highlight function shared between image and transcription
        window.highlightLine = function(lineId, highlight) {
            // Highlight image polygon
            const imageLines = element.querySelectorAll(`[data-line-id="${lineId}"]`);
            imageLines.forEach(el => {
                if (highlight) {
                    el.classList.add('highlighted');
                } else {
                    el.classList.remove('highlighted');
                }
            });

            // Trigger event to sync with transcription
            if (highlight) {
                props.selectedLine = lineId;
            } else {
                props.selectedLine = null;
            }
        };

        // Click to select line
        element.addEventListener('click', (e) => {
            const lineEl = e.target.closest('[data-line-id]');
            if (lineEl) {
                const lineId = parseInt(lineEl.dataset.lineId);
                trigger('line_clicked', { lineId: lineId });
            }
        });
        """

        super().__init__(
            html_template=html_template,
            css_template=css_template,
            js_on_load=js_on_load,
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
                            "polygon": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            }
        }


class TranscriptionViewer(gr.HTML):
    """Interactive transcription viewer with synchronized highlighting"""

    def __init__(self, **kwargs):
        html_template = """
        <div class="transcription-container">
            ${value.regions.map(region => `
                <div class="transcription-region">
                    ${region.map((line, idx) => `
                        <span class="transcription-line line-${line.id}"
                              data-line-id="${line.id}"
                              onmouseover="window.highlightLine(${line.id}, true)"
                              onmouseout="window.highlightLine(${line.id}, false)">
                            ${line.text}
                        </span><br>
                    `).join('')}
                </div>
                ${region !== value.regions[value.regions.length - 1] ? '<hr class="region-divider">' : ''}
            `).join('')}
        </div>
        """

        css_template = """
        .transcription-container {
            font-size: 1.1rem;
            line-height: 1.8;
            position: sticky;
            top: 20px;
            padding: 1rem;
        }

        .transcription-region {
            margin-bottom: 0.5rem;
        }

        .transcription-line {
            display: inline;
            padding: 2px 0;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .transcription-line:hover {
            background-color: rgba(59, 130, 246, 0.15);
            border-radius: 2px;
        }

        .transcription-line.highlighted {
            background-color: rgba(59, 130, 246, 0.3);
            font-weight: 600;
            border-radius: 2px;
            padding: 2px 4px;
        }

        .region-divider {
            margin: 1rem 0;
            border: none;
            border-top: 2px solid rgba(0, 0, 0, 0.1);
        }
        """

        js_on_load = """
        // Listen for highlights from image viewer
        element.addEventListener('click', (e) => {
            const lineEl = e.target.closest('[data-line-id]');
            if (lineEl) {
                const lineId = parseInt(lineEl.dataset.lineId);
                trigger('line_clicked', { lineId: lineId });
            }
        });

        // Extend global highlight function to also highlight transcription
        const origHighlight = window.highlightLine;
        window.highlightLine = function(lineId, highlight) {
            origHighlight(lineId, highlight);

            // Highlight transcription span
            const transcLines = document.querySelectorAll(`.transcription-line[data-line-id="${lineId}"]`);
            transcLines.forEach(el => {
                if (highlight) {
                    el.classList.add('highlighted');
                } else {
                    el.classList.remove('highlighted');
                }
            });
        };
        """

        super().__init__(
            html_template=html_template,
            css_template=css_template,
            js_on_load=js_on_load,
            **kwargs
        )

    def api_info(self):
        return {
            "type": "object",
            "properties": {
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


def prepare_image_data(collection: Collection, current_page_index: int):
    """Convert collection page to format expected by AnnotatedImageViewer"""
    page = collection[current_page_index]
    lines = list(page.traverse(lambda node: node.is_line()))

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
        ]
    }


def prepare_transcription_data(collection: Collection, current_page_index: int):
    """Convert collection page to format expected by TranscriptionViewer"""
    page = collection[current_page_index]
    regions = page.traverse(
        lambda node: node.children and all(child.is_line() for child in node)
    )

    line_counter = 0
    region_data = []
    for region in regions:
        region_lines = []
        for line in region:
            region_lines.append({
                "id": line_counter,
                "text": line.text
            })
            line_counter += 1
        region_data.append(region_lines)

    return {"regions": region_data}


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
        _("Hover over text regions to see synchronized highlighting between image and transcription. Click to select a line.")
    )

    with gr.Row():
        # Annotated image panel
        with gr.Column(scale=2):
            image = AnnotatedImageViewer(
                label=_("Annotated image"),
                value={"width": 100, "height": 100, "path": "", "lines": []},
            )

            image_caption = gr.Markdown()
            with gr.Row(elem_classes="button-group-viz"):
                left = gr.Button(
                    _("← Previous"), visible=False, interactive=False, scale=0
                )
                right = gr.Button(_("Next →"), visible=False, scale=0)

        # Transcription panel
        with gr.Column(scale=1):
            transcription = TranscriptionViewer(
                label=_("Transcription"),
                value={"regions": []},
            )

    collection = gr.State()
    current_page_index = gr.State(0)

    # Wiring of navigation buttons
    left.click(left_button_click, current_page_index, current_page_index)
    right.click(
        right_button_click, [collection, current_page_index], current_page_index
    )

    # Updates on collection change
    collection.change(
        prepare_image_data,
        inputs=[collection, current_page_index],
        outputs=image
    )
    collection.change(
        prepare_transcription_data,
        inputs=[collection, current_page_index],
        outputs=transcription,
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
        prepare_image_data,
        inputs=[collection, current_page_index],
        outputs=image
    )
    current_page_index.change(
        prepare_transcription_data,
        inputs=[collection, current_page_index],
        outputs=transcription,
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
