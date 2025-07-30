import argparse
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser(description="pah: PDF AutoAuto Highlighter")

    subparsers = parser.add_subparsers(title="subcommands", dest="command")
    cmd_highlight(subparsers.add_parser("highlight", help="highlight a PDF using LLMs"))
    cmd_gui(subparsers.add_parser("gui", help="Run pah on the Web"))

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


def cmd_highlight(parser: argparse.ArgumentParser):
    parser.add_argument("input_pdf_path", type=Path, help="Input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF file with highlights",
        required=True,
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

    def handler(args):
        from pah_core import PAH

        pah = PAH(
            input_pdf_path=args.input_pdf_path,
            output_pdf_path=args.output,
            llm_model=args.model,
            output_page_texts_path=args.output_page_texts,
            output_highlights_path=args.output_highlights,
            log_level=args.log_level,
        )
        pah.highlight(prompt=args.prompt)

    parser.set_defaults(handler=handler)


def cmd_gui(parser: argparse.ArgumentParser):
    from pathlib import Path
    import subprocess

    def handler(args):
        gui_path = Path(__file__).parent / "gui.py"
        process = subprocess.Popen(["streamlit", "run", str(gui_path)])
        process.wait()

    parser.set_defaults(handler=handler)


if __name__ == "__main__":
    cli()
