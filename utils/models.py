from dataclasses import dataclass, asdict, field
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum

ClassifierMode = Literal['sr', 'qf', 'both']
TestStatus = Literal['pending', 'running', 'completed', 'failed']


@dataclass
class TestResult:
    test_id: str
    status: TestStatus
    source_path: str
    out_path: str
    mode: ClassifierMode
    use_filter: bool
    async_mode: bool
    max_concurrency: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    total_emails: Optional[int] = None
    processed_emails: Optional[int] = None
    sr_positive: Optional[int] = None
    sr_negative: Optional[int] = None
    category_breakdown: Optional[dict] = None
    file_analyses: Optional[List[dict]] = None  # Per-file detailed analysis

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
