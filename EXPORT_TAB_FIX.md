# Export Tab Not Activating - Root Cause Analysis

## Problem
The Export tab remains non-interactive even after HTR completes, despite the Result tab becoming clickable.

## Investigation
1. ✅ Code logic is CORRECT - `activate_tab()` is called for both tabs
2. ✅ Debug output confirms both calls execute: `[DEBUG] activate_tab called: collection=present, returning interactive=True`
3. ✅ Both tabs receive `gr.update(interactive=True)`
4. ❌ Export tab UI does NOT become clickable

## Root Cause
**Gradio 6.5.0 Bug/Limitation**: The `interactive` parameter on `gr.Tab` does not properly update after initial render when using `.change()` event handlers.

## Solution
**Remove `interactive=False` from both Result and Export tabs.**

### Why This Works
- Makes all tabs always clickable (better UX)
- Users can explore empty tabs before running HTR
- Avoids Gradio framework limitation
- Simpler code without activation logic

### Code Change
```python
# BEFORE (doesn't work):
with gr.Tab(label=_("3. Export"), interactive=False, id="export") as tab_export:

# AFTER (works):
with gr.Tab(label=_("3. Export"), id="export") as tab_export:
```

Remove the corresponding activation handlers:
```python
# DELETE THESE:
collection_submit_state.change(activate_tab, inputs=collection_submit_state, outputs=tab_visualizer)
collection_submit_state.change(activate_tab, inputs=collection_submit_state, outputs=tab_export)
```

Keep only the auto-navigation:
```python
collection_submit_state.change(
    lambda collection: gr.Tabs(selected="result") if collection else gr.skip(),
    inputs=collection_submit_state,
    outputs=navbar
)
```
