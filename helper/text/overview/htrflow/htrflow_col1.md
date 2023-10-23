## Introduction

The Swedish National Archives introduces a demonstrational end-to-end HTR (Handwritten Text Recognition) pipeline. The pipeline consists of two instance segmentation models, one trained for segmenting text-regions within running-text document images, and another trained for segmenting text-lines within these regions. The text-lines are then transcribed by a text-recognition model trained on a vast set of swedish handwriting ranging from the 17th to the 19th century.

## Usage

It needs to be emphasized that this application is intended mainly for demo-purposes. It’s aim is to showcase our pipeline for transcribing historical, running-text documents, not to put the pipeline into large-scale production.
**Note**: In the future we’ll optimize the code to suit a production scenario with multi-GPU, batch-inference, but this is still a work in progress. <br>

For an insight into the upcoming features we are working on:

- Navigate to the > **Overview** > **Changelog & Roadmap**.
