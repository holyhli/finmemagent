from uagents import Model
from pydantic import Field
from typing import List, Dict, Any
from datetime import datetime, UTC

class TxBatch(Model):
    user_id: str
    # flattened transactions after transform
    transactions: List[Dict[str, Any]]
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

class RiskProfileRequest(Model):
    user_id: str
    transactions: List[Dict[str, Any]]

class RiskProfileResponse(Model):
    user_id: str
    risk_bucket: str
    risk_score: float
    reasoning: str

class PortfolioRequest(Model):
    user_id: str
    profile: RiskProfileResponse
    total_balance: float        # from bank account
    assets: List[Dict[str, Any]]  # the static asset list

class PortfolioResponse(Model):
    user_id: str
    portfolio: Dict[str, Any]   # full JSON the frontend expects
    reasoning: str
