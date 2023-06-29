class TextAbout:
    # About text
    intro_and_pipeline_overview_text = """

    ## Introduction
    The Swedish National Archives presents an end-to-end HTR-pipeline consisting of two RTMDet instance segmentation models, trained with MMDetection, one for segmenting text-regions, and one for segmenting text-lines within these regions, and one SATRN HTR-model trained with MMOCR. The aim is for a generic pipline for running-text documents ranging from 1600 to 1900. We will retrain and update the models continually as more data becomes avaialable. Feel free to try out the pipline yourself in our interactive demo (reference).

    ## The Pipeline in Overview

    The steps in the pipeline are as follows:
    """

    binarization = """

    ### Binarization
    The reason for binarizing the images before processing them is that we want the models to generalize as well as possible. 
    By training on only binarized images and by binarizing images before running them through the pipeline, we take the target domain closer to the training domain, and ruduce negative effects of background variation, background noise etc., on the final results. 
    The pipeline implements a simple adaptive thresholding algorithm for binarization.
"""
    text_region_segment = """    
    ### Text-region segmentation
    To facilitate the text-line segmentation process, it is advantageous to segment the image into text-regions beforehand. This initial step offers several benefits, including reducing variations in line spacing, eliminating blank areas on the page, establishing a clear reading order, and distinguishing marginalia from the main text.
    The segmentation model utilized in this process predicts both bounding boxes and masks. Although the model has the capability to predict both, only the masks are utilized for the segmentation tasks of lines and regions.
    An essential post-processing step involves checking for regions that are contained within other regions. During this step, only the containing region is retained, while the contained region is discarded. This ensures that the final segmented text-regions are accurate and devoid of overlapping or redundant areas.
"""
    text_line_segmentation = """
    ### Text-line segmentation

    This is also an RTMDet model that's trained on extracting text-lines from cropped text-regions within an image. 
    The same post-processing on the instance segmentation masks is done here as in the text-region segmentation step.
"""
    text_htr = """
    ### HTR

    For the text-recognition a SATRN model (reference) was trained with mmocr on approximately one million handwritten text-line images ranging from 1600 to 1900. 
    It was trained on a wide variety of archival material to make it generalize as well as possible. See below for detailed evaluation results, and also some finetuning experiments.
    """

    text_data = """
    ## The Data
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    """

    filler_text_data = """
    ## &nbsp;
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    """

    text_models = """
    ## The Models
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    """

    text_models_region = """
    
    ### Text-Region Segmentation
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

    text_models_lines = """
    ### Text-Line Segmentation
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    """

    text_models_htr = """
    ### HTR
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    """
