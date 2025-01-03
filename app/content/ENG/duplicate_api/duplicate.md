## Duplicating for own use

Please be aware of certain limitations when using the application:

- This application is primarily designed for demonstration purposes and is not intended for scaling up HTR.
- Currently, the Swedish National Archives has constraints on sharing hardware, leading to a queue system for high demand.
- The demo is hosted on Hugging Face domains, and they may rate-limit you if there's an excessive number of requests in a short timeframe, especially when using the API.

For those requiring heavy usage, you can conveniently duplicate the application.

- Duplicate [application](https://huggingface.co/spaces/Riksarkivet/htr_demo?duplicate=true).

By doing so, you'll create your own private app, which allows for unlimited requests without any restrictions. The image below shows the minimum hardware you need to use if you don't have access to hardware youself:

<figure>

<img src="https://raw.githubusercontent.com/Borg93/htr_gradio_file_placeholder/main/hardware_example.png" alt="HTR_tool" style="width:75%; display: block; margin-left: auto; margin-right:auto;" >
<figcaption style="text-align: center;"> <em> Figure - Choose a hardware that has atleast a GPU </em></figcaption>
</figure>

For individuals with access to dedicated hardware, additional options are available. You have the flexibility to run this application on your own machine utilizing Docker, or by cloning the repository directly. Doing so allows you to leverage your hardware's capabilities to their fullest extent.

- [Clone with Docker](https://huggingface.co/spaces/Riksarkivet/htr_demo?docker=true)
- [Clone Repo](https://huggingface.co/spaces/Riksarkivet/htr_demo/settings?clone=true)

**Note**: To take advantage of CUDA for accelerated inferences, an Nvidia graphics card is required. This setup significantly enhances the performance, ensuring a smoother and faster operation.
