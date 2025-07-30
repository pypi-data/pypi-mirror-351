from pathlib import Path

import pymupdf  # type: ignore
from pymupdf import Document, Page, Annot
from pymupdf import utils as pymupdfutils


def get_page_texts(doc: Document) -> list[str]:
    texts: list[str] = []
    for page in doc:
        # NOTE: page.get_text("text") is dynamically assigned, so it's not recognized by type checkers.
        # https://github.com/pymupdf/PyMuPDF/issues/2883
        # text = page.get_text("text")  # type: ignore
        assert isinstance(page, Page), "Page is not a pymupdf.Page instance"
        text = str(pymupdfutils.get_text(page, "text"))
        texts.append(text)

    return texts


def highlight_text(
    doc: Document,
    search_text: str,
    page_num: int | None = None,
    content: str | None = None,
) -> Annot | None:
    for page in doc:
        if page_num is not None and page.number != page_num:
            continue
        quads = pymupdfutils.search_for(page, search_text, quads=True)
        if len(quads) == 0:
            continue

        annot = page.add_highlight_annot(quads)
        annot.set_info(content=content)

        return annot

    return None


def save_document(doc: Document, output_path: Path) -> None:
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
