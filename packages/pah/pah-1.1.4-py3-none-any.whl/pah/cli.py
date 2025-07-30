def cli():
    import argparse
    from pathlib import Path

    from pah import PAH

    parser = argparse.ArgumentParser(description="pah: PDF AutoAuto Highlighter")
    parser.add_argument("input_pdf_path", type=Path, help="Input PDF file")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output/example_highlighted.pdf"),
        help="Output PDF file with highlights",
        required=True,
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        help="LLM model to use (See https://litellm.vercel.app/docs/providers)",
        required=True,
    )
    parser.add_argument(
        "--output-highlights",
        type=Path,
        default=Path("output/highlights.json"),
        help="Output JSON file for highlights",
        required=False,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        required=False,
    )

    args = parser.parse_args()

    pah = PAH(
        input_pdf_path=args.input_pdf_path,
        output_pdf_path=args.output,
        llm_model=args.model,
        output_highlights_path=args.output_highlights,
        log_level=args.log_level,
    )
    pah.highlight()


if __name__ == "__main__":
    cli()
