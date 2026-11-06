"""
PII Redaction & Cryptographic Tokenization Guardrail
Compliant with PCI-DSS Req 3.4 (PAN Masking), GLBA Safeguards, and GDPR Article 32.
"""

import re
import uuid
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DetectedEntity:
    entity_type: str
    original_value: str
    masked_value: str
    token: str
    confidence: float
    regulatory_framework: str


class BankingPIIGuardrail:
    def __init__(self):
        self._token_vault: Dict[str, str] = {}

    def mask_and_tokenize(self, text: str) -> Tuple[str, List[DetectedEntity]]:
        entities: List[DetectedEntity] = []
        sanitized = text
        cc_pattern = r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{15,16}\b"
        for match in list(re.finditer(cc_pattern, text)):
            val = match.group()
            token = f"[CARD_TOKEN_{uuid.uuid4().hex[:8].upper()}]"
            masked = f"****-****-****-{val[-4:]}"
            sanitized = sanitized.replace(val, token)
            entities.append(DetectedEntity("PAN", val, masked, token, 0.99, "PCI-DSS"))
        return sanitized, entities