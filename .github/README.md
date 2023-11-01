# HTRFLOW: A demo app for HTR

We're thrilled to introduce [HTRFLOW](https://huggingface.co/spaces/Riksarkivet/htr_demo), our demonstration platform that brings to life the process of transcribing Swedish handwritten documents from the 17th to the 19th century.

<p align="center">
  <img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/htrflow_background_dalle3.png?raw=true" alt="HTRFLOW Image" width=40%>
</p>

HTRFLOW is designed to provide users with a step-by-step visualization of the HTR-process, and offer non-expert users an inside look into the workings of an AI-transcription pipeline.
At the moment HTRFLOW is mainly a demo-application. It’s not intended for production, but instead to showcase the immense possibilities that HTR-technology is opening up for cultural heritage institutions around the world.

All code is open-source, all our models are on [Hugging Face](https://huggingface.co/collections/Riksarkivet/models-for-handwritten-text-recognition-652692c6871f915e766de688) and are free to use, and all data will be made available for download and use on [Hugging Face](https://huggingface.co/datasets/Riksarkivet/placeholder_htr) as well.

HTRFLOW is more than just a demo; it's a testament to the advancement of open source development of HTR. As we progress, the app will be renamed into HTRFLOW.app and HTRFLOW will evolve into multiple parts. HTRFLOW will become our foundational library that will serve as the backbone for a range of applications in the transcription domain. Note that the backend (src) for the app will be rewritten and packaged to be more optimized under the project name [HTR_SVEA](https://github.com/Borg93/htr_svea) (possibly renamed into HTRFLOW.core).

## Run app

Install libraries with Makefile:

```
make install
```

With pip:

```
pip install -r requirements.txt
```

and

```
!pip install -U openmim
!mim install mmengine
!mim install mmcv
!mim install mmdet
!mim install mmocr
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
docker run -it -d --name htrflow-app -p 7000:7000  htrflow/htrflow-app:latest
```

### Run with Docker with HF

You can also just run it from Hugging Face:

```
docker run -it -p 7860:7860 --platform=linux/amd64 --gpus all \
	-e registry.hf.space/riksarkivet-htr-demo:latest
```
