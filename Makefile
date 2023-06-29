venv:
	python -m venv venv


activate: 
	source ./venv/bin/activate

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