.PHONY: install

venv:
	python -m venv venv


activate: 
	source ./venv/bin/activate

install: local_install install_openmmlab

local_install:
	@echo "Running requirements install"
	pip install --upgrade pip
	pip install -r requirements.txt

install_openmmlab:
	@echo "Running Openmmlab requirements install"
	pip install -U openmim
	mim install mmengine
	mim install mmcv
	mim install mmdet
	mim install mmocr

build:
	pip install -e .
	gradio app.py

# clean_for_actions:
# 	git lfs prune
# 	git filter-branch --force --index-filter "git rm --cached --ignore-unmatch helper/text/videos/eating_spaghetti.mp4" --prune-empty --tag-name-filter cat -- --all
# 	git push --force origin main

# add_space:
#	git remote add demo https://huggingface.co/spaces/Riksarkivet/htr_demo
#	git push --force demo main