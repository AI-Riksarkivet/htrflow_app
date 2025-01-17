.PHONY: install

venv:
	python -m venv venv


activate: 
	source ./venv/bin/activate

install: local_install install_openmmlab

docker_install: local_install install_openmmlab_with_mim

local_install:
	@echo "Running requirements install"
	pip install --upgrade pip
	pip install -r requirements.txt

install_openmmlab_with_mim:
	@echo "Running Openmmlab requirements install"
	pip install -U openmim
	mim install mmengine
	mim install mmcv
	mim install mmdet
	mim install mmocr

install_openmmlab:
	@echo "Running Openmmlab requirements install"
	pip install mmengine==0.7.4
	pip install mmcv==2.0.1
	pip install mmdet==3.0.0
	pip install mmocr==1.0.0

build:
	pip install -e .
	gradio app.py

docker_build:
    docker build -t htrflow-app -f .docker/Dockerfile .

# clean_for_actions:
# 	git lfs prune
# 	git filter-branch --force --index-filter "git rm --cached --ignore-unmatch helper/text/videos/eating_spaghetti.mp4" --prune-empty --tag-name-filter cat -- --all
# 	git push --force origin main

# add_space:
#	git remote add demo https://huggingface.co/spaces/Riksarkivet/htr_demo
#	git push --force demo main