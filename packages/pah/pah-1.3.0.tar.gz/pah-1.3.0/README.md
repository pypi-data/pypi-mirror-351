# pah

[![PyPI - pah](https://img.shields.io/pypi/v/pah)](https://pypi.org/project/pah/)

PDF Auto Highlighter

## Usage

```bash
pip install pah
```

### As a CLI tool

```bash
$ pah --help
usage: pah [-h] -o OUTPUT -m MODEL -p PROMPT [--output-highlights OUTPUT_HIGHLIGHTS] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] input_pdf_path

pah: PDF AutoAuto Highlighter

positional arguments:
  input_pdf_path        Input PDF file

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output PDF file with highlights (default: output\example_highlighted.pdf)
  -m, --model MODEL     LLM model to use (See https://litellm.vercel.app/docs/providers)
  -p, --prompt PROMPT   Prompt to use for highlighting (default: Extract the most important sections of the text for helping the user understand the content
                        of the PDF document. )
  --output-highlights OUTPUT_HIGHLIGHTS
                        Output JSON file for highlights (default: output\highlights.json)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: INFO)
```

```bash
pah input.pdf --output_pdf_path output.pdf --llm_model gpt-4o
```

### As a Python library

```python
from pah import PAH

pah = PAH(
    input_pdf_path="input.pdf",
    output_pdf_path="output.pdf",
    llm_model="gpt-4o",
    output_highlights_path="highlights.json"
)
pah.highlight()
```

### As a GUI tool

```bash
pip install pah[gui]
```

```bash
pah-app
```
