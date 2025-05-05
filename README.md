
# Information extraction of the Derenbourg Catalogue

The Derenbourg Catalogue of Arabic manuscripts in the El Escorial Collection (Les manuscrits arabes de l’Escurial) has been been downloaded as pdfs: https://rbme.patrimonionacional.es/s/rbme/page/-rabes

This project includes the OCR, post-processing and manual post-correction of the catalogue entries to use it in various IR tasks using LLMs.


## Workflow

1. Convert pdfs to png files:

```bash
bash pdf2png.sh ../data/pdf ../data/png
```

2. Setup account in Google Cloud Vision and authenticate:

- Install gcloud, authenticate and setup project:

```bash
pip install google-cloud-vision
gcloud init
gcloud auth application-default login 
```

- Create a project called ocr-arabic-catalogue in https://console.cloud.google.com and enable Cloud Vision API and billing

3. Use API of Google Cloud Vision to extract French and Arabic text from png images into json:

```bash
python3 extract_text.py ../data/png ../data/json
```

4. Apply heuristic normalisations to the data for cleanup, segment into catalogue records and save each into text files.

```bash
python3 prepare_data.py ../data/json ../data/text
```


5. ollama + Open WebUI and RAG

ollama create mixtral-8192 -f Modelfile
ollama run mixtral-8192

ollama create llama3.2-8192 -f Modelfile
ollama run llama3.2-8192

ollama create aya-8192 -f Modelfile
ollama run aya-8192


