from logging import INFO, Formatter, StreamHandler, getLogger
from pathlib import Path
import json

import pymupdf  # type: ignore

from pah_core.services import llm, pdf

DEFAULT_PROMPT = """
Extract the most important sections of the text for helping the user understand the content of the PDF document.
"""


class PAH:
    def __init__(
        self,
        input_pdf_path: Path,
        output_pdf_path: Path,
        llm_model: str = "gemini/gemini-pro",
        llm_api_key: str | None = None,
        output_page_texts_path: Path | None = None,
        output_highlights_path: Path | None = None,
        log_level: int | str = INFO,
    ):
        self.input_pdf_path = input_pdf_path
        self.document = pymupdf.Document(input_pdf_path)
        self.output_pdf_path = output_pdf_path
        self.llm_model = llm_model
        self.llm_api_key = llm_api_key
        self.output_page_texts_path = output_page_texts_path
        self.output_highlights_path = output_highlights_path

        handler = StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(Formatter("%(name)s - [%(levelname)s] %(message)s"))
        logger = getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        self.logger = logger

    def highlight(
        self,
        prompt: str = DEFAULT_PROMPT,
    ):
        self.logger.info("Getting page texts from the PDF document...")
        page_texts = pdf.get_page_texts(self.document)

        if self.output_page_texts_path:
            self.logger.info(f"Saving page texts to {self.output_page_texts_path}...")
            with open(self.output_page_texts_path, "w", encoding="utf-8") as f:
                json.dump(page_texts, f, indent=2, ensure_ascii=False)

        self.logger.info("Getting highlights from the LLM...")
        highlights = llm.get_highlights(
            model=self.llm_model,
            prompt=prompt,
            page_texts=page_texts,
            api_key=self.llm_api_key,
        )

        if self.output_highlights_path:
            self.logger.info(f"Saving highlights to {self.output_highlights_path}...")
            with open(self.output_highlights_path, "w", encoding="utf-8") as f:
                json.dump(
                    [h.model_dump() for h in highlights],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        self.logger.info(
            f"Found {len(highlights)} highlights. Applying them to the PDF..."
        )

        for highlight in highlights:
            annot = pdf.highlight_text(
                doc=self.document,
                search_text=highlight.text,
                # page_num=highlight.page,
                content=highlight.reason,
            )
            if annot is None:
                self.logger.warning(
                    f"Could not find text to highlight '{highlight.text}' on page {highlight.page}. Skipping."
                )

        self.logger.info("Saving the highlighted PDF document...")
        self.output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.save_document(self.document, self.output_pdf_path)

        self.logger.info("Done! The highlighted PDF document is saved.")
