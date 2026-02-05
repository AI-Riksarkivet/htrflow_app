import gradio as gr

# Translation dictionaries for Swedish and English
translations = {
    "en": {
        # Main title
        "app_title": "HTR-demo 🔍",
        # Sidebar
        "sidebar_title": "HTR-demo",
        "sidebar_description": "Developed by the **National Archives of Sweden** with [Huminfra](https://www.huminfra.se/) that demonstrates AI-powered conversion of historical manuscripts to digital text using [HTRflow](https://ai-riksarkivet.github.io/htrflow/latest).",
        "sidebar_note": "Note: This demo application is for demonstration purposes only and is not intended for production use. The application is hosted on Hugging Face 🤗 using shared infrastructure, which means there is a daily quota limit on how much you can use the app each day.",
        "sidebar_opensource": "Both the App and HTRflow's code are completely open source. Explore and contribute on GitHub:",
        "sidebar_star": "If you find our projects useful, please consider giving us a star ⭐!",
        "sidebar_contact": "Contact",
        # Upload tab
        "tab_upload": "1. Upload",
        "tab_result": "2. Result",
        "tab_export": "3. Export",
        "upload_title": "Upload",
        "upload_description": "Select or upload the image you want to transcribe. Most common image formats are supported and you can upload max 5 images at a time in this hosted demo.",
        "image_label": "Image to transcribe",
        # Examples tab
        "examples_tab": "Examples",
        "image_id_tab": "Image ID",
        "iiif_tab": "IIIF Manifest",
        "url_tab": "URL",
        "pdf_tab": "PDF",
        # Image upload options
        "image_id_label": "Upload by image ID",
        "image_id_info": "Use any image from our digitized archives by pasting its image ID found in the image viewer. Press enter to submit.",
        "image_id_placeholder": "R0002231_00005",
        "iiif_label": "IIIF Manifest",
        "iiif_info": "Use an image from a IIIF manifest by pasting a IIIF manifest URL. Press enter to submit.",
        "iiif_max_images": "Number of image to return from IIIF manifest",
        "url_label": "Image URL",
        "url_info": "Upload an image by pasting its URL.",
        "url_placeholder": "https://example.com/image.jpg",
        "pdf_label": "PDF",
        # Settings
        "settings_title": "Settings",
        "settings_description": "Select a pipeline that best matches your image. The pipeline determines the processing workflow optimized for different text recognition tasks. If you select an example image, a suitable pipeline will be preselected automatically. However, you can edit the pipeline if you need to customize it further. Choosing the right pipeline significantly improves transcription quality.",
        "edit_pipeline": "Edit Pipeline",
        "edit_pipeline_description": 'The code snippet below is a YAML file that the HTR-demo app uses to process the image. If you have chosen an image from the "Examples" section, the YAML is already a pre-made template tailored to fit the example image.\n\nEdit pipeline if needed:',
        "pipeline_docs": "See the documentation for a detailed description on how to customize HTRflow pipelines.",
        # Buttons
        "run_htr": "Run HTR",
        # Messages
        "max_images_warning": "Maximum images you can upload is set to:",
        "yaml_required": "HTRflow: Please insert a HTRflow-yaml template",
        "yaml_error": "HTRflow: Error loading YAML configuration:",
        "upload_required": "HTRflow: You must upload atleast 1 image or more",
        "processing_message": "HTRflow: processing",
        "image": "image",
        "images": "images",
        "pipeline_failed": "HTRflow: Pipeline failed on step",
        "backup_saved": "A backup collection is saved at",
        "completed": "Completed succesfully ✨",
        # Progress messages
        "progress_starting": "HTRflow: Starting",
        "progress_processing": "HTRflow: Processing",
        "progress_finish": "HTRflow: Finish, redirecting to 'Results tab'",
        # Visualizer
        "visualizer_description": "The image to the left shows where HTRflow found text in the image. The transcription can be seen to the right.",
    },
    "sv": {
        # Main title
        "app_title": "HTR-demo 🔍",
        # Sidebar
        "sidebar_title": "HTR-demo",
        "sidebar_description": "Utvecklad av **Riksarkivet** med [Huminfra](https://www.huminfra.se/) som demonstrerar AI-driven konvertering av historiska manuskript till digital text med [HTRflow](https://ai-riksarkivet.github.io/htrflow/latest).",
        "sidebar_note": "OBS: Denna demoapplikation är endast för demonstrationsändamål och är inte avsedd för produktionsanvändning. Applikationen är värd på Hugging Face 🤗 med delad infrastruktur, vilket innebär att det finns en daglig kvotgräns för hur mycket du kan använda appen varje dag.",
        "sidebar_opensource": "Både appen och HTRflows kod är helt öppen källkod. Utforska och bidra på GitHub:",
        "sidebar_star": "Om du tycker våra projekt är användbara, överväg att ge oss en stjärna ⭐!",
        "sidebar_contact": "Kontakt",
        # Upload tab
        "tab_upload": "1. Ladda upp",
        "tab_result": "2. Resultat",
        "tab_export": "3. Exportera",
        "upload_title": "Ladda upp",
        "upload_description": "Välj eller ladda upp bilden du vill transkribera. De flesta vanliga bildformat stöds och du kan ladda upp max 5 bilder åt gången i denna värdbaserade demo.",
        "image_label": "Bild att transkribera",
        # Examples tab
        "examples_tab": "Exempel",
        "image_id_tab": "Bild-ID",
        "iiif_tab": "IIIF-manifest",
        "url_tab": "URL",
        "pdf_tab": "PDF",
        # Image upload options
        "image_id_label": "Ladda upp med bild-ID",
        "image_id_info": "Använd vilken bild som helst från våra digitaliserade arkiv genom att klistra in dess bild-ID som finns i bildvisaren. Tryck enter för att skicka.",
        "image_id_placeholder": "R0002231_00005",
        "iiif_label": "IIIF-manifest",
        "iiif_info": "Använd en bild från ett IIIF-manifest genom att klistra in en IIIF-manifest-URL. Tryck enter för att skicka.",
        "iiif_max_images": "Antal bilder att returnera från IIIF-manifest",
        "url_label": "Bild-URL",
        "url_info": "Ladda upp en bild genom att klistra in dess URL.",
        "url_placeholder": "https://exempel.com/bild.jpg",
        "pdf_label": "PDF",
        # Settings
        "settings_title": "Inställningar",
        "settings_description": "Välj en pipeline som bäst matchar din bild. Pipelinen bestämmer arbetsflödet optimerat för olika textigenkänningsuppgifter. Om du väljer en exempelbild kommer en lämplig pipeline att väljas automatiskt. Du kan dock redigera pipelinen om du behöver anpassa den ytterligare. Att välja rätt pipeline förbättrar avsevärt transkriberingskvaliteten.",
        "edit_pipeline": "Redigera pipeline",
        "edit_pipeline_description": 'Kodavsnittet nedan är en YAML-fil som HTR-demo-appen använder för att bearbeta bilden. Om du har valt en bild från avsnittet "Exempel" är YAML redan en färdig mall anpassad för exempelbilden.\n\nRedigera pipeline vid behov:',
        "pipeline_docs": "Se dokumentationen för en detaljerad beskrivning av hur man anpassar HTRflow-pipelines.",
        # Buttons
        "run_htr": "Kör HTR",
        # Messages
        "max_images_warning": "Maximalt antal bilder du kan ladda upp är satt till:",
        "yaml_required": "HTRflow: Vänligen infoga en HTRflow-yaml-mall",
        "yaml_error": "HTRflow: Fel vid laddning av YAML-konfiguration:",
        "upload_required": "HTRflow: Du måste ladda upp minst 1 bild eller fler",
        "processing_message": "HTRflow: bearbetar",
        "image": "bild",
        "images": "bilder",
        "pipeline_failed": "HTRflow: Pipeline misslyckades vid steg",
        "backup_saved": "En säkerhetskopia är sparad på",
        "completed": "Slutförd framgångsrikt ✨",
        # Progress messages
        "progress_starting": "HTRflow: Startar",
        "progress_processing": "HTRflow: Bearbetar",
        "progress_finish": "HTRflow: Klar, omdirigerar till 'Resultat-flik'",
        # Visualizer
        "visualizer_description": "Bilden till vänster visar var HTRflow hittade text i bilden. Transkriptionen kan ses till höger.",
    },
}

# Create i18n instance
i18n = gr.I18n(**translations)
