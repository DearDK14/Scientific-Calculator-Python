"""
history.py
==========
Calculation history manager with optional local JSON persistence.

This module keeps track of prior calculations so users can review previous
formulas and results, or click them in the GUI to reload them into the calculator.
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class HistoryEntry:
    """Represents a single recorded calculation."""
    expression: str
    result: str
    timestamp: str

    def display_text(self) -> str:
        """Returns formatted string for list display."""
        return f"{self.expression} = {self.result}"


class HistoryManager:
    """
    Manages calculation history with maximum capacity and JSON file persistence.
    """

    def __init__(self, storage_file: Optional[str] = None, max_entries: int = 100):
        """
        Initializes the HistoryManager.

        :param storage_file: Path to JSON file for persistent history.
                             If None, defaults to 'calculator_history.json' next to this file.
        :param max_entries: Maximum number of history records to keep.
        """
        self.max_entries = max_entries
        if storage_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_file = os.path.join(base_dir, "calculator_history.json")
        else:
            self.storage_file = storage_file

        self._entries: List[HistoryEntry] = []
        self.load_from_disk()

    def add(self, expression: str, result: str) -> HistoryEntry:
        """
        Records a new calculation into history.

        :param expression: The mathematical expression (e.g. '15 + 25 * 2')
        :param result: The evaluated answer (e.g. '65')
        :return: Newly created HistoryEntry
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = HistoryEntry(expression=expression, result=result, timestamp=timestamp)

        # Prepend so latest calculation appears at the top
        self._entries.insert(0, entry)

        # Truncate if exceeding maximum allowed entries
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[: self.max_entries]

        self.save_to_disk()
        return entry

    def get_all(self) -> List[HistoryEntry]:
        """Returns the list of all history entries (newest first)."""
        return list(self._entries)

    def get_latest(self) -> Optional[HistoryEntry]:
        """Returns the most recent calculation, or None if history is empty."""
        return self._entries[0] if self._entries else None

    def clear(self) -> None:
        """Clears all history entries both from memory and the local disk file."""
        self._entries.clear()
        self.save_to_disk()

    def delete_entry(self, index: int) -> bool:
        """Deletes an entry at the given index. Returns True if successful."""
        if 0 <= index < len(self._entries):
            self._entries.pop(index)
            self.save_to_disk()
            return True
        return False

    def save_to_disk(self) -> None:
        """Saves current history entries to the JSON file safely."""
        try:
            data = [asdict(e) for e in self._entries]
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[HistoryManager] Warning: could not save history to disk: {e}")

    def load_from_disk(self) -> None:
        """Loads historical calculations from the JSON file if it exists."""
        if not os.path.exists(self.storage_file):
            self._entries = []
            return

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._entries = [
                    HistoryEntry(
                        expression=item.get("expression", ""),
                        result=item.get("result", ""),
                        timestamp=item.get("timestamp", ""),
                    )
                    for item in data
                    if "expression" in item and "result" in item
                ]
        except Exception as e:
            print(f"[HistoryManager] Warning: could not load history from disk: {e}")
            self._entries = []
