import re
from typing import Any


class MetadataExtractor:
    DOI_REGEX = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
    YEAR_REGEX = re.compile(r"\b(19|20)\d{2}\b")

    def extract(self, pages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Extracts title, doi, year, authors heuristically from the first few pages.
        """
        if not pages:
            return {}

        first_page_text = pages[0]["text"]
        lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]

        metadata = {
            "title": lines[0] if lines else None,
            "doi": None,
            "year": None,
            "authors": None,
            "venue": None,
            "abstract": None,
        }

        # Search for DOI
        for line in lines[:20]:
            match = self.DOI_REGEX.search(line)
            if match:
                metadata["doi"] = match.group(0)
                break

        # Search for Year near title
        for line in lines[:10]:
            match = self.YEAR_REGEX.search(line)
            if match:
                metadata["year"] = int(match.group(0))
                break

        # Basic heuristic for abstract
        abstract_start = -1
        for i, line in enumerate(lines):
            if "abstract" in line.lower()[:15]:
                abstract_start = i
                break

        if abstract_start != -1:
            abstract_text = []
            for line in lines[abstract_start + 1 :]:
                if "introduction" in line.lower()[:15]:
                    break
                abstract_text.append(line)
            metadata["abstract"] = " ".join(abstract_text)

        return metadata
