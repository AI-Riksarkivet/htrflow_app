PIPELINES = {
    "Swedish - Spreads": {
        "file": "app/assets/templates/nested_swe_ra.yaml",
        "description": "This pipeline works well on handwritten historic documents written in Swedish with multiple text regions. The HTR model used in the pipeline is <b>Swedish Lion Libre</b> from <a href='https://huggingface.co/Riksarkivet'>the National Archives of Sweden</a>.",
        "examples": [
            "R0003364_00005.jpg",
            "30002027_00008.jpg",
            "A0070302_00201.jpg",
        ],
    },
    "Swedish - Single page and snippets": {
        "file": "app/assets/templates/simple_swe_ra.yaml",
        "description": "This pipeline works well on handwritten historic letters and other documents written in Swedish with only one text region. The HTR model used in the pipeline is <b>Swedish Lion Libre</b> from <a href='https://huggingface.co/Riksarkivet'>the National Archives of Sweden</a>.",
        "examples": [
            "451511_1512_01.jpg",
            "A0062408_00006.jpg",
            "C0000546_00085_crop.png",
            "A0073477_00025.jpg",
        ],
    },
    "Norwegian - Single page and snippets": {
        "file": "app/assets/templates/simple_nordhand.yaml",
        "description": "This pipeline works well on handwritten historic letters and other documents written in Norwegian with only one text region. The model is developed by the <a href='https://huggingface.co/Sprakbanken/TrOCR-norhand-v3'>Language Bank</a> at The National Library of Norway.",
        "examples": ["norhand_fmgh040_4.jpg"],
    },
    "Medieval - Single page and snippets": {
        "file": "app/assets/templates/simple_medival.yaml",
        "description": "This pipeline works well for medieval scripts written in single-page running text. The HTR model is from <a href='https://huggingface.co/medieval-data'>Medieval Data</a>, but other models can be selected from here: <a href='https://huggingface.co/collections/medieval-data/trocr-medieval-htr-66871faba03abfbb1b66ab69'>Medieval Models</a>.",
        "examples": ["manusscript_kb.png"],
    },
    "English - Single page and snippets": {
        "file": "app/assets/templates/simple_eng_modern.yaml",
        "description": "This pipeline works well for English text in single page running text. The HTR model is from <a href='https://huggingface.co/microsoft/trocr-base-handwritten'>Microsoft</a>.",
        "examples": ["iam.png"],
    },
}
