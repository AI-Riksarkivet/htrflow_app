import gradio as gr
from htrflow.volume.volume import Collection
from gradio_i18n import gettext as _


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
                <div class="zoom-controls">
                    <button class="zoom-btn" data-action="zoom-in" title="Zoom In">+</button>
                    <button class="zoom-btn" data-action="zoom-out" title="Zoom Out">−</button>
                    <button class="zoom-btn" data-action="reset" title="Reset View">⟲</button>
                    <span class="zoom-level">100%</span>
                </div>
                <div class="svg-container">
                    <svg class="image-svg" viewBox="0 0 ${value.width} ${value.height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                        <image height="${value.height}" width="${value.width}" href="/gradio_api/file=${value.path}" />
                        ${value.lines.map((line) => `
                            <a class="textline" data-line-id="${line.id}">
                                <polygon points="${line.polygonPoints}"/>
                            </a>
                        `).join('')}
                    </svg>
                </div>
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
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border-color-primary);
            border-radius: var(--radius-lg);
            background: var(--background-fill-primary);
            box-sizing: border-box;
        }

        .zoom-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 10;
            display: flex;
            gap: 4px;
            background: var(--background-fill-secondary);
            padding: 4px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color-primary);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .zoom-btn {
            width: 32px;
            height: 32px;
            border: none;
            background: var(--button-secondary-background-fill);
            color: var(--button-secondary-text-color);
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .zoom-btn:hover {
            background: var(--button-secondary-background-fill-hover);
            transform: scale(1.05);
        }

        .zoom-btn:active {
            transform: scale(0.95);
        }

        .zoom-level {
            padding: 0 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--body-text-color);
            display: flex;
            align-items: center;
            min-width: 50px;
            justify-content: center;
        }

        .svg-container {
            width: 100%;
            height: 100%;
            overflow: hidden;
            cursor: default;
            position: relative;
        }

        .svg-container.can-pan {
            cursor: grab;
        }

        .svg-container.panning {
            cursor: grabbing;
        }

        .image-svg {
            width: 100%;
            height: 100%;
            display: block;
        }

        .textline polygon {
            fill: transparent;
            stroke: var(--color-accent);
            stroke-width: 3;
            stroke-opacity: 0.3;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .textline:hover polygon,
        .textline.highlighted polygon {
            fill: var(--color-accent);
            fill-opacity: 0.25;
            stroke-width: 5;
            stroke-opacity: 0.5;
        }

        .textline.selected polygon {
            fill: var(--color-accent);
            fill-opacity: 0.4;
            stroke: var(--color-accent);
            stroke-width: 6;
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
        (() => {
            const initVisualizer = () => {
                // Check if we have valid data
                if (!props.value || !props.value.path || props.value.lines.length === 0) {
                    setTimeout(initVisualizer, 100);
                    return;
                }

                const imagePanel = element.querySelector('.image-panel');
                const svgContainer = element.querySelector('.svg-container');
                const imageSvg = element.querySelector('.image-svg');
                const transcriptionPanel = element.querySelector('.transcription-panel');

                let selectedLineId = null;

        // Zoom and pan state using viewBox
        const svgWidth = props.value.width;
        const svgHeight = props.value.height;
        let viewBox = { x: 0, y: 0, width: svgWidth, height: svgHeight };
        let isPanning = false;
        let isCtrlPressed = false;
        let panStart = { x: 0, y: 0 };

        // Touch gesture state
        let isTouchPanning = false;
        let touchStartDistance = 0;
        let touchStartViewBox = { x: 0, y: 0, width: 0, height: 0 };
        let touchStartCenter = { x: 0, y: 0 };

        // Set initial viewBox
        imageSvg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);

        // Helper to update viewBox
        function updateViewBox() {
            imageSvg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);

            // Update zoom level indicator
            const zoomLevel = Math.round((svgWidth / viewBox.width) * 100);
            const zoomLevelEl = element.querySelector('.zoom-level');
            if (zoomLevelEl) {
                zoomLevelEl.textContent = `${zoomLevel}%`;
            }
        }

        // Helper to get distance between two touch points
        function getTouchDistance(touch1, touch2) {
            const dx = touch1.clientX - touch2.clientX;
            const dy = touch1.clientY - touch2.clientY;
            return Math.sqrt(dx * dx + dy * dy);
        }

        // Helper to get center point between two touches
        function getTouchCenter(touch1, touch2) {
            return {
                x: (touch1.clientX + touch2.clientX) / 2,
                y: (touch1.clientY + touch2.clientY) / 2
            };
        }

        // Zoom controls
        element.querySelectorAll('.zoom-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;

                if (action === 'zoom-in') {
                    // Zoom in by reducing viewBox size (zoom toward center)
                    const zoomFactor = 0.85;
                    const centerX = viewBox.x + viewBox.width / 2;
                    const centerY = viewBox.y + viewBox.height / 2;
                    const newWidth = viewBox.width * zoomFactor;
                    const newHeight = viewBox.height * zoomFactor;
                    viewBox.x = centerX - newWidth / 2;
                    viewBox.y = centerY - newHeight / 2;
                    viewBox.width = newWidth;
                    viewBox.height = newHeight;
                } else if (action === 'zoom-out') {
                    // Zoom out by increasing viewBox size
                    const zoomFactor = 1.15;
                    const centerX = viewBox.x + viewBox.width / 2;
                    const centerY = viewBox.y + viewBox.height / 2;
                    const newWidth = Math.min(viewBox.width * zoomFactor, svgWidth);
                    const newHeight = Math.min(viewBox.height * zoomFactor, svgHeight);
                    viewBox.x = Math.max(0, centerX - newWidth / 2);
                    viewBox.y = Math.max(0, centerY - newHeight / 2);
                    viewBox.width = newWidth;
                    viewBox.height = newHeight;
                } else if (action === 'reset') {
                    // Reset to original viewBox
                    viewBox = { x: 0, y: 0, width: svgWidth, height: svgHeight };
                }

                updateViewBox();
            });
        });

        // Show pan cursor when Ctrl is held
        const handleKeyDown = (e) => {
            if (e.ctrlKey || e.metaKey) {
                console.log('Ctrl pressed, isCtrlPressed =', true);
                isCtrlPressed = true;
                svgContainer.classList.add('can-pan');

                // Clear any existing hover highlights when entering pan mode
                element.querySelectorAll('.highlighted').forEach(el => {
                    el.classList.remove('highlighted');
                });
            }
        };

        const handleKeyUp = (e) => {
            if (!e.ctrlKey && !e.metaKey) {
                console.log('Ctrl released, isCtrlPressed =', false);
                isCtrlPressed = false;
                svgContainer.classList.remove('can-pan');
                if (isPanning) {
                    isPanning = false;
                    svgContainer.classList.remove('panning');
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);

        // Pan functionality with Ctrl+drag
        svgContainer.addEventListener('mousedown', (e) => {
            console.log('mousedown - isCtrlPressed:', isCtrlPressed, 'e.ctrlKey:', e.ctrlKey, 'e.metaKey:', e.metaKey);
            // Only pan if Ctrl/Cmd is held
            if (!e.ctrlKey && !e.metaKey) {
                console.log('Ctrl not held, ignoring pan');
                return;
            }
            // Don't pan if clicking on a text line
            if (e.target.closest('.textline')) {
                console.log('Clicked on textline, ignoring pan');
                return;
            }

            console.log('Starting pan');
            isPanning = true;
            svgContainer.classList.add('panning');

            // Get SVG point from mouse position
            const rect = svgContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            panStart.x = x * (viewBox.width / rect.width) + viewBox.x;
            panStart.y = y * (viewBox.height / rect.height) + viewBox.y;

            e.preventDefault();
        });

        svgContainer.addEventListener('mouseleave', () => {
            isPanning = false;
            svgContainer.classList.remove('panning');
        });

        svgContainer.addEventListener('mouseup', () => {
            isPanning = false;
            svgContainer.classList.remove('panning');
        });

        svgContainer.addEventListener('mousemove', (e) => {
            // Update cursor and Ctrl state
            if (e.ctrlKey || e.metaKey) {
                isCtrlPressed = true;
                if (!isPanning) svgContainer.classList.add('can-pan');
            } else {
                isCtrlPressed = false;
                if (!isPanning) svgContainer.classList.remove('can-pan');
            }

            if (!isPanning) return;
            e.preventDefault();

            // Calculate pan in SVG coordinates
            const rect = svgContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const svgX = x * (viewBox.width / rect.width) + viewBox.x;
            const svgY = y * (viewBox.height / rect.height) + viewBox.y;

            const dx = svgX - panStart.x;
            const dy = svgY - panStart.y;

            viewBox.x -= dx;
            viewBox.y -= dy;

            // Constrain to image bounds
            viewBox.x = Math.max(0, Math.min(svgWidth - viewBox.width, viewBox.x));
            viewBox.y = Math.max(0, Math.min(svgHeight - viewBox.height, viewBox.y));

            updateViewBox();
        });

        // Zoom with mouse wheel (zoom toward cursor position)
        svgContainer.addEventListener('wheel', (e) => {
            e.preventDefault();

            // Get mouse position in SVG coordinates
            const rect = svgContainer.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const svgX = mouseX * (viewBox.width / rect.width) + viewBox.x;
            const svgY = mouseY * (viewBox.height / rect.height) + viewBox.y;

            // Calculate zoom factor
            const zoomFactor = e.deltaY < 0 ? 0.95 : 1.05;

            // Calculate new viewBox dimensions
            const newWidth = viewBox.width * zoomFactor;
            const newHeight = viewBox.height * zoomFactor;

            // Don't zoom out beyond original size
            if (newWidth > svgWidth || newHeight > svgHeight) {
                viewBox = { x: 0, y: 0, width: svgWidth, height: svgHeight };
                updateViewBox();
                return;
            }

            // Don't zoom in too much (max 10x zoom)
            const minViewBoxSize = svgWidth / 10;
            if (newWidth < minViewBoxSize || newHeight < minViewBoxSize) {
                return;
            }

            // Calculate new viewBox position to keep mouse point stationary
            viewBox.x = svgX - (svgX - viewBox.x) * zoomFactor;
            viewBox.y = svgY - (svgY - viewBox.y) * zoomFactor;
            viewBox.width = newWidth;
            viewBox.height = newHeight;

            // Constrain to image bounds
            viewBox.x = Math.max(0, Math.min(svgWidth - viewBox.width, viewBox.x));
            viewBox.y = Math.max(0, Math.min(svgHeight - viewBox.height, viewBox.y));

            updateViewBox();
        });

        // Touch gesture support for mobile
        svgContainer.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                // Two-finger gesture - prevent default and start pinch/pan
                e.preventDefault();
                isTouchPanning = true;

                // Store initial touch distance and viewBox for pinch zoom
                touchStartDistance = getTouchDistance(e.touches[0], e.touches[1]);
                touchStartViewBox = { ...viewBox };

                // Store center point in screen coordinates
                const centerScreen = getTouchCenter(e.touches[0], e.touches[1]);
                const rect = svgContainer.getBoundingClientRect();
                const relX = centerScreen.x - rect.left;
                const relY = centerScreen.y - rect.top;

                // Convert to SVG coordinates
                touchStartCenter.x = relX * (viewBox.width / rect.width) + viewBox.x;
                touchStartCenter.y = relY * (viewBox.height / rect.height) + viewBox.y;
            } else if (e.touches.length === 1) {
                // Single touch - allow normal interaction (selection)
                isTouchPanning = false;
            }
        }, { passive: false });

        svgContainer.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && isTouchPanning) {
                e.preventDefault();

                // Calculate new distance and zoom factor
                const currentDistance = getTouchDistance(e.touches[0], e.touches[1]);
                const scaleFactor = touchStartDistance / currentDistance;

                // Calculate new viewBox dimensions
                let newWidth = touchStartViewBox.width * scaleFactor;
                let newHeight = touchStartViewBox.height * scaleFactor;

                // Constrain zoom limits
                if (newWidth > svgWidth || newHeight > svgHeight) {
                    newWidth = svgWidth;
                    newHeight = svgHeight;
                }
                const minViewBoxSize = svgWidth / 10;
                if (newWidth < minViewBoxSize || newHeight < minViewBoxSize) {
                    return;
                }

                // Get current center point in screen coordinates
                const centerScreen = getTouchCenter(e.touches[0], e.touches[1]);
                const rect = svgContainer.getBoundingClientRect();
                const relX = centerScreen.x - rect.left;
                const relY = centerScreen.y - rect.top;

                // Calculate pan offset from initial center
                const screenDx = centerScreen.x - (touchStartCenter.x - touchStartViewBox.x) * (rect.width / touchStartViewBox.width) - rect.left;
                const screenDy = centerScreen.y - (touchStartCenter.y - touchStartViewBox.y) * (rect.height / touchStartViewBox.height) - rect.top;

                // Update viewBox to zoom toward pinch center
                viewBox.width = newWidth;
                viewBox.height = newHeight;
                viewBox.x = touchStartCenter.x - (relX * (viewBox.width / rect.width));
                viewBox.y = touchStartCenter.y - (relY * (viewBox.height / rect.height));

                // Constrain to image bounds
                viewBox.x = Math.max(0, Math.min(svgWidth - viewBox.width, viewBox.x));
                viewBox.y = Math.max(0, Math.min(svgHeight - viewBox.height, viewBox.y));

                updateViewBox();
            }
        }, { passive: false });

        svgContainer.addEventListener('touchend', (e) => {
            if (e.touches.length < 2) {
                isTouchPanning = false;
            }
        });

        // Highlight function for hover (bidirectional)
        function highlightLine(lineId, isHovering) {
            const allElements = element.querySelectorAll(`[data-line-id="${lineId}"]`);
            allElements.forEach(el => {
                if (isHovering) {
                    el.classList.add('highlighted');
                } else {
                    el.classList.remove('highlighted');
                }
            });
        }

        // Select function for click (bidirectional)
        function selectLine(lineId, clickedFromTranscription = false) {
            // Clear previous selection
            element.querySelectorAll('.selected').forEach(el => {
                el.classList.remove('selected');
            });

            // Set new selection
            if (lineId !== null) {
                const elements = element.querySelectorAll(`[data-line-id="${lineId}"]`);
                elements.forEach(el => el.classList.add('selected'));

                // Always scroll transcription to show selected line when clicking from image
                const transcriptionLine = transcriptionPanel.querySelector(`.transcription-line[data-line-id="${lineId}"]`);
                if (transcriptionLine && !clickedFromTranscription) {
                    setTimeout(() => {
                        transcriptionLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 50);
                }

                // Always scroll image to show selected polygon when clicking from transcription
                const imageLine = svgContainer.querySelector(`.textline[data-line-id="${lineId}"]`);
                if (imageLine && clickedFromTranscription) {
                    const polygon = imageLine.querySelector('polygon');
                    if (polygon) {
                        setTimeout(() => {
                            // Get bounding box of polygon and scroll to it
                            const bbox = polygon.getBBox();
                            const containerRect = svgContainer.getBoundingClientRect();
                            const scale = currentZoom;

                            // Calculate center position with zoom applied
                            const centerX = (bbox.x + bbox.width / 2) * scale;
                            const centerY = (bbox.y + bbox.height / 2) * scale;

                            // Scroll to center the polygon
                            svgContainer.scrollTo({
                                left: centerX - containerRect.width / 2,
                                top: centerY - containerRect.height / 2,
                                behavior: 'smooth'
                            });
                        }, 50);
                    }
                }
            }

            selectedLineId = lineId;
            props.selectedLine = lineId;
        }

        // Add hover and click listeners to all lines
        element.querySelectorAll('[data-line-id]').forEach(lineEl => {
            const lineId = lineEl.dataset.lineId;
            const isImageLine = lineEl.classList.contains('textline');
            const isTranscriptionLine = lineEl.classList.contains('transcription-line');

            // Hover highlighting (disabled when Ctrl is pressed)
            lineEl.addEventListener('mouseenter', (e) => {
                console.log('mouseenter - isCtrlPressed:', isCtrlPressed, 'e.ctrlKey:', e.ctrlKey);
                if (!isCtrlPressed && !e.ctrlKey && !e.metaKey) {
                    highlightLine(lineId, true);
                } else {
                    console.log('Skipping highlight - Ctrl is pressed');
                }
            });

            lineEl.addEventListener('mouseleave', (e) => {
                console.log('mouseleave - isCtrlPressed:', isCtrlPressed);
                if (!isCtrlPressed && !e.ctrlKey && !e.metaKey) {
                    highlightLine(lineId, false);
                }
            });

            // Click selection (disabled when Ctrl is pressed)
            lineEl.addEventListener('click', (e) => {
                console.log('click - isCtrlPressed:', isCtrlPressed, 'e.ctrlKey:', e.ctrlKey);
                if (isCtrlPressed || e.ctrlKey || e.metaKey) {
                    console.log('Skipping click - Ctrl is pressed');
                    return;
                }
                e.stopPropagation();
                const newSelection = selectedLineId === lineId ? null : lineId;
                selectLine(newSelection, isTranscriptionLine);
                trigger('line_selected', { lineId: newSelection });
            });
        });
        };

        // Monitor for prop changes
        let lastPath = props.value?.path;
        setInterval(() => {
            if (props.value?.path && props.value.path !== lastPath) {
                lastPath = props.value.path;
                initVisualizer();
            }
        }, 100);

        // Start initialization
        initVisualizer();
    })();
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
        _("visualizer_description")
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
