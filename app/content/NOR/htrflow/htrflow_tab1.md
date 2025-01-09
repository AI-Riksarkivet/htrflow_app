### Binarization

The reason for binarizing the images before processing them is that we want the models to generalize as well as possible. By training on only binarized images and by binarizing images before running them through the pipeline, we take the target domain closer to the training domain, and reduce negative effects of background variation, background noise etc., on the final results. The pipeline implements a simple adaptive thresholding algorithm for binarization.

<figure>
<img src="https://github.com/Borg93/htr_gradio_file_placeholder/blob/main/app_project_bin.png?raw=true" alt="HTR_tool" style="width:70%; display: block; margin-left: auto; margin-right:auto;" >
</figure>
