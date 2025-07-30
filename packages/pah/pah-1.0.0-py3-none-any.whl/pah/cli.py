def cli():
    import argparse
    from pathlib import Path

    from pah import PAH

    parser = argparse.ArgumentParser(description="pah: PDF AutoAuto Highlighter")
    parser.add_argument("input_pdf_path", type=Path, help="Input PDF file")
    parser.add_argument(
        "--output_pdf_path",
        type=Path,
        default=Path("output/example_highlighted.pdf"),
        help="Output PDF file with highlights",
        required=True,
    )
    parser.add_argument(
        "--llm_model",
        type=str,
        # default="gemini/gemini-2.5-flash-preview-05-20",
        help="LLM model to use (See https://litellm.vercel.app/docs/providers)",
        required=True,
    )
    parser.add_argument(
        "--output_highlights_path",
        type=Path,
        default=Path("output/highlights.json"),
        help="Output JSON file for highlights",
        required=False,
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        required=False,
    )

    args = parser.parse_args()

    pah = PAH(
        args.input_pdf_path,
        args.output_pdf_path,
        args.llm_model,
        args.output_highlights_path,
        args.log_level,
    )
    pah.highlight()


if __name__ == "__main__":
    cli()
