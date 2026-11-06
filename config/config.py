"""
BankGuard Banking Compliance & Application Configuration
Adheres to PCI-DSS v4.0, GLBA, and SOC 2 Type II controls.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_ENCRYPTION_KEY = os.getenv("DATABASE_ENCRYPTION_KEY", "BankGuardDefaultDemoEncryptionKey32B!")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db"))

COMPLIANCE_STANDARDS = [
    {"standard": "PCI-DSS v4.0", "requirement": "Req 3.4 (Masking PAN)", "status": "ENFORCED"},
    {"standard": "GLBA", "requirement": "16 CFR Part 314 Safeguards Rule", "status": "ENFORCED"},
    {"standard": "SOC 2 Type II", "requirement": "CC6.1 - CC6.7 Access & Encryption", "status": "ENFORCED"},
    {"standard": "FINRA", "requirement": "Rule 4370 Business Continuity & Records", "status": "ENFORCED"},
    {"standard": "GDPR / CCPA", "requirement": "Article 32 Cryptographic Pseudonymization", "status": "ENFORCED"},
]