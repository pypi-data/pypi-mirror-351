# pah

[![PyPI - pah](https://img.shields.io/pypi/v/pah)](https://pypi.org/project/pah/)

PDF Auto Highlighter

## Usage

```bash
pip install pah
```

### As a CLI tool

```bash
$ uv run pah --help
usage: pah [-h] --output_pdf_path OUTPUT_PDF_PATH --llm_model LLM_MODEL [--output_highlights_path OUTPUT_HIGHLIGHTS_PATH]
           [--log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
           input_pdf_path

pah: PDF AutoAuto Highlighter

positional arguments:
  input_pdf_path        Input PDF file

options:
  -h, --help            show this help message and exit
  --output_pdf_path OUTPUT_PDF_PATH
                        Output PDF file with highlights
  --llm_model LLM_MODEL
                        LLM model to use (See https://litellm.vercel.app/docs/providers)
  --output_highlights_path OUTPUT_HIGHLIGHTS_PATH
                        Output JSON file for highlights
  --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level
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
