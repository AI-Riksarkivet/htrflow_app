// HTR Visualizer JavaScript
// Interactive viewer with zoom, pan, edit mode, and synchronized highlighting

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

        // Edit mode state
        let isEditMode = false;
        let editedTexts = {};  // Store edited line texts

        // Set initial viewBox
        imageSvg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);

        // Helper to update viewBox and zoom level
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

        // ===== ZOOM CONTROLS =====
        element.querySelectorAll('.zoom-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;

                if (action === 'zoom-in') {
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
                    viewBox = { x: 0, y: 0, width: svgWidth, height: svgHeight };
                }

                updateViewBox();
            });
        });

        // ===== KEYBOARD CONTROLS =====
        const handleKeyDown = (e) => {
            if (e.ctrlKey || e.metaKey) {
                isCtrlPressed = true;
                svgContainer.classList.add('can-pan');
                // Clear hover highlights when entering pan mode
                element.querySelectorAll('.highlighted').forEach(el => {
                    el.classList.remove('highlighted');
                });
            }
        };

        const handleKeyUp = (e) => {
            if (!e.ctrlKey && !e.metaKey) {
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

        // ===== PAN FUNCTIONALITY (Ctrl+Drag) =====
        svgContainer.addEventListener('mousedown', (e) => {
            if (!e.ctrlKey && !e.metaKey) return;
            if (e.target.closest('.textline')) return;

            isPanning = true;
            svgContainer.classList.add('panning');

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
            // Update cursor state
            if (e.ctrlKey || e.metaKey) {
                isCtrlPressed = true;
                if (!isPanning) svgContainer.classList.add('can-pan');
            } else {
                isCtrlPressed = false;
                if (!isPanning) svgContainer.classList.remove('can-pan');
            }

            if (!isPanning) return;
            e.preventDefault();

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

        // ===== ZOOM WITH MOUSE WHEEL =====
        svgContainer.addEventListener('wheel', (e) => {
            e.preventDefault();

            const rect = svgContainer.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const svgX = mouseX * (viewBox.width / rect.width) + viewBox.x;
            const svgY = mouseY * (viewBox.height / rect.height) + viewBox.y;

            const zoomFactor = e.deltaY < 0 ? 0.95 : 1.05;

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

        // ===== TOUCH GESTURES (Mobile) =====
        svgContainer.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                e.preventDefault();
                isTouchPanning = true;

                touchStartDistance = getTouchDistance(e.touches[0], e.touches[1]);
                touchStartViewBox = { ...viewBox };

                const centerScreen = getTouchCenter(e.touches[0], e.touches[1]);
                const rect = svgContainer.getBoundingClientRect();
                const relX = centerScreen.x - rect.left;
                const relY = centerScreen.y - rect.top;

                touchStartCenter.x = relX * (viewBox.width / rect.width) + viewBox.x;
                touchStartCenter.y = relY * (viewBox.height / rect.height) + viewBox.y;
            } else if (e.touches.length === 1) {
                isTouchPanning = false;
            }
        }, { passive: false });

        svgContainer.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && isTouchPanning) {
                e.preventDefault();

                const currentDistance = getTouchDistance(e.touches[0], e.touches[1]);
                const scaleFactor = touchStartDistance / currentDistance;

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

                const centerScreen = getTouchCenter(e.touches[0], e.touches[1]);
                const rect = svgContainer.getBoundingClientRect();
                const relX = centerScreen.x - rect.left;
                const relY = centerScreen.y - rect.top;

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

        // ===== HIGHLIGHT & SELECT FUNCTIONS =====
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

        function selectLine(lineId, clickedFromTranscription = false) {
            // Clear previous selection
            element.querySelectorAll('.selected').forEach(el => {
                el.classList.remove('selected');
            });

            // Set new selection
            if (lineId !== null) {
                const elements = element.querySelectorAll(`[data-line-id="${lineId}"]`);
                elements.forEach(el => el.classList.add('selected'));

                // Scroll transcription to show selected line
                const transcriptionLine = transcriptionPanel.querySelector(`.transcription-line[data-line-id="${lineId}"]`);
                if (transcriptionLine && !clickedFromTranscription) {
                    setTimeout(() => {
                        transcriptionLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 50);
                }

                // Note: Auto-scroll to polygon is disabled (we use viewBox for zoom/pan)
            }

            selectedLineId = lineId;
            props.selectedLine = lineId;
        }

        // ===== LINE INTERACTION (Hover & Click) =====
        element.querySelectorAll('[data-line-id]').forEach(lineEl => {
            const lineId = lineEl.dataset.lineId;
            const isTranscriptionLine = lineEl.classList.contains('transcription-line');

            // Hover highlighting (disabled when Ctrl is pressed)
            lineEl.addEventListener('mouseenter', (e) => {
                if (!isCtrlPressed && !e.ctrlKey && !e.metaKey) {
                    highlightLine(lineId, true);
                }
            });

            lineEl.addEventListener('mouseleave', (e) => {
                if (!isCtrlPressed && !e.ctrlKey && !e.metaKey) {
                    highlightLine(lineId, false);
                }
            });

            // Click selection (disabled when Ctrl is pressed)
            lineEl.addEventListener('click', (e) => {
                if (isCtrlPressed || e.ctrlKey || e.metaKey) return;
                e.stopPropagation();
                const newSelection = selectedLineId === lineId ? null : lineId;
                selectLine(newSelection, isTranscriptionLine);
                trigger('line_selected', { lineId: newSelection });
            });
        });

        // ===== EDIT MODE FUNCTIONALITY =====
        function toggleEditMode(enabled) {
            isEditMode = enabled;
            const transcriptionLines = element.querySelectorAll('.transcription-line');

            transcriptionLines.forEach(lineEl => {
                if (enabled) {
                    lineEl.setAttribute('contenteditable', 'true');
                    lineEl.setAttribute('spellcheck', 'false');
                    lineEl.addEventListener('blur', handleTextEdit);
                    lineEl.addEventListener('input', handleTextInput);
                } else {
                    lineEl.setAttribute('contenteditable', 'false');
                    lineEl.removeEventListener('blur', handleTextEdit);
                    lineEl.removeEventListener('input', handleTextInput);
                    lineEl.classList.remove('edited');
                }
            });
        }

        function handleTextInput(e) {
            const lineEl = e.target;
            const originalText = lineEl.dataset.originalText;
            const currentText = lineEl.textContent.trim();

            if (currentText !== originalText) {
                lineEl.classList.add('edited');
            } else {
                lineEl.classList.remove('edited');
            }
        }

        function handleTextEdit(e) {
            const lineEl = e.target;
            const lineId = lineEl.dataset.lineId;
            const newText = lineEl.textContent.trim();
            const originalText = lineEl.dataset.originalText;

            if (newText !== originalText) {
                editedTexts[lineId] = newText;
            }
        }

        // ===== WIRE UP INTERNAL EDIT CONTROLS =====
        const editToggle = element.querySelector('#edit-mode-toggle');
        const saveBtn = element.querySelector('#save-edits-btn');

        if (editToggle && saveBtn) {
            // Toggle edit mode and show/hide save button
            editToggle.addEventListener('change', (e) => {
                const isEnabled = e.target.checked;
                toggleEditMode(isEnabled);
                saveBtn.style.display = isEnabled ? 'inline-block' : 'none';

                // Clear edits when disabling edit mode
                if (!isEnabled) {
                    editedTexts = {};
                    // Remove 'edited' class from all lines
                    element.querySelectorAll('.transcription-line').forEach(line => {
                        line.classList.remove('edited');
                    });
                }
            });

            // Handle save button click
            saveBtn.addEventListener('click', () => {
                // Create a deep copy of edits to avoid reference issues
                const editsCopy = JSON.parse(JSON.stringify(editedTexts));

                // Store edits in the component's value so Python can access it
                // Create a new value object with the edits
                const currentValue = props.value || {};
                const newValue = {
                    ...currentValue,  // Spread existing properties
                    edits: editsCopy  // Add edits as a new property
                };
                props.value = newValue;

                // Trigger the component's change event to notify Python
                // This will fire the visualizer_component.change() listener in Python
                trigger('change');

                // Disable edit mode after saving
                editToggle.checked = false;
                toggleEditMode(false);
                saveBtn.style.display = 'none';

                // Clear local edits and remove 'edited' styling
                editedTexts = {};
                element.querySelectorAll('.transcription-line').forEach(line => {
                    line.classList.remove('edited');
                });
            });
        }
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
