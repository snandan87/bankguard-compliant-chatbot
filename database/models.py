"""
Database Entities & Data Models for Banking Vault
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class CustomerAccount:
    account_id: str
    customer_id: str
    account_type: str
    account_number_masked: str
    balance: float
    loan_amount: float = 18500.00
    credit_card_masked: str = "•••• 3451"
    pan: str = "ABCDE1234F"


@dataclass
class CustomerProfile:
    customer_id: str
    full_name: str
    balance: float
    credit_card_no: str
    account_no: str
    loan_amount: float
    pan: str


@dataclass
class AuditTrailEntry:
    event_id: str
    timestamp: str
    actor: str
    action: str
    details: Dict[str, Any]
    ip_address: str
    previous_hash: str
    event_hash: str