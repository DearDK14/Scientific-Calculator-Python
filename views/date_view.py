"""
views/date_view.py
==================
Date Calculation Mode View.

Features:
- Sub-mode 1: Date Difference (total days, elapsed weeks, and exact calendar years + months + days)
- Sub-mode 2: Add or Subtract Days (with month-end clipping and leap year safety)
- Sub-mode 3: Date Information (day of week, leap year status, day of year, days remaining, ISO week, quarter)
- Interactive date pickers (Month, Day, Year) with quick preset buttons ('Today', '+1 Month', '+1 Year')
- Real-time input validation with user-friendly error banners
- Full Dark / Light theme synchronization
"""

import calendar
from datetime import date
from typing import Any, Dict, Optional, Tuple
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from date_engine import DateEngine


class DateCalcView(BaseModeView):
    """
    Modular Date Calculation mode view with 3 sub-modes:
    1. Difference between dates
    2. Add or subtract days/months/years
    3. Calendar date information
    """

    MONTH_NAMES = [calendar.month_name[m] for m in range(1, 13)]

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)

        self.current_tab = "Difference"
        self._build_ui()

    def get_title(self) -> str:
        return "Date Calculation"

    def get_mode_id(self) -> str:
        return "date_calc"

    def handles_keyboard(self) -> bool:
        return False

    def on_activate(self) -> None:
        self._recalculate_active_tab()

    # -------------------------------------------------------------------------
    # UI Layout Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Tab Selector Bar
        self.grid_rowconfigure(1, weight=1)  # Tab Content Area

        # 1. Top Sub-mode Selector
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        self.tab_selector = ctk.CTkSegmentedButton(
            top_bar,
            values=["Difference", "Add / Subtract", "Date Info"],
            command=self._on_tab_changed,
            font=Fonts.button_bottom(),
            selected_color=Theme.ACCENT_PRIMARY,
            selected_hover_color=Theme.ACCENT_HOVER,
            height=34,
        )
        self.tab_selector.set("Difference")
        self.tab_selector.grid(row=0, column=0, sticky="ew")

        # 2. Main Content Container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=4, pady=0)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Build the 3 Sub-mode Frames
        self.frame_diff = self._build_difference_tab(self.content_container)
        self.frame_add_sub = self._build_add_sub_tab(self.content_container)
        self.frame_info = self._build_info_tab(self.content_container)

        self._show_tab("Difference")

    # -------------------------------------------------------------------------
    # Tab 1: Date Difference
    # -------------------------------------------------------------------------
    def _build_difference_tab(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        # Dates Container (From & To)
        pickers_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        pickers_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        pickers_card.grid_columnconfigure(0, weight=1)

        # From Date Picker
        today = date.today()
        self.from_pickers = self._create_date_picker_group(
            pickers_card,
            row=0,
            label_text="From Date:",
            initial_date=today,
            on_change=lambda: self._calculate_difference(),
        )

        # Divider line
        divider = ctk.CTkFrame(pickers_card, height=1, fg_color=Theme.BORDER_COLOR)
        divider.grid(row=1, column=0, sticky="ew", padx=14, pady=8)

        # To Date Picker (default +30 days)
        future_default = today.replace(day=min(today.day, 28))
        if today.month == 12:
            future_default = future_default.replace(year=today.year + 1, month=1)
        else:
            future_default = future_default.replace(month=today.month + 1)

        self.to_pickers = self._create_date_picker_group(
            pickers_card,
            row=2,
            label_text="To Date:",
            initial_date=future_default,
            on_change=lambda: self._calculate_difference(),
        )

        # Results Card
        self.diff_result_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.diff_result_card.grid(row=1, column=0, sticky="nsew", pady=0)
        self.diff_result_card.grid_columnconfigure(0, weight=1)

        # Main Big Days Label
        self.diff_main_label = ctk.CTkLabel(
            self.diff_result_card,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=Theme.TEXT_ACCENT,
        )
        self.diff_main_label.pack(pady=(20, 4))

        # Secondary Details
        self.diff_detail_calendar = ctk.CTkLabel(
            self.diff_result_card,
            text="",
            font=Fonts.button_bottom(),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.diff_detail_calendar.pack(pady=2)

        self.diff_detail_weeks = ctk.CTkLabel(
            self.diff_result_card,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.diff_detail_weeks.pack(pady=2)

        self.diff_error_label = ctk.CTkLabel(
            self.diff_result_card,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ERROR,
        )
        self.diff_error_label.pack(pady=(4, 16))

        return frame

    # -------------------------------------------------------------------------
    # Tab 2: Add or Subtract Days
    # -------------------------------------------------------------------------
    def _build_add_sub_tab(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        controls_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        controls_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls_card.grid_columnconfigure(0, weight=1)

        # Start Date Picker
        self.addsub_start_pickers = self._create_date_picker_group(
            controls_card,
            row=0,
            label_text="Starting Date:",
            initial_date=date.today(),
            on_change=lambda: self._calculate_add_sub(),
        )

        divider = ctk.CTkFrame(controls_card, height=1, fg_color=Theme.BORDER_COLOR)
        divider.grid(row=1, column=0, sticky="ew", padx=14, pady=8)

        # Operation Selector (+ / -) and Duration Inputs
        inputs_row = ctk.CTkFrame(controls_card, fg_color="transparent")
        inputs_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 14))

        self.op_seg = ctk.CTkSegmentedButton(
            inputs_row,
            values=["➕ Add", "➖ Subtract"],
            command=lambda v: self._calculate_add_sub(),
            font=Fonts.label_badge(),
            selected_color=Theme.ACCENT_PRIMARY,
            selected_hover_color=Theme.ACCENT_HOVER,
            width=140,
        )
        self.op_seg.set("➕ Add")
        self.op_seg.pack(side="left", padx=(0, 14))

        # Years, Months, Days Entry Fields
        def create_num_entry(label_txt: str, default_val: str):
            box = ctk.CTkFrame(inputs_row, fg_color="transparent")
            box.pack(side="left", padx=6)
            ctk.CTkLabel(box, text=label_txt, font=Fonts.label_badge(), text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
            entry = ctk.CTkEntry(box, width=54, height=30, font=Fonts.button_bottom(), justify="center")
            entry.insert(0, default_val)
            entry.pack(side="left")
            entry.bind("<KeyRelease>", lambda e: self._calculate_add_sub())
            return entry

        self.entry_years = create_num_entry("Years:", "0")
        self.entry_months = create_num_entry("Months:", "0")
        self.entry_days = create_num_entry("Days:", "30")

        # Result Card
        self.addsub_result_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.addsub_result_card.grid(row=1, column=0, sticky="nsew", pady=0)
        self.addsub_result_card.grid_columnconfigure(0, weight=1)

        self.addsub_res_title = ctk.CTkLabel(
            self.addsub_result_card,
            text="Resulting Date",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.addsub_res_title.pack(pady=(20, 2))

        self.addsub_res_date = ctk.CTkLabel(
            self.addsub_result_card,
            text="--",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=Theme.TEXT_ACCENT,
        )
        self.addsub_res_date.pack(pady=4)

        self.addsub_res_dayname = ctk.CTkLabel(
            self.addsub_result_card,
            text="",
            font=Fonts.button_bottom(),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.addsub_res_dayname.pack(pady=2)

        self.addsub_error_label = ctk.CTkLabel(
            self.addsub_result_card,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ERROR,
        )
        self.addsub_error_label.pack(pady=(4, 16))

        return frame

    # -------------------------------------------------------------------------
    # Tab 3: Date Information
    # -------------------------------------------------------------------------
    def _build_info_tab(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        picker_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        picker_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        picker_card.grid_columnconfigure(0, weight=1)

        self.info_date_pickers = self._create_date_picker_group(
            picker_card,
            row=0,
            label_text="Select Date:",
            initial_date=date.today(),
            on_change=lambda: self._calculate_info(),
        )

        # Info Grid
        self.info_grid_card = ctk.CTkFrame(
            frame,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.info_grid_card.grid(row=1, column=0, sticky="nsew", pady=0)

        # 2 columns x 3 rows of metric cards
        self.info_grid_card.grid_columnconfigure((0, 1), weight=1)

        self.metric_widgets: Dict[str, Dict[str, ctk.CTkLabel]] = {}
        metrics = [
            ("weekday", "Day of the Week", 0, 0),
            ("leap_year", "Leap Year", 0, 1),
            ("day_of_year", "Day of the Year", 1, 0),
            ("remaining", "Days Remaining", 1, 1),
            ("week_no", "ISO Week Number", 2, 0),
            ("quarter", "Calendar Quarter", 2, 1),
        ]

        for key, title, r, c in metrics:
            m_card = ctk.CTkFrame(
                self.info_grid_card,
                fg_color=Theme.PANEL_BG,
                border_color=Theme.BORDER_COLOR,
                border_width=1,
                corner_radius=8,
            )
            m_card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            t_lbl = ctk.CTkLabel(
                m_card,
                text=title,
                font=Fonts.label_badge(),
                text_color=Theme.TEXT_SECONDARY,
            )
            t_lbl.pack(anchor="w", padx=10, pady=(8, 2))

            v_lbl = ctk.CTkLabel(
                m_card,
                text="--",
                font=Fonts.button_bottom(),
                text_color=Theme.TEXT_ACCENT,
            )
            v_lbl.pack(anchor="w", padx=10, pady=(0, 8))

            self.metric_widgets[key] = {"title": t_lbl, "val": v_lbl}

        return frame

    # -------------------------------------------------------------------------
    # Helper: Date Picker Component
    # -------------------------------------------------------------------------
    def _create_date_picker_group(
        self,
        parent: ctk.CTkFrame,
        row: int,
        label_text: str,
        initial_date: date,
        on_change: Any,
    ) -> Dict[str, Any]:
        """Creates an interactive Month / Day / Year dropdown group with a 'Today' quick button."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=0, sticky="ew", padx=14, pady=8)

        # Label
        header_lbl = ctk.CTkLabel(
            container,
            text=label_text,
            width=100,
            font=Fonts.button_bottom(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        header_lbl.pack(side="left", padx=(0, 10))

        # Month OptionMenu
        month_var = ctk.StringVar(value=calendar.month_name[initial_date.month])
        month_opt = ctk.CTkOptionMenu(
            container,
            values=self.MONTH_NAMES,
            variable=month_var,
            width=120,
            height=30,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
            command=lambda v: on_change(),
        )
        month_opt.pack(side="left", padx=(0, 6))

        # Day OptionMenu (1..31)
        day_var = ctk.StringVar(value=str(initial_date.day))
        day_opt = ctk.CTkOptionMenu(
            container,
            values=[str(d) for d in range(1, 32)],
            variable=day_var,
            width=65,
            height=30,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
            command=lambda v: on_change(),
        )
        day_opt.pack(side="left", padx=(0, 6))

        # Year Entry
        year_entry = ctk.CTkEntry(
            container,
            width=65,
            height=30,
            font=Fonts.button_bottom(),
            justify="center",
        )
        year_entry.insert(0, str(initial_date.year))
        year_entry.pack(side="left", padx=(0, 10))
        year_entry.bind("<KeyRelease>", lambda e: on_change())

        # Quick 'Today' Button
        today_btn = ctk.CTkButton(
            container,
            text="Today",
            width=55,
            height=28,
            font=Fonts.label_badge(),
            command=lambda: self._set_picker_date(pickers_dict, date.today(), on_change),
            **Theme.BTN_TOOL,
        )
        today_btn.pack(side="left")

        pickers_dict = {
            "month_var": month_var,
            "day_var": day_var,
            "year_entry": year_entry,
        }
        return pickers_dict

    def _set_picker_date(self, pickers: Dict[str, Any], dt: date, on_change: Any) -> None:
        pickers["month_var"].set(calendar.month_name[dt.month])
        pickers["day_var"].set(str(dt.day))
        pickers["year_entry"].delete(0, "end")
        pickers["year_entry"].insert(0, str(dt.year))
        on_change()

    def _read_picker_date(self, pickers: Dict[str, Any]) -> Tuple[bool, Optional[date], Optional[str]]:
        month_name = pickers["month_var"].get()
        month = self.MONTH_NAMES.index(month_name) + 1 if month_name in self.MONTH_NAMES else 1

        try:
            day = int(pickers["day_var"].get())
        except ValueError:
            return False, None, "Invalid day selection"

        year_str = pickers["year_entry"].get().strip()
        try:
            year = int(year_str)
        except ValueError:
            return False, None, f"Invalid year: '{year_str}'"

        return DateEngine.validate_date_parts(year, month, day)

    # -------------------------------------------------------------------------
    # Calculations & Updates
    # -------------------------------------------------------------------------
    def _on_tab_changed(self, tab_name: str) -> None:
        self.current_tab = tab_name
        self._show_tab(tab_name)
        self._recalculate_active_tab()

    def _show_tab(self, tab_name: str) -> None:
        self.frame_diff.grid_remove()
        self.frame_add_sub.grid_remove()
        self.frame_info.grid_remove()

        if tab_name == "Difference":
            self.frame_diff.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "Add / Subtract":
            self.frame_add_sub.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "Date Info":
            self.frame_info.grid(row=0, column=0, sticky="nsew")

    def _recalculate_active_tab(self) -> None:
        if self.current_tab == "Difference":
            self._calculate_difference()
        elif self.current_tab == "Add / Subtract":
            self._calculate_add_sub()
        elif self.current_tab == "Date Info":
            self._calculate_info()

    # 1. Calculate Difference
    def _calculate_difference(self) -> None:
        valid_from, d_from, err_from = self._read_picker_date(self.from_pickers)
        if not valid_from:
            self.diff_main_label.configure(text="--")
            self.diff_detail_calendar.configure(text="")
            self.diff_detail_weeks.configure(text="")
            self.diff_error_label.configure(text=err_from)
            return

        valid_to, d_to, err_to = self._read_picker_date(self.to_pickers)
        if not valid_to:
            self.diff_main_label.configure(text="--")
            self.diff_detail_calendar.configure(text="")
            self.diff_detail_weeks.configure(text="")
            self.diff_error_label.configure(text=err_to)
            return

        self.diff_error_label.configure(text="")
        res = DateEngine.calculate_date_difference(d_from, d_to)

        # Main Days Readout
        days_unit = "day" if res.total_days == 1 else "days"
        self.diff_main_label.configure(text=f"{res.total_days:,} {days_unit}")

        # Calendar breakdown
        self.diff_detail_calendar.configure(text=res.summary_text())

        # Weeks breakdown
        if res.total_days > 0:
            weeks_str = f"{res.weeks} {'week' if res.weeks == 1 else 'weeks'}"
            if res.remaining_days_in_week > 0:
                weeks_str += f", {res.remaining_days_in_week} {'day' if res.remaining_days_in_week == 1 else 'days'}"
            self.diff_detail_weeks.configure(text=f"Equivalent to: {weeks_str}")
        else:
            self.diff_detail_weeks.configure(text="")

    # 2. Calculate Add / Subtract
    def _calculate_add_sub(self) -> None:
        valid_start, d_start, err_start = self._read_picker_date(self.addsub_start_pickers)
        if not valid_start:
            self.addsub_res_date.configure(text="--")
            self.addsub_res_dayname.configure(text="")
            self.addsub_error_label.configure(text=err_start)
            return

        try:
            years = int(self.entry_years.get().strip() or "0")
            months = int(self.entry_months.get().strip() or "0")
            days = int(self.entry_days.get().strip() or "0")
        except ValueError:
            self.addsub_res_date.configure(text="--")
            self.addsub_res_dayname.configure(text="")
            self.addsub_error_label.configure(text="Duration fields must contain integer numbers")
            return

        op = "add" if "Add" in self.op_seg.get() else "subtract"
        success, res, err = DateEngine.add_subtract_date(d_start, years=years, months=months, days=days, operation=op)

        if not success or res is None:
            self.addsub_res_date.configure(text="--")
            self.addsub_res_dayname.configure(text="")
            self.addsub_error_label.configure(text=err or "Calculation error")
            return

        self.addsub_error_label.configure(text="")
        self.addsub_res_date.configure(text=res.formatted_result())
        self.addsub_res_dayname.configure(text=f"Day of the week: {res.resulting_date.strftime('%A')}")

    # 3. Calculate Date Info
    def _calculate_info(self) -> None:
        valid, d_target, err = self._read_picker_date(self.info_date_pickers)
        if not valid or d_target is None:
            for key in self.metric_widgets:
                self.metric_widgets[key]["val"].configure(text="--")
            return

        info = DateEngine.get_date_info(d_target)
        self.metric_widgets["weekday"]["val"].configure(text=info.day_of_week)
        self.metric_widgets["leap_year"]["val"].configure(text=info.leap_year_description())
        self.metric_widgets["day_of_year"]["val"].configure(text=f"Day {info.day_of_year} of {info.total_days_in_year}")
        self.metric_widgets["remaining"]["val"].configure(text=f"{info.days_remaining_in_year} days remaining")
        self.metric_widgets["week_no"]["val"].configure(text=f"Week {info.week_number}")
        self.metric_widgets["quarter"]["val"].configure(text=f"Quarter {info.quarter} (Q{info.quarter})")
