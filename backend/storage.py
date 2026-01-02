import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from models import TestResult, TestSummary
from config import settings


class TestStorage:
    def __init__(self):
        self.history_file = Path(settings.test_history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.write_text("[]")

    def _read_history(self) -> List[dict]:
        with open(self.history_file, "r") as f:
            return json.load(f)

    def _write_history(self, history: List[dict]):
        # Keep only the latest max_history_items
        if len(history) > settings.max_history_items:
            history = history[-settings.max_history_items:]
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2, default=str)

    def save_test(self, test: TestResult):
        history = self._read_history()
        test_dict = test.model_dump(mode='json')

        # Update existing or append new
        existing_idx = next((i for i, t in enumerate(history) if t["test_id"] == test.test_id), None)
        if existing_idx is not None:
            history[existing_idx] = test_dict
        else:
            history.append(test_dict)

        self._write_history(history)

    def get_test(self, test_id: str) -> Optional[TestResult]:
        history = self._read_history()
        test_dict = next((t for t in history if t["test_id"] == test_id), None)
        if test_dict:
            return TestResult(**test_dict)
        return None

    def get_all_tests(self) -> List[TestSummary]:
        history = self._read_history()
        # Return in reverse order (newest first)
        return [TestSummary(**t) for t in reversed(history)]

    def delete_test(self, test_id: str):
        history = self._read_history()
        history = [t for t in history if t["test_id"] != test_id]
        self._write_history(history)


storage = TestStorage()
