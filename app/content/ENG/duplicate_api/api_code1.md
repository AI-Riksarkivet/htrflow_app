from gradio_client import Client # pip install gradio_client

# Change url to your client (localhost: http://127.0.0.1:7860/)

client = Client("https://huggingface.co/spaces/Riksarkivet/htr_demo")
job = client.submit(
"https://your.image.url.or.pah.jpg",
api_name="/run_htr_pipeline",
)

print(job.result())
