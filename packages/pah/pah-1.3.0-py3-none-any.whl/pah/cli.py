import argparse
from pathlib import Path


def cli():
    from pah_core import PAH

    parser = argparse.ArgumentParser(description="pah: PDF AutoAuto Highlighter")

    parser.add_argument("input_pdf_path", type=Path, help="Input PDF file", nargs="?")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/example_highlighted.pdf"),
        help="Output PDF file with highlights (default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="LLM model to use (See https://litellm.vercel.app/docs/providers)",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Prompt to use for highlighting",
    )
    parser.add_argument(
        "--output-page-texts",
        type=Path,
        help="Output JSON file for page texts",
    )
    parser.add_argument(
        "--output-highlights",
        type=Path,
        help="Output JSON file for highlights",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: %(default)s)",
    )

    args = parser.parse_args()

    pah = PAH(
        input_pdf_path=args.input_pdf_path,
        output_pdf_path=args.output,
        llm_model=args.model,
        output_page_texts_path=args.output_page_texts,
        output_highlights_path=args.output_highlights,
        log_level=args.log_level,
    )
    pah.highlight(prompt=args.prompt)


if __name__ == "__main__":
    cli()
