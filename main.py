"""
main.py
=======
Modern Desktop Calculator Application Shell.
Built with Python 3 and CustomTkinter.

Features:
- Resizable desktop application with original modern visual identity
- Hamburger menu button (☰) toggling collapsible left navigation sidebar
- Categorized Sidebar:
  * Calculator: Standard, Scientific, Graphing, Programmer, Date Calculation
  * Converter: Currency, Volume, Length, Weight and Mass, Temperature, Energy,
               Area, Speed, Time, Power, Data, Pressure, Angle
  * Bottom: Settings
- Dynamic central content area (in-place view loading without opening unnecessary windows)
- Right-side dual-tab panel for Calculation History and Memory Management
- Theme System: Dark and Light modes with local persistence
- Full physical keyboard support routed to the active calculator mode
"""

import os
import sys
from typing import Dict, Optional, Tuple
import customtkinter as ctk

# Ensure current directory is in search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from calculator import CalculatorEngine
from history import HistoryManager
from history_memory_panel import HistoryMemoryPanel
from sidebar import SidebarNavigation
from theme import Theme, Fonts, ThemeManager, CTkToolTip
from views import (
    BaseModeView,
    ScientificView,
    StandardView,
    PlaceholderView,
    SettingsView,
)


class ModernCalculatorApp(ctk.CTk):
    """
    Main desktop shell window for the Modern Calculator.
    Orchestrates the collapsible sidebar, central content area, and right-side
    History & Memory panel while managing state, themes, and global keyboard shortcuts.
    """

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------------------
        # 1. State & Logic Setup
        # ---------------------------------------------------------------------
        self.history_mgr = HistoryManager(max_entries=50)
        self.engine = CalculatorEngine(history_manager=self.history_mgr)
        self.theme_mgr = ThemeManager(initial_mode="dark")

        # View Cache for in-place transitions
        self.views_cache: Dict[str, BaseModeView] = {}
        self.current_view: Optional[BaseModeView] = None
        self.current_mode_id: str = ""

        # ---------------------------------------------------------------------
        # 2. Window Configuration
        # ---------------------------------------------------------------------
        self.title("Modern Calculator")
        self._set_window_icon()
        self.configure(fg_color=Theme.WINDOW_BG)
        self.geometry("980x780")
        self.minsize(720, 620)
        self.resizable(True, True)

        # ---------------------------------------------------------------------
        # 3. Layout Construction
        # ---------------------------------------------------------------------
        self._build_shell_layout()
        self._bind_keyboard_shortcuts()

        # Load initial default mode (Scientific)
        self.switch_mode("scientific")

    def _set_window_icon(self) -> None:
        """Sets application window icon if available."""
        ico_path = os.path.join(current_dir, "assets", "icons", "calculator.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Shell Layout Construction
    # -------------------------------------------------------------------------
    def _build_shell_layout(self) -> None:
        """
        Constructs the master 2-row x 3-column shell layout:
        Row 0: Top Header (Hamburger, Mode Title, DEG/RAD, History Toggle, Theme Toggle)
        Row 1: Body:
          - Col 0: Collapsible Left Sidebar (SidebarNavigation)
          - Col 1: Central Content Area (Holds active calculator/converter/settings view)
          - Col 2: Collapsible Right Panel (HistoryMemoryPanel)
        """
        # Master grid weights
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Body
        self.grid_columnconfigure(0, weight=0)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)  # Central Content
        self.grid_columnconfigure(2, weight=0)  # Right History / Memory

        # ----------------- Top Header Bar -----------------
        self.header_bar = ctk.CTkFrame(self, fg_color="transparent", height=44)
        self.header_bar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=14, pady=(10, 6))
        self.header_bar.grid_columnconfigure(0, weight=0)  # Left controls
        self.header_bar.grid_columnconfigure(1, weight=1)  # Spacer
        self.header_bar.grid_columnconfigure(2, weight=0)  # Right controls

        # Left Header Container
        header_left = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        header_left.grid(row=0, column=0, sticky="w")

        # Hamburger Menu Button (☰)
        self.hamburger_btn = ctk.CTkButton(
            header_left,
            text="☰",
            width=36,
            height=34,
            command=self._toggle_sidebar,
            font=ctk.CTkFont(size=18, weight="bold"),
            **Theme.BTN_TOOL,
        )
        self.hamburger_btn.pack(side="left", padx=(0, 10))
        CTkToolTip(self.hamburger_btn, "Toggle navigation menu (☰)")

        # Current Mode Title Label
        self.title_label = ctk.CTkLabel(
            header_left,
            text="Scientific",
            font=Fonts.mode_title(),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.title_label.pack(side="left", padx=(0, 10))

        # DEG/RAD Quick Toggle Button (Visible in Scientific mode)
        self.deg_rad_btn = ctk.CTkButton(
            header_left,
            text="DEG",
            width=50,
            height=28,
            command=self._toggle_angle_mode,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        CTkToolTip(self.deg_rad_btn, "Toggle trigonometric angle unit (DEG / RAD)")

        # Right Header Container
        header_right = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        header_right.grid(row=0, column=2, sticky="e")

        # History & Memory Drawer Toggle Button
        self.history_toggle_btn = ctk.CTkButton(
            header_right,
            text="🕒 History & Memory",
            width=142,
            height=32,
            command=self._toggle_history_memory,
            font=Fonts.tab_title(),
            fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
            hover_color=Theme.BTN_SIDEBAR_ACTIVE["hover_color"],
            text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
            corner_radius=8,
        )
        self.history_toggle_btn.pack(side="left", padx=(0, 8))
        CTkToolTip(self.history_toggle_btn, "Toggle History and Memory panel")

        # Dark / Light Theme Toggle Button
        self.theme_btn = ctk.CTkButton(
            header_right,
            text="☀️" if self.theme_mgr.current_mode == "dark" else "🌙",
            width=34,
            height=32,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=15),
            **Theme.BTN_TOOL,
        )
        self.theme_btn.pack(side="left")
        CTkToolTip(self.theme_btn, "Toggle Dark / Light appearance theme")

        # ----------------- Body Components -----------------
        # 1. Left Sidebar Navigation
        self.sidebar = SidebarNavigation(
            self,
            on_mode_select=self.switch_mode,
            initial_mode="scientific",
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(12, 4), pady=(0, 12))

        # 2. Central Content Container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=1, sticky="nsew", padx=4, pady=(0, 12))
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # 3. Right History & Memory Panel
        self.history_memory_panel = HistoryMemoryPanel(
            self,
            app=self,
            width=270,
        )
        self.history_memory_panel.grid(row=1, column=2, sticky="nsew", padx=(4, 12), pady=(0, 12))

    # -------------------------------------------------------------------------
    # Mode Switching & View Caching
    # -------------------------------------------------------------------------
    def switch_mode(self, mode_id: str) -> None:
        """
        Loads the selected mode in-place within the central content container.
        Swaps views smoothly using caching without opening separate windows.
        """
        if self.current_mode_id == mode_id and self.current_view is not None:
            return

        # Check cache or instantiate view
        if mode_id not in self.views_cache:
            self.views_cache[mode_id] = self._create_view_instance(mode_id)

        target_view = self.views_cache[mode_id]

        # Deactivate and hide previous view
        if self.current_view is not None:
            self.current_view.on_deactivate()
            self.current_view.grid_remove()

        # Mount and activate new view
        self.current_view = target_view
        self.current_mode_id = mode_id
        target_view.grid(row=0, column=0, sticky="nsew")
        target_view.on_activate()

        # Update Header Title
        self.title_label.configure(text=target_view.get_title())

        # Show/Hide DEG/RAD badge button in header
        if mode_id == "scientific":
            self.deg_rad_btn.configure(text=self.engine.angle_mode)
            self.deg_rad_btn.pack(side="left", padx=(0, 10))
        else:
            self.deg_rad_btn.pack_forget()

        # Keep sidebar highlight synchronized
        self.sidebar.set_active_mode(mode_id)

    def _create_view_instance(self, mode_id: str) -> BaseModeView:
        """Instantiates a view according to the specified mode ID."""
        if mode_id == "standard":
            return StandardView(self.content_container, app=self)
        elif mode_id == "scientific":
            return ScientificView(self.content_container, app=self)
        elif mode_id == "settings":
            return SettingsView(self.content_container, app=self)
        else:
            # Placeholder for future modes & converters
            cat_name, label, icon, description = self._find_mode_metadata(mode_id)
            return PlaceholderView(
                self.content_container,
                app=self,
                mode_id=mode_id,
                title=label,
                category=cat_name,
                icon=icon,
                description=description,
            )

    def _find_mode_metadata(self, mode_id: str) -> Tuple[str, str, str, str]:
        """Finds metadata (category, display label, icon, tip) from navigation definitions."""
        for cat_name, items in SidebarNavigation.NAV_SECTIONS:
            for m_id, label, icon, tip in items:
                if m_id == mode_id:
                    return cat_name, label, icon, tip
        for m_id, label, icon, tip in SidebarNavigation.BOTTOM_SECTION:
            if m_id == mode_id:
                return "System", label, icon, tip
        return "Calculator", mode_id.capitalize(), "🧮", ""

    def refresh_current_view(self) -> None:
        """Refreshes the active view's display and header angle mode."""
        if self.current_view and hasattr(self.current_view, "_update_display"):
            self.current_view._update_display()
        if hasattr(self, "deg_rad_btn"):
            self.deg_rad_btn.configure(text=self.engine.angle_mode)

    # -------------------------------------------------------------------------
    # Header Actions & Panel Toggling
    # -------------------------------------------------------------------------
    def _toggle_sidebar(self) -> None:
        is_collapsed = self.sidebar.toggle()
        if is_collapsed:
            self.hamburger_btn.configure(
                fg_color=Theme.BTN_TOOL["fg_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )
        else:
            self.hamburger_btn.configure(
                fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
                text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
            )

    def _toggle_history_memory(self) -> None:
        is_collapsed = self.history_memory_panel.toggle()
        if is_collapsed:
            self.history_toggle_btn.configure(
                fg_color=Theme.BTN_TOOL["fg_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )
        else:
            self.history_toggle_btn.configure(
                fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
                text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
            )

    def _toggle_angle_mode(self) -> None:
        new_mode = self.engine.toggle_angle_mode()
        self.deg_rad_btn.configure(text=new_mode)
        if hasattr(self.current_view, "_update_display"):
            self.current_view._update_display()

    def _toggle_theme(self) -> None:
        self.theme_mgr.toggle()
        self._update_theme_icon()
        if "settings" in self.views_cache:
            self.views_cache["settings"].on_activate()

    def _update_theme_icon(self) -> None:
        is_dark = self.theme_mgr.current_mode == "dark"
        self.theme_btn.configure(text="☀️" if is_dark else "🌙")

    # -------------------------------------------------------------------------
    # Global Keyboard Shortcut Routing
    # -------------------------------------------------------------------------
    def _bind_keyboard_shortcuts(self) -> None:
        """Binds standard physical keyboard keys to delegate actions to the active view."""
        # Digits 0-9
        for digit in "0123456789":
            self.bind(f"<Key-{digit}>", lambda e, d=digit: self._route_key("number", d))
            self.bind(f"<KP_{digit}>", lambda e, d=digit: self._route_key("number", d))

        # Basic Operators
        self.bind("<plus>", lambda e: self._route_key("operator", "+"))
        self.bind("<KP_Add>", lambda e: self._route_key("operator", "+"))
        self.bind("<minus>", lambda e: self._route_key("operator", "-"))
        self.bind("<KP_Subtract>", lambda e: self._route_key("operator", "-"))
        self.bind("<asterisk>", lambda e: self._route_key("operator", "*"))
        self.bind("<KP_Multiply>", lambda e: self._route_key("operator", "*"))
        self.bind("<slash>", lambda e: self._route_key("operator", "/"))
        self.bind("<KP_Divide>", lambda e: self._route_key("operator", "/"))
        self.bind("<percent>", lambda e: self._route_key("operator", "%"))
        self.bind("<asciicircum>", lambda e: self._route_key("operator", "^"))

        # Decimal & Parentheses
        self.bind("<period>", lambda e: self._route_key("decimal"))
        self.bind("<KP_Decimal>", lambda e: self._route_key("decimal"))
        self.bind("<parenleft>", lambda e: self._route_key("bracket", "("))
        self.bind("<parenright>", lambda e: self._route_key("bracket", ")"))

        # Execution & Clear Actions
        self.bind("<Return>", lambda e: self._route_key("equals"))
        self.bind("<KP_Enter>", lambda e: self._route_key("equals"))
        self.bind("<equal>", lambda e: self._route_key("equals"))
        self.bind("<BackSpace>", lambda e: self._route_key("backspace"))
        self.bind("<Escape>", lambda e: self._route_key("clear"))
        self.bind("<Delete>", lambda e: self._route_key("all_clear"))

        # Clipboard & Selection
        self.bind("<Control-c>", lambda e: self._route_key("copy"))
        self.bind("<Control-C>", lambda e: self._route_key("copy"))
        self.bind("<Control-v>", lambda e: self._route_key("paste"))
        self.bind("<Control-V>", lambda e: self._route_key("paste"))
        self.bind("<Control-a>", lambda e: self._route_key("select_all"))
        self.bind("<Control-A>", lambda e: self._route_key("select_all"))

    def _route_key(self, action_type: str, value: Optional[str] = None) -> None:
        """Delegates keyboard input to active mode view if supported."""
        if self.current_view and self.current_view.handles_keyboard():
            self.current_view.handle_key_action(action_type, value)
            if hasattr(self, "history_memory_panel") and not self.history_memory_panel.is_collapsed:
                self.history_memory_panel.refresh()


# Backwards compatibility alias
ScientificCalculatorApp = ModernCalculatorApp


if __name__ == "__main__":
    app = ModernCalculatorApp()
    app.mainloop()
