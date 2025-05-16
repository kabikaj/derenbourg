
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

5. Create RAG with [OpenWebUI](https://github.com/open-webui/open-webui) and [ollama](https://ollama.com) or [OpenAI](https://platform.openai.com).

Use the oficial information.

For local models with ollama you need to increase the context window:

```bash
ollama create mixtral-8192 -f src/mixtral/Modelfile
ollama run mixtral-8192

ollama create llama3.2-8192 -f src/llama3.2/Modelfile
ollama run llama3.2-8192

ollama create aya-8192 -f src/aya/Modelfile
ollama run aya-8192
```

6. Convert text files to structured data:

```bash
python3 transform.py ../data/text_corrected ../data/json_modelled --service openai --ini 1 --end 150
```

You can use openai or deepseek as service. You need to have the corresponding keys saved in .openai.env and .deepseek.env.


## Website

Visit the sample website at https://kabikaj.github.io/derenbourg


## License

MIT License

Copyright (c) 2025 Alicia González Martínez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
