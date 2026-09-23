"""
Minimal evidence ledger (v0.1).

Python standard library only.
Records claims, observations, and evidence.
Does not decide truth; it only stores structured records.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(payload: Any) -> str:
    """Deterministic SHA-256 of canonical JSON."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Ledger:
    """In-memory append-only ledger for v0.1 experiments."""

    def __init__(self) -> None:
        self.claims: Dict[str, Dict[str, Any]] = {}
        self.observations: Dict[str, Dict[str, Any]] = {}
        self.evidence: Dict[str, Dict[str, Any]] = {}
        self.verifications: List[Dict[str, Any]] = []

    def record_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        if "claim_id" not in claim:
            raise ValueError("claim_id required")
        claim = dict(claim)
        claim.setdefault("schema_version", "0.1")
        claim.setdefault("created_at", _utcnow())
        self.claims[claim["claim_id"]] = claim
        return claim

    def record_observation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        if "observation_id" not in observation:
            raise ValueError("observation_id required")
        if "evidence_state" not in observation:
            raise ValueError("evidence_state required")
        observation = dict(observation)
        observation.setdefault("schema_version", "0.1")
        self.observations[observation["observation_id"]] = observation
        return observation

    def record_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        if "evidence_id" not in evidence:
            raise ValueError("evidence_id required")
        if "evidence_state" not in evidence:
            raise ValueError("evidence_state required")
        evidence = dict(evidence)
        evidence.setdefault("schema_version", "0.1")
        # If content_hash is missing, compute from the value-bearing fields.
        if "content_hash" not in evidence:
            hashable = {
                k: evidence.get(k)
                for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
            }
            evidence["content_hash"] = content_hash(hashable)
        self.evidence[evidence["evidence_id"]] = evidence
        return evidence

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        return self.evidence.get(evidence_id)

    def list_evidence_for_claim(self, claim_id: str) -> List[Dict[str, Any]]:
        # Simple scan; sufficient for v0.1
        result = []
        for ev in self.evidence.values():
            obs_id = ev.get("observation_id")
            if obs_id and obs_id in self.observations:
                if self.observations[obs_id].get("claim_id") == claim_id:
                    result.append(ev)
        return result
