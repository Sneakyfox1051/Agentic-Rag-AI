# evaluation/evaluator.py
from typing import List, Dict, Any
from datetime import datetime
import math
import json


class KnowledgeEvaluator:
    def __init__(self, llm_client, max_age_days: int = 365):
        """
        llm_client must expose:
        generate(prompt: str) -> str
        """
        self.llm = llm_client
        self.max_age_days = max_age_days

    def evaluate(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        scores: List[float]
    ) -> Dict[str, Any]:
        freshness = self._freshness_score(metadatas)
        conflict = self._detect_conflict(chunks)
        confidence = self._confidence_score(
            freshness=freshness,
            conflict=conflict,
            scores=scores
        )

        return {
            "freshness": round(freshness, 2),
            "conflict": conflict,
            "confidence": round(confidence, 2)
        }

    # ------------------------
    # Freshness
    # ------------------------
    def _freshness_score(self, metadatas: List[Dict[str, Any]]) -> float:
        """
        Scores freshness based on document age.
        1.0 = very recent
        0.0 = too old
        """
        now = datetime.utcnow()
        ages = []

        for meta in metadatas:
            ts = meta.get("ingested_at")
            if not ts:
                continue
            try:
                doc_time = datetime.fromisoformat(ts)
                age_days = (now - doc_time).days
                ages.append(age_days)
            except Exception:
                continue

        if not ages:
            return 0.3  # unknown freshness → conservative

        avg_age = sum(ages) / len(ages)

        # exponential decay
        freshness = math.exp(-avg_age / self.max_age_days)
        return min(max(freshness, 0.0), 1.0)

    # ------------------------
    # Conflict Detection
    # ------------------------
    def _detect_conflict(self, chunks: List[str]) -> bool:
        """
        Uses LLM to detect semantic contradictions.
        Returns True if conflict is detected.
        """
        if len(chunks) < 2:
            return False

        prompt = f"""
You are a contradiction detection agent.

Below are excerpts retrieved from internal documents.

Your task:
- Determine if there are semantic conflicts or contradictions
- Answer ONLY with valid JSON
- No explanations

JSON FORMAT:
{{
  "conflict": true | false
}}

DOCUMENT EXCERPTS:
"""

        for i, chunk in enumerate(chunks[:5]):
            prompt += f"\n[{i+1}] {chunk}\n"

        raw = self.llm.generate(prompt)

        try:
            parsed = json.loads(raw)
            return bool(parsed.get("conflict", False))
        except Exception:
            # Fail safe: assume conflict if LLM misbehaves
            return True

    # ------------------------
    # Confidence
    # ------------------------
    def _confidence_score(
        self,
        freshness: float,
        conflict: bool,
        scores: List[float]
    ) -> float:
        """
        Combines retrieval strength + freshness + conflict penalty.
        """
        if not scores:
            return 0.0

        # Normalize FAISS L2 scores (lower is better)
        norm_scores = [1 / (1 + s) for s in scores]
        relevance = sum(norm_scores) / len(norm_scores)

        confidence = (
            0.5 * relevance +
            0.4 * freshness -
            0.4 * (1.0 if conflict else 0.0)
        )

        return min(max(confidence, 0.0), 1.0)
