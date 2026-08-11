import difflib
from typing import Any

from app.ai.agents.prompts import CITATION_VERIFICATION_SYSTEM_PROMPT
from app.ai.providers.base import LLMProvider


class CitationVerifier:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def verify_citation(self, claim: str, chunk_text: str) -> dict[str, Any]:
        """
        Uses the LLM to strictly verify if the chunk text supports the claim.
        Returns a dictionary with verdict, score, and reasoning.
        """
        prompt = f"Claim: {claim}\n\nContext Chunk: {chunk_text}"
        return await self.llm.generate_json(
            prompt=prompt, system=CITATION_VERIFICATION_SYSTEM_PROMPT, temperature=0.0
        )

    def extract_exact_quote(self, claim: str, chunk_text: str) -> str:
        """
        Attempts to extract the most relevant sentence from the chunk_text that matches the claim.
        Using difflib SequenceMatcher for a heuristic fuzzy match approach.
        """
        sentences = [s.strip() for s in chunk_text.split(".") if s.strip()]
        if not sentences:
            return ""

        best_match = ""
        highest_ratio = 0.0

        for sentence in sentences:
            ratio = difflib.SequenceMatcher(None, claim.lower(), sentence.lower()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = sentence

        # If the match is too weak, just return an empty string
        if highest_ratio < 0.2:
            return ""

        return best_match
