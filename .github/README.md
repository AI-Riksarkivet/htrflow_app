# HTRflow_app

[HTRflow_app](https://huggingface.co/spaces/Riksarkivet/htr_demo), our interactive demo application that visualizes the entire Handwritten Text Recognition (HTR) process. With this demo, users can explore, step by step, how AI transforms historical manuscripts into digital text.

Please note that this is a demo application—not intended for production use—but it highlights the immense potential of HTR technology for cultural heritage institutions worldwide.


<p align="center">
  <img src="https://ai-riksarkivet.github.io/htrflow/latest/assets/background_htrflow_2.png" alt="HTRflow App Demo" width="80%">
</p>

---

## Guide

This demo consists of three tabs: **Upload**, **Results**, and **Export** and uses [HTRflow](https://ai-riksarkivet.github.io/htrflow/latest/index.html) as backend

1. **Upload Tab:**  
   - **Upload Images:** Start in the Upload tab by adding one or multiple images.  
   - **Fetch Images:** Alternatively, you can retrieve images from the [Riksarkivet IIIF server](https://github.com/Riksarkivet/dataplattform/wiki/IIIF).  
   - **Choose a Template:** Select a template that matches your material. For more details, see the [HTRflow guide](https://ai-riksarkivet.github.io/htrflow/latest/getting_started/pipeline.html).  
   - **Submit:** Click **Submit** to start the HTR job. The HTRflow backend will then process your images and generate a [Document Model](https://ai-riksarkivet.github.io/htrflow/latest/getting_started/document_model.html).

2. **Results Tab:**  
   - This tab displays the updated state of the Document Model created from your submission. Your uploaded images and chosen template drive how the document is rendered and visualized in real time.

3. **Export Tab:**  
   - Use the Export tab to serialize and export the Document Model. Here, you can select the output format and choose name of the files that meets your needs.

---

## Development

### Prerequisites

- **Python:** Version 3.10 or higher
- **pip:** Python package installer
- **(Optional) Docker:** For containerized deployment
- **(Optional) Nvidia GPU:** For faster predictions..


### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your_username/htrflow_app.git
cd htrflow_app
```

#### 2. Install **uv** Globally

Install **uv** without activating a virtual environment:

```bash
pip install uv
```

#### 3. Create a Virtual Environment Using **uv**

Create a virtual environment with Python 3.10:

```bash
uv venv python 3.10
```

#### 4. Activate the Virtual Environment

Activate your newly created virtual environment:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 5. Install Project Dependencies

For a one-time dependency sync, run:

```bash
uv sync
```

Or, if you are developing and prefer an editable installation, run:

```bash
uv pip install -e .
```

#### 6. Running the Application Locally (dev)

For "hot reload" when developing, launch the Gradio demo by running:

```bash
gradio app/main.py
```

### Running the Application

Follow [Installation](#installation) and launch the Gradio demo by running:

```bash
uv run app/main.py
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

## License

This project is open source. See the [LICENSE](./LICENSE) file for details.

