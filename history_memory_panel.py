"""
history_memory_panel.py
=======================
Dual-tab right-side panel for Calculation History and Memory Management.
Integrates with the main application shell and active calculator engine.
"""

from typing import Any, Optional
import customtkinter as ctk

from history import HistoryEntry
from theme import Theme, Fonts, CTkToolTip


class HistoryMemoryPanel(ctk.CTkFrame):
    """
    Collapsible right-side panel featuring two tabs:
    1. History: Shows past calculations with timestamp, click-to-load, and clear history.
    2. Memory: Shows stored memory value, MC, MR, M+, M- quick actions, and clear.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, width: int = 270, **kwargs):
        super().__init__(
            parent,
            fg_color=Theme.PANEL_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=14,
            width=width,
            **kwargs,
        )
        self.app = app
        self.active_tab: str = "History"
        self.is_collapsed: bool = False

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top Tab Bar
        self.grid_rowconfigure(1, weight=0)  # Top Divider
        self.grid_rowconfigure(2, weight=1)  # Content Area (Scrollable)
        self.grid_rowconfigure(3, weight=0)  # Bottom Divider
        self.grid_rowconfigure(4, weight=0)  # Bottom Action Button

        # 1. Header with Tab Switcher & Close Button
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        # Tab Segmented Control
        self.tab_selector = ctk.CTkSegmentedButton(
            header,
            values=["History", "Memory"],
            command=self._on_tab_change,
            font=Fonts.tab_title(),
            height=28,
        )
        self.tab_selector.set("History")
        self.tab_selector.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Close Panel Button
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=28,
            height=28,
            command=self.collapse,
            font=ctk.CTkFont(size=13, weight="bold"),
            **Theme.BTN_COPY,
        )
        close_btn.grid(row=0, column=1, sticky="e")
        CTkToolTip(close_btn, "Close panel")

        # 2. Top Divider Line
        self.top_divider = ctk.CTkFrame(self, fg_color=Theme.DIVIDER_COLOR, height=1)
        self.top_divider.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        # 3. Content Scroll Container
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=2, column=0, sticky="nsew", padx=8, pady=0)
        self.scroll_container.grid_columnconfigure(0, weight=1)

        # 4. Bottom Divider Line
        self.bottom_divider = ctk.CTkFrame(self, fg_color=Theme.DIVIDER_COLOR, height=1)
        self.bottom_divider.grid(row=3, column=0, sticky="ew", padx=12, pady=(6, 8))

        # 5. Bottom Action Button Container
        self.action_btn = ctk.CTkButton(
            self,
            text="Clear All History",
            height=36,
            command=self._on_bottom_action,
            font=Fonts.button_bottom(),
            **Theme.BTN_ACTION,
        )
        self.action_btn.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))

        # Populate initial view
        self.refresh()

    # -------------------------------------------------------------------------
    # Tab Switching & Refresh
    # -------------------------------------------------------------------------
    def _on_tab_change(self, selected_tab: str) -> None:
        self.active_tab = selected_tab
        self.refresh()

    def refresh(self) -> None:
        """Refreshes the content according to the active tab."""
        # Clear existing cards
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        if self.active_tab == "History":
            self._render_history_tab()
        else:
            self._render_memory_tab()

    # -------------------------------------------------------------------------
    # History Tab Rendering
    # -------------------------------------------------------------------------
    def _render_history_tab(self) -> None:
        self.action_btn.configure(
            text="Clear All History",
            state="normal",
            command=self._clear_history,
        )

        entries = self.app.history_mgr.get_all()
        if not entries:
            self.action_btn.configure(state="disabled")
            empty_box = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=48)

            empty_icon = ctk.CTkLabel(
                empty_box,
                text="🕒",
                font=ctk.CTkFont(size=32),
            )
            empty_icon.pack(pady=(0, 6))

            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="There's no history yet\nPerform calculations to see them here.",
                font=Fonts.history_expr(),
                text_color=Theme.TEXT_SECONDARY,
                justify="center",
            )
            empty_lbl.pack()
            return

        for entry in entries:
            card = ctk.CTkFrame(
                self.scroll_container,
                fg_color=Theme.CARD_BG,
                border_color=Theme.BORDER_COLOR,
                border_width=1,
                corner_radius=10,
            )
            card.pack(fill="x", pady=4, padx=2)
            card.grid_columnconfigure(0, weight=1)

            def make_loader(e=entry):
                return lambda event=None: self._load_history_entry(e)

            card.bind("<Button-1>", make_loader())

            time_lbl = ctk.CTkLabel(
                card,
                text=entry.timestamp,
                font=Fonts.history_time(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            time_lbl.pack(fill="x", padx=10, pady=(6, 1))
            time_lbl.bind("<Button-1>", make_loader())

            expr_lbl = ctk.CTkLabel(
                card,
                text=entry.expression,
                font=Fonts.history_expr(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="e",
            )
            expr_lbl.pack(fill="x", padx=10, pady=1)
            expr_lbl.bind("<Button-1>", make_loader())

            res_lbl = ctk.CTkLabel(
                card,
                text=f"= {entry.result}",
                font=Fonts.history_result(),
                text_color=Theme.TEXT_ACCENT,
                anchor="e",
            )
            res_lbl.pack(fill="x", padx=10, pady=(1, 8))
            res_lbl.bind("<Button-1>", make_loader())

    def _load_history_entry(self, entry: HistoryEntry) -> None:
        """Loads a previous calculation result into the active calculator."""
        self.app.engine.current_input = entry.result
        self.app.engine.previous_expression = f"{entry.expression} ="
        self.app.engine.is_new_calculation = True
        self.app.refresh_current_view()
        if hasattr(self.app.current_view, "_show_feedback"):
            self.app.current_view._show_feedback("Loaded from history", Theme.TEXT_ACCENT)

    def _clear_history(self) -> None:
        self.app.history_mgr.clear()
        self.refresh()
        if hasattr(self.app, "views_cache") and "settings" in self.app.views_cache:
            self.app.views_cache["settings"].on_activate()

    # -------------------------------------------------------------------------
    # Memory Tab Rendering
    # -------------------------------------------------------------------------
    def _render_memory_tab(self) -> None:
        self.action_btn.configure(
            text="Clear Memory (MC)",
            state="normal" if self.app.engine.has_memory else "disabled",
            command=self._clear_memory,
        )

        if not self.app.engine.has_memory:
            empty_box = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=48)

            empty_icon = ctk.CTkLabel(
                empty_box,
                text="🧠",
                font=ctk.CTkFont(size=32),
            )
            empty_icon.pack(pady=(0, 6))

            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="There's nothing saved in memory\nUse MS or M+ to save a value.",
                font=Fonts.history_expr(),
                text_color=Theme.TEXT_SECONDARY,
                justify="center",
            )
            empty_lbl.pack()
            return

        # Memory Value Display Card
        card = ctk.CTkFrame(
            self.scroll_container,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=10,
        )
        card.pack(fill="x", pady=6, padx=2)
        card.grid_columnconfigure(0, weight=1)

        mem_tag = ctk.CTkLabel(
            card,
            text="SAVED MEMORY (M)",
            font=Fonts.history_time(),
            text_color=Theme.TEXT_ACCENT,
            anchor="w",
        )
        mem_tag.pack(fill="x", padx=12, pady=(10, 2))

        val_str = self.app.engine._format_number(self.app.engine.memory_value)
        val_lbl = ctk.CTkLabel(
            card,
            text=val_str,
            font=Fonts.history_result(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="e",
        )
        val_lbl.pack(fill="x", padx=12, pady=(2, 10))

        # Quick Actions inside Memory Card
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(fill="x", padx=8, pady=(0, 10))
        btn_box.grid_columnconfigure((0, 1, 2, 3), weight=1)

        actions = [
            ("MC", self._clear_memory, "Clear memory"),
            ("MR", self._recall_memory, "Recall to display"),
            ("M+", self._add_memory, "Add current input to memory"),
            ("M-", self._subtract_memory, "Subtract current input from memory"),
        ]

        for idx, (label, cmd, tip) in enumerate(actions):
            b = ctk.CTkButton(
                btn_box,
                text=label,
                command=cmd,
                font=Fonts.button_memory(),
                height=26,
                **Theme.BTN_MEMORY,
            )
            b.grid(row=0, column=idx, padx=2, sticky="ew")
            CTkToolTip(b, tip)

    def _clear_memory(self) -> None:
        self.app.engine.memory_clear()
        self.app.refresh_current_view()
        self.refresh()

    def _recall_memory(self) -> None:
        self.app.engine.memory_recall()
        self.app.refresh_current_view()
        self.refresh()

    def _add_memory(self) -> None:
        self.app.engine.memory_add()
        self.app.refresh_current_view()
        self.refresh()

    def _subtract_memory(self) -> None:
        self.app.engine.memory_subtract()
        self.app.refresh_current_view()
        self.refresh()

    def _on_bottom_action(self) -> None:
        if self.active_tab == "History":
            self._clear_history()
        else:
            self._clear_memory()

    # -------------------------------------------------------------------------
    # Panel Visibility Controls
    # -------------------------------------------------------------------------
    def toggle(self) -> bool:
        """Toggles visibility of the right panel."""
        if self.winfo_viewable():
            self.collapse()
        else:
            self.expand()
        return self.is_collapsed

    def collapse(self) -> None:
        self.grid_remove()
        self.is_collapsed = True
        if hasattr(self.app, "history_toggle_btn"):
            self.app.history_toggle_btn.configure(
                fg_color=Theme.BTN_TOOL["fg_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )

    def expand(self) -> None:
        self.grid()
        self.is_collapsed = False
        self.refresh()
        if hasattr(self.app, "history_toggle_btn"):
            self.app.history_toggle_btn.configure(
                fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
                text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
            )
