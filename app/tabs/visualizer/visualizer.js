// HTR Visualizer JavaScript
// Fully self-contained with internal navigation

(() => {
    const initVisualizer = () => {
        // Check if we have valid data
        if (!props.value || !props.value.pages || props.value.pages.length === 0) {
            setTimeout(initVisualizer, 100);
            return;
        }

        const svgContainer = element.querySelector('.svg-container');
        const transcriptionPanel = element.querySelector('.transcription-panel');
        const pageInfoEl = element.querySelector('#page-info');
        const prevBtn = element.querySelector('#nav-prev-btn');
        const nextBtn = element.querySelector('#nav-next-btn');

        // Internal state
        let currentPageIndex = props.value.currentPageIndex || 0;
        let selectedLineId = null;
        let editedTexts = {};

        // Zoom and pan state using viewBox
        let viewBox = { x: 0, y: 0, width: 0, height: 0 };
        let isPanning = false;
        let isCtrlPressed = false;
        let panStart = { x: 0, y: 0 };

        // Touch gesture state
        let isTouchPanning = false;
        let touchStartDistance = 0;
        let touchStartViewBox = { x: 0, y: 0, width: 0, height: 0 };
        let touchStartCenter = { x: 0, y: 0 };

        // ===== RENDER FUNCTIONS =====
        function renderPage(pageIndex) {
            const page = props.value.pages[pageIndex];
            if (!page) return;

            // Reset zoom/pan
            viewBox = { x: 0, y: 0, width: page.width, height: page.height };

            // Render SVG
            svgContainer.innerHTML = `
                <svg class="image-svg" viewBox="0 0 ${page.width} ${page.height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                    <image height="${page.height}" width="${page.width}" href="/gradio_api/file=${page.path}" />
                    ${page.lines.map((line) => `
                        <a class="textline" data-line-id="${line.id}">
                            <polygon points="${line.polygonPoints}"/>
                        </a>
                    `).join('')}
                </svg>
            `;

            // Render transcription
            transcriptionPanel.innerHTML = page.regions.map((region, regionIdx) => `
                <div class="transcription-region">
                    ${region.map((line) => `
                        <span class="transcription-line"
                              data-line-id="${line.id}"
                              data-original-text="${line.text}">
                            ${line.text}
                        </span><br>
                    `).join('')}
                </div>
                ${regionIdx < page.regions.length - 1 ? '<hr class="region-divider">' : ''}
            `).join('');

            // Update page info
            if (pageInfoEl) {
                pageInfoEl.textContent = `Image ${pageIndex + 1} of ${props.value.totalPages}: ${page.label}`;
            }

            // Update navigation buttons
            if (prevBtn) prevBtn.disabled = pageIndex <= 0;
            if (nextBtn) nextBtn.disabled = pageIndex >= props.value.totalPages - 1;

            // Update zoom level
            updateViewBox();

            // Re-attach event listeners to new elements
            attachLineInteractions();

            // Re-apply edit mode if active
            if (isEditMode) {
                toggleEditMode(true);
            }

            // Clear selection
            selectedLineId = null;
        }

        // Helper to update viewBox and zoom level
        function updateViewBox() {
            const imageSvg = element.querySelector('.image-svg');
            if (!imageSvg) return;

            imageSvg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);

            const page = props.value.pages[currentPageIndex];
            if (!page) return;

            const zoomLevel = Math.round((page.width / viewBox.width) * 100);
            const zoomLevelEl = element.querySelector('.zoom-level');
            if (zoomLevelEl) {
                zoomLevelEl.textContent = `${zoomLevel}%`;
            }
        }

        // ===== NAVIGATION FUNCTIONS =====
        function navigateToPrevious() {
            if (currentPageIndex > 0) {
                currentPageIndex--;
                renderPage(currentPageIndex);
            }
        }

        function navigateToNext() {
            if (currentPageIndex < props.value.totalPages - 1) {
                currentPageIndex++;
                renderPage(currentPageIndex);
            }
        }

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
            }

            selectedLineId = lineId;
        }

        // ===== LINE INTERACTION (Hover & Click) =====
        function attachLineInteractions() {
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
                });
            });
        }

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
                // Store edit with page context
                const editKey = `${currentPageIndex}_${lineId}`;
                editedTexts[editKey] = newText;
            }
        }

        // ===== ZOOM CONTROLS =====
        element.querySelectorAll('.zoom-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                const page = props.value.pages[currentPageIndex];

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
                    const newWidth = Math.min(viewBox.width * zoomFactor, page.width);
                    const newHeight = Math.min(viewBox.height * zoomFactor, page.height);
                    viewBox.x = Math.max(0, centerX - newWidth / 2);
                    viewBox.y = Math.max(0, centerY - newHeight / 2);
                    viewBox.width = newWidth;
                    viewBox.height = newHeight;
                } else if (action === 'reset') {
                    viewBox = { x: 0, y: 0, width: page.width, height: page.height };
                }

                updateViewBox();
            });
        });

        // ===== KEYBOARD CONTROLS =====
        const handleKeyDown = (e) => {
            if (e.ctrlKey || e.metaKey) {
                isCtrlPressed = true;
                svgContainer.classList.add('can-pan');
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

            const page = props.value.pages[currentPageIndex];
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
            viewBox.x = Math.max(0, Math.min(page.width - viewBox.width, viewBox.x));
            viewBox.y = Math.max(0, Math.min(page.height - viewBox.height, viewBox.y));

            updateViewBox();
        });

        // ===== ZOOM WITH MOUSE WHEEL =====
        svgContainer.addEventListener('wheel', (e) => {
            e.preventDefault();

            const page = props.value.pages[currentPageIndex];
            const rect = svgContainer.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const svgX = mouseX * (viewBox.width / rect.width) + viewBox.x;
            const svgY = mouseY * (viewBox.height / rect.height) + viewBox.y;

            const zoomFactor = e.deltaY < 0 ? 0.95 : 1.05;

            const newWidth = viewBox.width * zoomFactor;
            const newHeight = viewBox.height * zoomFactor;

            // Don't zoom out beyond original size
            if (newWidth > page.width || newHeight > page.height) {
                viewBox = { x: 0, y: 0, width: page.width, height: page.height };
                updateViewBox();
                return;
            }

            // Don't zoom in too much (max 10x zoom)
            const minViewBoxSize = page.width / 10;
            if (newWidth < minViewBoxSize || newHeight < minViewBoxSize) {
                return;
            }

            // Calculate new viewBox position to keep mouse point stationary
            viewBox.x = svgX - (svgX - viewBox.x) * zoomFactor;
            viewBox.y = svgY - (svgY - viewBox.y) * zoomFactor;
            viewBox.width = newWidth;
            viewBox.height = newHeight;

            // Constrain to image bounds
            viewBox.x = Math.max(0, Math.min(page.width - viewBox.width, viewBox.x));
            viewBox.y = Math.max(0, Math.min(page.height - viewBox.height, viewBox.y));

            updateViewBox();
        });

        // Helper functions for touch gestures
        function getTouchDistance(touch1, touch2) {
            const dx = touch1.clientX - touch2.clientX;
            const dy = touch1.clientY - touch2.clientY;
            return Math.sqrt(dx * dx + dy * dy);
        }

        function getTouchCenter(touch1, touch2) {
            return {
                x: (touch1.clientX + touch2.clientX) / 2,
                y: (touch1.clientY + touch2.clientY) / 2
            };
        }

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

                const page = props.value.pages[currentPageIndex];
                const currentDistance = getTouchDistance(e.touches[0], e.touches[1]);
                const scaleFactor = touchStartDistance / currentDistance;

                let newWidth = touchStartViewBox.width * scaleFactor;
                let newHeight = touchStartViewBox.height * scaleFactor;

                // Constrain zoom limits
                if (newWidth > page.width || newHeight > page.height) {
                    newWidth = page.width;
                    newHeight = page.height;
                }
                const minViewBoxSize = page.width / 10;
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
                viewBox.x = Math.max(0, Math.min(page.width - viewBox.width, viewBox.x));
                viewBox.y = Math.max(0, Math.min(page.height - viewBox.height, viewBox.y));

                updateViewBox();
            }
        }, { passive: false });

        svgContainer.addEventListener('touchend', (e) => {
            if (e.touches.length < 2) {
                isTouchPanning = false;
            }
        });

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
                const currentValue = props.value || {};
                const newValue = {
                    ...currentValue,
                    edits: editsCopy
                };
                props.value = newValue;

                // Trigger the component's change event to notify Python
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

        // ===== WIRE UP NAVIGATION BUTTONS =====
        if (prevBtn) {
            prevBtn.addEventListener('click', navigateToPrevious);
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', navigateToNext);
        }

        // ===== INITIAL RENDER =====
        renderPage(currentPageIndex);
    };

    // Monitor for prop changes
    let lastTotalPages = props.value?.totalPages;
    setInterval(() => {
        if (props.value?.totalPages && props.value.totalPages !== lastTotalPages) {
            lastTotalPages = props.value.totalPages;
            initVisualizer();
        }
    }, 100);

    // Start initialization
    initVisualizer();
})();
