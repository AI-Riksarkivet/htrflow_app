class TextRoadmap:
    roadmap = """
    ## Roadmap

    #### &#x2611; Release Model on HuggingFace
      - Continually retrain and update both segmentation and text-recognition models as more training data becomes available.

    #### &#x2610; Release Training and Eval data on HuggingFace

    #### &#x2610; Specialized TrOCR Model
      - Train a TrOCR model specialized on Swedish historical handwritten text.
      - Initialize with a historical BERT-model trained at the Swedish National Archives.
    
    #### &#x2610; Open-source and package HTR-pipeline for mass HTR
      - Develop an easy-to-implement pipeline like the demo.
      - Ensure high modularity: 
        - Different segmentation strategies.
        - Integration of models from various frameworks.
        - Effective evaluation methods for entire pipelines and their comparisons.
      - Broad use-cases: Not just running text, but all types of handwritten archives.

    #### &#x2610; Inference Endpoints
      - Serve model through inference APIs / Rest APIs with dedicated hardware.

    """

    changelog = """

## App Changelog

### [0.0.1] - 2023-10-19

#### Added

- Stepwise feature > Explore results > New Text diff and CER components

#### Fixed

- ..

#### Changed

- Layout in both Fast track and Stepwise to improve the UX

### Removed

- ..

    
"""

    roadmap_image = """  
    <figure>
    <img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/roadmap_image_2.png" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
    </figure> """

    text_contribution = """
## Project Contributions

We extend our deepest gratitude to the individuals and organizations who have made this project possible through their invaluable contributions, especially in providing datasets for training the models. Their generosity and collaboration have significantly propelled the project forward.

### Datasets Contributors

- [Name/Organization]: Provided [Name of Dataset] which was instrumental in training [Specify Model].
- [Name/Organization]: Contributed [Name of Dataset] that greatly enhanced the performance of [Specify Model].
- [Name/Organization]: Generously shared [Name of Dataset] enabling us to refine [Specify Model].
- ... (continue listing contributors as necessary)

### Other Contributions

- [Name/Organization]: For [description of contribution, e.g., code, testing, design].
- ... (continue listing contributors as necessary)

### Special Mentions

- ... (mention any other individuals/organizations that played a significant role)

We are immensely thankful for the collective effort and dedication that has significantly contributed to the progress of this project. The open collaboration and sharing of resources underscore the community’s commitment to advancing the field.

For further details on contributions or if you are interested in contributing, please refer to our Contribution Guidelines or contact [Your Contact Information].

Thank you!

// Riksarkivet


"""
