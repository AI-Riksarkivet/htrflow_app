## Introduction

The Swedish National Archives introduces a demonstrational end-to-end HTR (Handwritten Text Recognition) pipeline. The pipeline consists of two instance segmentation models, one trained for segmenting text-regions within running-text document images, and another trained for segmenting text-lines within these regions. The text-lines are then transcribed by a text-recognition model trained on a vast set of swedish handwriting ranging from the 17th to the 19th century.

## Usage

It needs to be emphasized that this application is intended mainly for demo-purposes. Its aim is to showcase our pipeline for transcribing historical, running-text documents, not to put the pipeline into large-scale production.
**Note**: In the future we’ll optimize the code to suit a production scenario with multi-GPU, batch-inference, but this is still a work in progress. <br>

For an insight into the upcoming features we are working on:

- Navigate to the > **Overview** > **Changelog & Roadmap**.

## Limitations

The demo, hosted on Huggingface and assigned a T4 GPU, can only handle two users submissions at a time. If you experience long wait times or unresponsiveness, this is the reason. In the future, we plan to host this solution ourselves, with a better server for an improved user experience, optimized code, and multiple model options. Exciting developments are on the horizon!

It's also important to note that the models work on running text, not text in table format.
