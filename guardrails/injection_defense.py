"""
Prompt Injection Defense & Adversarial Guardrails
Protects banking models from system prompt exfiltration, jailbreaks, and privilege escalation.
"""

import re
from typing import Tuple, List


class InjectionDefenseGuardrail:
    ADVERSARIAL_PATTERNS = [
        (r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", "INSTRUCTION_OVERRIDE"),
        (r"(?i)\b(?:system\s+prompt|developer\s+mode|dan\s+mode)\b", "PRIVILEGE_ESCALATION"),
        (r"(?i)\b(?:dump|reveal|print|show)\s+(?:all\s+)?(?:database|ssn)\b", "DATA_EXFILTRATION"),
    ]

    @classmethod
    def evaluate_prompt(cls, prompt: str) -> Tuple[bool, List[str]]:
        threats = []
        for pattern, threat_name in cls.ADVERSARIAL_PATTERNS:
            if re.search(pattern, prompt):
                threats.append(threat_name)
        return len(threats) == 0, threats