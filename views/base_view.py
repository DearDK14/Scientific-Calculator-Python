"""
base_view.py
============
Defines the abstract interface for all calculator modes, converters, and utility views.

Each view represents a distinct mode (e.g. Standard, Scientific, Currency, Settings)
hosted inside the application shell's central content area.
"""

from typing import Any, Optional
import customtkinter as ctk


class BaseModeView(ctk.CTkFrame):
    """
    Abstract base class for all calculator and converter modes.
    Ensures modularity, clean lifecycle management, and in-place view transitions.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app

    def get_title(self) -> str:
        """Returns the human-readable display title (e.g. 'Scientific', 'Standard')."""
        raise NotImplementedError

    def get_mode_id(self) -> str:
        """Returns unique identifier string for the mode."""
        raise NotImplementedError

    def on_activate(self) -> None:
        """Called whenever the user switches into this mode."""
        pass

    def on_deactivate(self) -> None:
        """Called before leaving this view for another mode."""
        pass

    def handles_keyboard(self) -> bool:
        """Returns True if this view intercepts global physical keyboard input."""
        return False

    def handle_key_action(self, action_type: str, value: Optional[str] = None) -> None:
        """
        Receives routed keyboard actions from the main application shell.

        :param action_type: 'number', 'operator', 'decimal', 'bracket', 'equals',
                            'backspace', 'clear', 'all_clear', 'copy', 'paste', 'select_all'
        :param value: Optional character or operand string (e.g. '5', '+')
        """
        pass
