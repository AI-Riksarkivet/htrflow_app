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
