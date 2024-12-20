# WORK IN PROGRESS

> :warning: **Dont use yet !**

# htrflow_app: A demo app for htrflow

We're thrilled to introduce [htrflow](https://huggingface.co/spaces/Riksarkivet/htr_demo), our demonstration platform that brings to life the process of transcribing Swedish handwritten documents from the 17th to the 19th century.

<p align="center">
  <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/htrflow_background_dalle3.png?raw=true" alt="HTRFLOW Image" width=40%>
</p>

htrflow_app is designed to provide users with a step-by-step visualization of the HTR-process, and offer non-expert users an inside look into the workings of an AI-transcription pipeline.
At the moment htrflow_app is mainly a demo-application. It’s not intended for production, but instead to showcase the immense possibilities that HTR-technology is opening up for cultural heritage institutions around the world.

All code is open-source, all our models are on [Hugging Face](https://huggingface.co/collections/Riksarkivet/models-for-handwritten-text-recognition-652692c6871f915e766de688) and are free to use, and all data will be made available for download and use on [Hugging Face](https://huggingface.co/datasets/Riksarkivet/placeholder_htr) as well.

**Note** that the backend (src) for the app will be rewritten and packaged to be more optimized under the project name [htrflow_core](https://github.com/Swedish-National-Archives-AI-lab/htrflow_core).

## Run app

Use virtual env.

```
python3 -m venv .venv
source .venv/bin/activate
```

Install libraries with Makefile:

```
make install
```

With pip:

```
pip install -r requirements.txt
```

Run app with:

```
gradio app.py
```

## Run with Docker

There are two options:

### Run with Docker locally

Build container:

```
docker build --tag htrflow/htrflow-app .
```

Run container:

```
docker run -it -d --name htrflow-app -p 7000:7860  htrflow/htrflow-app:latest
```

### Run with Docker with HF

You can also just run it from Hugging Face:

```
docker run -it -p 7860:7860 --platform=linux/amd64 --gpus all \
	-e registry.hf.space/riksarkivet-htr-demo:latest
```

---

## Instructions for documentation

- Naming convention of folder is based on tab
- Naming convention of file is based on subtabs
  - If subtab uses columns and rows
    - Use suffix such as col1, row1 or tab1, to indicate differences in postion of text.

see image below:

<p align="center">
        <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/layout_structure.png?raw=true" alt="Badge 1">
</p>

## Assets and file sharing with app

This repo acts as asset manager for the app:

- [Github Repo](https://github.com/Borg93/htr_gradio_file_placeholder)

**Note**: this repo is an work in progress
