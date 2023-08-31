class TextRoadmap:
    roadmap = """

    ## Roadmap

    * Continually retrain and update both segmentation och text-recognition models as more training-data becomes available.
    * Train a TrOCR model specialized on swedish historical handwritten text that is initialized with an historical BERT-model trained here at the Swedish National Archives.
    * An open-source HTR-project where it is easy to implement pipelines such as the one shown in the demo, but that is highly modularized, so you can implement different segmentation strategies, implement models trained with a variety of frameworks, and that offers effective ways to evaluate entire pipelines and compare them with each other. Use-cases should not be restricted to running text, but should comprise all types of handwritten archives.
    * Do large scale HTR on handwritten historical archives that are of interest to researchers within the humanities. 
   
    """

    discussion = """
    ## Get in Touch

    If you have suggestions, questions, or would like to discuss our roadmap further, please don't hesitate to reach out.
    Press badge below to open a discussion on HuggingFace.

    <p align="center">
        <a href="https://huggingface.co/spaces/Riksarkivet/htr_demo/discussions">
            <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/open-a-discussion-xl-dark.svg" alt="Badge 1">
        </a>
    </p>"""

    roadmap_image = """  
    <figure>
    <img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/roadmap_image.png" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> """
