class TextAbout:
    # About text
    intro_text = """

    ## Introduction
    The Swedish National Archives introduces a demonstrational end-to-end HTR (Handwritten Text Recognition) pipeline. This pipeline comprises two instance segmentation models: one designated for segmenting text-regions and another for isolating text-lines within these regions, coupled with an HTR model for image-to-text transcription. The objective of this project is to establish a generic pipeline capable of processing running-text documents spanning from 1600 to 1900.

    ## Usage
    It's crucial to emphasize that this application serves primarily for demonstration purposes, aimed at showcasing the various models employed in the current workflow for processing documents with running-text. <br>

    For an insight into the upcoming features we are working on:
    -  Navigate to the > **About** > **Roadmap**. 

    To understand how to utilize this application through a REST API, self-host or via Docker, 
    - Navigate to the > **About** > **How to Use** > **API & Duplicate for Private Use**.
    
    """

    ## The Pipeline in Overview
    pipeline_overview_text = """
    ## The Pipeline in Overview
    
    The steps in the pipeline can be seen below as follows:
    """

    binarization = """

    ### Binarization
    The reason for binarizing the images before processing them is that we want the models to generalize as well as possible. By training on only binarized images and by binarizing images before running them through the pipeline, we take the target domain closer to the training domain, and ruduce negative effects of background variation, background noise etc., on the final results. The pipeline implements a simple adaptive thresholding algorithm for binarization.
    <figure>
    <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_bin.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> 

"""
    text_region_segment = """    
    ### Text-region segmentation
    To facilitate the text-line segmentation process, it is advantageous to segment the image into text-regions beforehand. This initial step offers several benefits, including reducing variations in line spacing, eliminating blank areas on the page, establishing a clear reading order, and distinguishing marginalia from the main text. The segmentation model utilized in this process predicts both bounding boxes and masks. Although the model has the capability to predict both, only the masks are utilized for the segmentation tasks of lines and regions. An essential post-processing step involves checking for regions that are contained within other regions. During this step, only the containing region is retained, while the contained region is discarded. This ensures that the final segmented text-regions are accurate and devoid of overlapping or redundant areas.
    <figure>
    <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_region.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> 
"""
    text_line_segmentation = """
    ### Text-line segmentation

    This is also an RTMDet model that's trained on extracting text-lines from cropped text-regions within an image. The same post-processing on the instance segmentation masks is done here as in the text-region segmentation step.
    <figure>
    <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_line.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> 
"""
    text_htr = """
    ### HTR

    For the text-recognition a SATRN model was trained with mmocr on approximately one million handwritten text-line images ranging from 1600 to 1900. It was trained on a wide variety of archival material to make it generalize as well as possible. See below for detailed evaluation results, and also some finetuning experiments.
    <figure>
    <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_htr.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> 
    """

    text_src_code_data_models = """
    ## Source Code
    Please fork and leave a star on Github if you like it! The code for this project can be found here:
    - [Github](https://github.com/Borg93/htr_gradio)
    **Note**: We will in the future package all of the code for mass htr (batch inference on multi-GPU setup), but the code is still work in progress.

    ## The Dataset
    For a glimpse into the kind of data we're working with, you can explore our sample test data on Hugging Face:
    - [HuggingFace Dataset Card](https://huggingface.co/datasets/Riksarkivet/test_images_demo)
    **Note**: This is just a sample. The complete training dataset will be released in the future.

    ## The Models
    The models within this pipeline will be subject to continual retraining and updates as more data becomes accessible. For detailed information about all the models used in this project, please refer to the model cards available on Hugging Face:
    - [Riksarkivet/rtmdet_regions](https://huggingface.co/Riksarkivet/rtmdet_regions)
    - [Riksarkivet/rtmdet_lines](https://huggingface.co/Riksarkivet/rtmdet_lines)
    - [Riksarkivet/satrn_htr](https://huggingface.co/https://huggingface.co/Riksarkivet/satrn_htr)
    """


if __name__ == "__main__":
    pass
