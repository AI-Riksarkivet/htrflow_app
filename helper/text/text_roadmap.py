class TextRoadmap:
    roadmap = """
    ## Roadmap
    
    - **Model Training & Updates**
      - Continually retrain and update both segmentation and text-recognition models as more training data becomes available.
    
    - **Specialized TrOCR Model**
      - Train a TrOCR model specialized on Swedish historical handwritten text.
      - Initialize with a historical BERT-model trained at the Swedish National Archives.
    
    - **Open-source HTR Project**
      - Develop an easy-to-implement pipeline like the demo.
      - Ensure high modularity: 
        - Different segmentation strategies.
        - Integration of models from various frameworks.
        - Effective evaluation methods for entire pipelines and their comparisons.
      - Broad use-cases: Not just running text, but all types of handwritten archives.
    
    - **Large Scale HTR**
      - Conduct large scale HTR on handwritten historical archives of interest to humanities researchers.

    - **Rest APIs**
      - Serve model through inference APIs 
      
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
