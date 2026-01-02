import json
from pathlib import Path
from typing import List, Optional
from .models import TestResult


class TestStorage:
    def __init__(self, storage_path: str = "./data/test_history.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")

    def _read_history(self) -> List[dict]:
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_history(self, history: List[dict], max_items: int = 100):
        # Keep only the latest max_items
        if len(history) > max_items:
            history = history[-max_items:]
        with open(self.storage_path, "w") as f:
            json.dump(history, f, indent=2)

    def save_test(self, test: TestResult):
        history = self._read_history()
        test_dict = test.to_dict()

        # Update existing or append new
        existing_idx = next(
            (i for i, t in enumerate(history) if t["test_id"] == test.test_id),
            None
        )
        if existing_idx is not None:
            history[existing_idx] = test_dict
        else:
            history.append(test_dict)

        self._write_history(history)

    def get_test(self, test_id: str) -> Optional[TestResult]:
        history = self._read_history()
        test_dict = next((t for t in history if t["test_id"] == test_id), None)
        if test_dict:
            return TestResult.from_dict(test_dict)
        return None

    def get_all_tests(self) -> List[TestResult]:
        history = self._read_history()
        # Return in reverse order (newest first)
        return [TestResult.from_dict(t) for t in reversed(history)]

    def delete_test(self, test_id: str):
        history = self._read_history()
        history = [t for t in history if t["test_id"] != test_id]
        self._write_history(history)


# Global storage instance
storage = TestStorage()
