class TextHowTo:
    htr_tool = """
    ## Getting Started with the HTR Tool
    To quickly run the HTR Tool and transcribe handwritten text, follow these steps:
    1. Open the HTR Tool tab.
    2. Upload an image or choose an image from the provided Examples (under "Example images to use:" accordin). 
       Note that the accordin works like a "dropdown" and that you just need to press an example to use it (also, use the pagniation at the bottom to view more examples).
    3. The radio button specifes the output file extension, which can be either text or page XML.
    4. Click the "Run HTR" button to initiate the HTR process. You can refer to the screenshot below:
    <figure>
    <img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/htr_run_example.png" alt="HTR_tool" style="width:65%; display: block; margin-left: auto; margin-right:auto;" >
    <figcaption style="text-align: center;"> <em> Figure - How to Run the HTR Tool </em></figcaption>
    </figure> 
    The HTR Tool will transform an image of handwritten text into structured, transcribed text within approximately 1-2 minutes (depending on your hardware). 
    Note that the generated page XML file is strucutred in such manner that it allows for an easy integration with other software, such as Transkribus.
    
    <br><br>

    You can use our own developed Image viewer for the xml output: 
    <p align="center">
        <a href="https://huggingface.co/spaces/Riksarkivet/Viewer_demo">
            <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-xl-dark.svg" alt="Badge 1">
        </a>
    </p>
    <br>

                    
"""
    reach_out = """  Feel free to reach out if you have any questions or need further assistance!

    """

    stepwise_htr_tool = """
## Stepwise HTR Tool

The Stepwise HTR Tool is a powerful tool for performing Handwritten Text Recognition (HTR) tasks. The Stepwise version provides you with fine-grained control over each step of the HTR process, allowing for greater customization and troubleshooting capabilities.
<br><br>
With the Stepwise HTR Tool, you can break down the HTR process into distinct steps: region segmentation, line segmentation, text transcription, and result exploration. This tool offers a range of configuration options to tailor the HTR process to your specific needs. You can adjust settings such as P-threshold and C-threshold to fine-tune the region and line segmentation, and choose from a selection of underlying machine learning models to drive each step of the process.
<br><br>
The Stepwise HTR Tool also provides a dedicated Explore Results tab, allowing you to thoroughly analyze and interact with the transcriptions. You can sort and identify both bad and good predictions, helping you gain insights and make improvements to the HTR accuracy. Each step is interconnected, and the output of one step serves as the input for the next step, ensuring a seamless and efficient workflow.

"""
    stepwise_htr_tool_tab_intro = """
    Follow the instructions below provided in each tab to perform the respective step of the HTR process and ensure you work through the tabs sequentially:

"""

    stepwise_htr_tool_tab1 = """
### Tab 1: Region Segmentation
The Region Segmentation tab allows you to perform the initial step of segmenting the handwritten text into regions of interest. By adjusting the P-threshold and C-threshold settings, you can control the confidence score required for a prediction and the minimum overlap or similarity for a detected region to be considered valid. Additionally, you can select an underlying machine learning model for region segmentation.
<br><br>
To perform region segmentation, follow these steps:
1. Open the "Region Segmentation" tab.
2. Upload an image or choose an image from the provided Examples (under "Example images to use:" accordin).
3. Configure the region segmentation settings:
   - Adjust the P-threshold: Filter and determine the confidence score required for a prediction score to be considered.
   - Adjust the C-threshold: Set the minimum required overlap or similarity for a detected region or object to be considered valid.
   - Select an underlying machine learning model.
4. Click the "Run Region Segmentation" button to initiate the region segmentation process.
"""
    stepwise_htr_tool_tab2 = """

### Tab 2: Line Segmentation
In the Line Segmentation tab, you can further refine the segmentation process by identifying individual lines of text. 
Similar to the Region Segmentation tab, you can adjust the P-threshold and C-threshold settings for line segmentation and choose an appropriate machine learning model.
<br><br>
To perform line segmentation, follow these steps:
1. Open the "Line Segmentation" tab. 
2. Choice a segmented region from image gallery, which populated with the results from the previous tab.
3. Configure the line segmentation settings:
   - Adjust the P-threshold: Filter and determine the confidence score required for a prediction score to be considered.
   - Adjust the C-threshold: Set the minimum required overlap or similarity for a detected region or object to be considered valid.
   - Select an underlying machine learning model.
4. Click the "Run Line Segmentation" button to initiate the line segmentation process. 
"""

    stepwise_htr_tool_tab3 = """
### Tab 3: Transcribe Text
The Transcribe Text tab allows you to convert the segmented text into transcriptions. Here, you can select the desired machine learning model for text transcription.
<br><br>
To transcribe text, follow these steps:
1. Open the "Transcribe Text" tab.
2. The image to transcribe is predefined with the results from the previous tab.
3. Configure the text transcription settings:
   - Select an underlying machine learning model.
4. Click the "Run Text Transcription" button to initiate the text transcription process. 
"""

    stepwise_htr_tool_tab4 = """
### Tab 4: Explore Results
Once the transcription is complete, you can explore the results in the Explore Results tab. This tab provides various features for analyzing and interacting with the transcriptions, allowing you to sort and identify both bad and good predictions.
<br><br>
To explore the HTR results, follow these steps:
1. Open the "Explore Results" tab.
2. Analyze the generated results. The image gallery of cropped text line segments is bi-directional coupled through interaction with the dataframe on the left.
3. Use the provided features, such as the prediction score to sort and interact with the image gallery, identifying both bad and good transcriptions. 
"""

    stepwise_htr_tool_end = """
As mentioned, please note that each tab in this workflow is dependent on the previous steps, where you progressively work through the process in a step-by-step manner.
<br>
"""

    both_htr_tool_video = """
## &nbsp;
Alternatively, you can watch the instructional video below, which provides a step-by-step walkthrough of the HTR Tool and some additional features.
"""

    figure_htr_api = """
<figure>
<img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/notebook_api.png" alt="HTR_tool" style="width:98%; display: block; margin-left: auto; margin-right:auto;" >
<figcaption style="text-align: center;"> <em> Figure - How to run API through a client in a notebook </em></figcaption>
</figure> 
"""

    figure_htr_hardware = """

<figure>
<img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/hardware_example.png" alt="HTR_tool" style="width:75%; display: block; margin-left: auto; margin-right:auto;" >
<figcaption style="text-align: center;"> <em> Figure - Choose a hardware that has atleast a GPU </em></figcaption>
</figure> 
"""


if __name__ == "__main__":
    pass
