### Text-region segmentation

To facilitate the text-line segmentation process, it is advantageous to segment the image into text-regions beforehand. This initial step offers several benefits, including reducing variations in line spacing, eliminating blank areas on the page, establishing a clear reading order, and distinguishing marginalia from the main text. The segmentation model utilized in this process predicts both bounding boxes and masks. Although the model has the capability to predict both, only the masks are utilized for the segmentation tasks of lines and regions. An essential post-processing step involves checking for regions that are contained within other regions. During this step, only the containing region is retained, while the contained region is discarded. This ensures that the final segmented text-regions are accurate and devoid of overlapping or redundant areas. This ensures that there’s no duplicate text-regions sent to the text-recognition model.

<figure>
<img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_region.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
</figure>
