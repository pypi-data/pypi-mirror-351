# pah

[![PyPI - pah](https://img.shields.io/pypi/v/pah)](https://pypi.org/project/pah/)

PDF Auto Highlighter

## Usage

```bash
pip install pah
```

### As a CLI tool

```bash
$ pah highlight --help
usage: pah highlight [-h] -o OUTPUT -m MODEL [-p PROMPT] [--output-page-texts OUTPUT_PAGE_TEXTS] [--output-highlights OUTPUT_HIGHLIGHTS]
                     [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     input_pdf_path

positional arguments:
  input_pdf_path        Input PDF file

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output PDF file with highlights
  -m, --model MODEL     LLM model to use (See https://litellm.vercel.app/docs/providers)
  -p, --prompt PROMPT   Prompt to use for highlighting
  --output-page-texts OUTPUT_PAGE_TEXTS
                        Output JSON file for page texts
  --output-highlights OUTPUT_HIGHLIGHTS
                        Output JSON file for highlights
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
pah gui --help
usage: pah gui [-h]

options:
  -h, --help  show this help message and exit
```

```bash
pah gui
```
