from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestType(str, Enum):
    demo_request = "demo_request"
    support_issue = "support_issue"
    pricing_inquiry = "pricing_inquiry"
    proposal_request = "proposal_request"
    implementation_request = "implementation_request"
    data_request = "data_request"
    content_request = "content_request"
    sales_lead = "sales_lead"
    other = "other"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class ExtractionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    request_type: RequestType
    priority: Priority
    budget_amount: Optional[float] = Field(default=None, ge=0)
    budget_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    deadline_iso: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    needs_human_review: bool
