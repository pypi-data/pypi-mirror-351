import argparse
from pathlib import Path

from pah import PAH

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PAH: PDF AutoAuto Highlighter")
    parser.add_argument("input_pdf_path", type=Path, help="Path to the input PDF file")
    parser.add_argument(
        "--output_pdf_path",
        type=Path,
        default=Path("output/example_highlighted.pdf"),
        help="Path to the output PDF file with highlights",
    )
    parser.add_argument(
        "--llm_model",
        type=str,
        default="gemini/gemini-2.5-flash-preview-05-20",
        help="LLM model to use",
    )
    parser.add_argument(
        "--output_highlights_path",
        type=Path,
        default=Path("output/highlights.json"),
        help="Path to the output JSON file for highlights",
    )

    args = parser.parse_args()

    pah = PAH(
        args.input_pdf_path,
        args.output_pdf_path,
        llm_model=args.llm_model,
        output_highlights_path=args.output_highlights_path,
    )
    pah.highlight()
