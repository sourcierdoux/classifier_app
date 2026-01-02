from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from enum import Enum


class ClassifierMode(str, Enum):
    SR = "sr"
    QF = "qf"
    BOTH = "both"


class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RunClassifierRequest(BaseModel):
    source_path: str = Field(..., description="Path to source file/folder containing emails")
    out_path: str = Field(..., description="Output path for results")
    mode: ClassifierMode = Field(default=ClassifierMode.BOTH, description="Classification mode")
    use_filter: bool = Field(default=True, description="Use aggressive filters on dataframe")
    async_mode: bool = Field(default=True, description="Run parallel predictions")
    max_concurrency: int = Field(default=20, ge=1, le=50, description="Max concurrent predictions")


class TestResult(BaseModel):
    test_id: str
    status: TestStatus
    source_path: str
    out_path: str
    mode: ClassifierMode
    use_filter: bool
    async_mode: bool
    max_concurrency: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_emails: Optional[int] = None
    processed_emails: Optional[int] = None
    sr_positive: Optional[int] = None
    sr_negative: Optional[int] = None
    category_breakdown: Optional[dict] = None


class TestSummary(BaseModel):
    test_id: str
    status: TestStatus
    source_path: str
    mode: ClassifierMode
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_emails: Optional[int] = None
