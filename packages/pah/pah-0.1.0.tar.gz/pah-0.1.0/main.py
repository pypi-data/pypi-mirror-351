from pathlib import Path

from pah import PAH


if __name__ == "__main__":
    input_pdf_path = Path("example.pdf")
    output_pdf_path = Path("output/example_highlighted.pdf")
    llm_model = "gemini/gemini-2.5-flash-preview-05-20"

    pah = PAH(
        input_pdf_path,
        output_pdf_path,
        llm_model=llm_model,
        output_highlights_path=Path("output/highlights.json"),
    )
    pah.highlight()
