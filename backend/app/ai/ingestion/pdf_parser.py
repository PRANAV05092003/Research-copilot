import io
from typing import Any

from pypdf import PdfReader

from app.core.errors import AppError


class PDFParser:
    def parse(self, file_bytes: bytes) -> list[dict[str, Any]]:
        """
        Parses a PDF and returns a list of pages.
        Each page is a dictionary: {"page_number": int, "text": str}
        """
        reader = PdfReader(io.BytesIO(file_bytes))

        if reader.is_encrypted:
            raise AppError(
                status_code=422, title="PDF Error", detail="Encrypted PDFs are not supported."
            )

        pages = []
        total_chars = 0

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append({"page_number": i + 1, "text": text.strip()})
                total_chars += len(text)

        # Detect if it's likely a scanned document with no text layer
        avg_chars_per_page = total_chars / max(1, len(reader.pages))
        if avg_chars_per_page < 10:
            raise AppError(
                status_code=422,
                title="Unprocessable Entity",
                detail="No extractable text found. Scanned PDFs are currently unsupported.",
            )

        return pages
