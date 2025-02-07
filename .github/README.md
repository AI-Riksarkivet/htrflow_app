# HTRflow_app

[HTRflow_app](https://huggingface.co/spaces/Riksarkivet/htr_demo), our interactive demo application that visualizes the entire Handwritten Text Recognition (HTR) process. With this demo, users can explore, step by step, how AI transforms historical manuscripts into digital text.

Please note that this is a demo application—not intended for production use—but it highlights the immense potential of HTR technology for cultural heritage institutions worldwide.


<p align="center">
  <img src="https://ai-riksarkivet.github.io/htrflow/latest/assets/background_htrflow_2.png" alt="HTRflow App Demo" width="80%">
</p>

---
<!-- https://ecotrust-canada.github.io/markdown-toc/ -->
- [HTRflow_app](#htrflow-app) 
  * [Overview](#overview)
  * [Guide](#guide)
  * [How to use app..](#how-to-use-app)
  * [Getting Started](#getting-started)
    + [Prerequisites](#prerequisites)
    + [Installation](#installation)
    + [Running the Application Locally](#running-the-application-locally)
  * [Running with Docker](#running-with-docker)
    + [Locally with Docker](#locally-with-docker)
    + [On Hugging Face Spaces](#on-hugging-face-spaces)
  * [Contributing](#contributing)
  * [License](#license)


---

## Guide

The demo consist of 3 tabs: Upload, Results and Export. You navigate through the app by first uploading 1 or many images  in 

Upload:

Result:

Export:

## Pipeline Configuration

HTRflow powers the application's engine with a structured pipeline design pattern. This pattern uses declarative YAML schemas as blueprints to define step-by-step processing instructions. For detailed documentation, visit the [HTRflow Pipeline Guide](https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html#yaml).

<p align="center">
  <img src="../app/assets/images/3_worker.png" alt="HTRflow Worker Pipeline" width="20%">
</p>

### Understanding YAML Pipeline Templates

The following series of images demonstrates how YAML pipeline templates function. Each template is designed for specific document types - the example below shows a template optimized for single-column running text, such as letters, notes, and individual pages.

<p align="center">
  <img src="../app/assets/images/how_to_1.png" alt="YAML Template Structure" width="70%">
</p>

### Pipeline Steps

Each pipeline consists of sequential steps executed from top to bottom. In this example, we focus on two primary steps:

1. **Segmentation**: Identifies and extracts text lines from the image
2. **Text Recognition**: Performs Handwritten Text Recognition (HTR) on the segmented lines

<p align="center">
  <img src="../app/assets/images/how_to_2.png" alt="Pipeline Steps Overview" width="50%">
</p>

### Model Integration

Models specified in the pipeline can be downloaded directly from the [Huggingface model hub](https://huggingface.co/models?library=htrflow). For a comprehensive list of supported models, refer to the [HTRflow Models Documentation](https://ai-riksarkivet.github.io/htrflow/latest/getting_started/models.html#models).

> **Note**: For English text recognition, you'll need to specify an appropriate model ID, such as the [Microsoft TrOCR base handwritten model](https://huggingface.co/microsoft/trocr-base-handwritten).

<p align="center">
  <img src="../app/assets/images/how_to_3.png" alt="Model Configuration" width="50%">
</p>

### Processing Workflow

#### Text Line Detection
The following image illustrates the text line segmentation process:

<p align="center">
  <img src="../app/assets/images/how_to_4.png" alt="Text Line Detection Process" width="90%">
</p>

#### Text Recognition
After segmentation, the detected text lines are processed by the HTR component:

<p align="center">
  <img src="../app/assets/images/how_to_5.png" alt="Text Recognition Process" width="80%">
</p>

#### Reading Order Determination
The final pipeline step determines the reading order of the text. In this example, it applies a simple top-down ordering transformation:

<p align="center">
  <img src="../app/assets/images/how_to_6.png" alt="Reading Order Determination" width="85%">
</p>





## Development

### Prerequisites

- **Python:** Version 3.7 or higher
- **pip:** Python package installer
- **(Optional) Docker:** For containerized deployment
- **(Optional) Nvidia GPU:** For faster predictions..


### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your_username/htrflow_app.git
   cd htrflow_app
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**

   Since we are no longer using a Makefile, install the required packages with:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application Locally

Launch the Gradio demo by running:

```bash
gradio app/main.py
```

Then open your web browser and navigate to `http://localhost:7860` (or the address displayed in your terminal) to interact with the demo.

---

## Running with Docker

### Locally with Docker

1. **Build the Docker Image:**

   ```bash
   docker build --tag htrflow/htrflow-app .
   ```

2. **Run the Docker Container:**

   ```bash
   docker run -it -d --name htrflow-app -p 7000:7860 htrflow/htrflow-app:latest
   ```

   Now, visit `http://localhost:7000` in your browser.

### On Hugging Face Spaces

Alternatively, you can run HTRflow_app directly on Hugging Face with:

```bash
docker run -it -p 7860:7860 --platform=linux/amd64 --gpus all \
    -e registry.hf.space/riksarkivet-htr-demo:latest
```

---


## Contributing

We welcome community contributions! If you’d like to contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to your branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## License

This project is open source. See the [LICENSE](./LICENSE) file for details.

