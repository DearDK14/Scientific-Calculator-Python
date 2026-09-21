"""
graphing_view.py
================
Graphing Calculator mode view for the Modern Desktop Calculator.
Embeds interactive 2D Cartesian Matplotlib canvas inside CustomTkinter, supporting:
- Multi-function plotting with customized line styles and colors
- Interactive pan, zoom in/out, scroll-wheel zoom, and view reset
- Function visibility toggling and individual plot removal
- Safe AST formula validation with error messaging
- Dynamic Dark / Light theme synchronization
- Responsive window resizing
"""

from typing import Any, Dict, List, Optional, Tuple
import customtkinter as ctk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from graphing_engine import GraphingEngine, PlotFunction


class GraphingView(BaseModeView):
    """
    Modular 2D Cartesian Graphing Calculator mode view.
    Hosts Matplotlib plotting canvas, multi-function manager, and navigation toolbar.
    """

    STYLE_MAP = {
        "Solid": "-",
        "Dashed": "--",
        "Dotted": ":",
        "Dash-dot": "-.",
    }
    REVERSE_STYLE_MAP = {v: k for k, v in STYLE_MAP.items()}

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)

        self.graph_engine = GraphingEngine()

        # Viewport boundaries (Cartesian range)
        self.x_min: float = -10.0
        self.x_max: float = 10.0
        self.y_min: float = -10.0
        self.y_max: float = 10.0

        # Interactive state
        self.is_panning: bool = False
        self._pan_start: Optional[Tuple[float, float]] = None
        self._error_timer = None

        self._build_ui()

        # Add initial sample plot (sin(x)) for instant visual delight
        self._add_function_string("sin(x)")

    def get_title(self) -> str:
        return "Graphing"

    def get_mode_id(self) -> str:
        return "graphing"

    def handles_keyboard(self) -> bool:
        # Returns False so typing inside entry doesn't trigger global calc shortcuts
        return False

    def on_activate(self) -> None:
        """Adapts figure colors to current theme and re-plots."""
        self._apply_theme_to_figure()
        self._redraw_plot()

    # -------------------------------------------------------------------------
    # UI Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Controls Container
        self.grid_rowconfigure(1, weight=1)  # Split Content: Canvas & Functions

        # 1. Top Controls Header
        self._build_controls_header(self)

        # 2. Main Graph Body
        self._build_graph_body(self)

    def _build_controls_header(self, parent: ctk.CTkFrame) -> None:
        controls_frame = ctk.CTkFrame(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        controls_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))
        controls_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Formula Input & Action
        input_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        input_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 6))
        input_row.grid_columnconfigure(1, weight=1)

        y_label = ctk.CTkLabel(
            input_row,
            text="y =",
            font=Fonts.button_bottom(),
            text_color=Theme.TEXT_ACCENT,
        )
        y_label.grid(row=0, column=0, padx=(0, 8))

        self.func_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Enter expression, e.g. sin(x), x^2, cos(x), log(x)...",
            font=Fonts.sidebar_item(),
            height=34,
        )
        self.func_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.func_entry.bind("<Return>", lambda e: self._on_add_button())

        # Line style dropdown
        self.style_var = ctk.StringVar(value="Solid")
        self.style_dropdown = ctk.CTkOptionMenu(
            input_row,
            values=list(self.STYLE_MAP.keys()),
            variable=self.style_var,
            width=100,
            height=34,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
        )
        self.style_dropdown.grid(row=0, column=2, padx=(0, 8))
        CTkToolTip(self.style_dropdown, "Select curve line style")

        # Plot button
        self.plot_btn = ctk.CTkButton(
            input_row,
            text="+ Plot",
            width=80,
            height=34,
            command=self._on_add_button,
            font=Fonts.button_scientific(),
            **Theme.BTN_EQUALS,
        )
        self.plot_btn.grid(row=0, column=3)
        CTkToolTip(self.plot_btn, "Add function to graph (Enter)")

        # Row 1: Presets, Navigation Tools & Status Message
        tools_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        tools_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        tools_row.grid_columnconfigure(6, weight=1)

        # Quick Preset Chips
        presets = [("x²", "x^2"), ("sin(x)", "sin(x)"), ("cos(x)", "cos(x)"), ("log(x)", "log(x)"), ("√x", "sqrt(x)")]
        for idx, (lbl, expr) in enumerate(presets):
            chip = ctk.CTkButton(
                tools_row,
                text=lbl,
                width=54,
                height=26,
                command=lambda e=expr: self._apply_preset(e),
                font=Fonts.label_badge(),
                **Theme.BTN_TOOL,
            )
            chip.grid(row=0, column=idx, padx=(0, 4))
            CTkToolTip(chip, f"Plot {lbl}")

        # Toolbar Buttons: Zoom In, Zoom Out, Pan, Reset, Clear
        col_start = 7
        self.zoom_in_btn = ctk.CTkButton(
            tools_row,
            text="🔍+",
            width=38,
            height=26,
            command=self._zoom_in,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.zoom_in_btn.grid(row=0, column=col_start, padx=(0, 4))
        CTkToolTip(self.zoom_in_btn, "Zoom In (scale 1.25x)")

        self.zoom_out_btn = ctk.CTkButton(
            tools_row,
            text="🔍-",
            width=38,
            height=26,
            command=self._zoom_out,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.zoom_out_btn.grid(row=0, column=col_start + 1, padx=(0, 4))
        CTkToolTip(self.zoom_out_btn, "Zoom Out (scale 0.8x)")

        self.pan_btn = ctk.CTkButton(
            tools_row,
            text="✋ Pan",
            width=58,
            height=26,
            command=self._toggle_pan,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.pan_btn.grid(row=0, column=col_start + 2, padx=(0, 4))
        CTkToolTip(self.pan_btn, "Toggle drag-to-pan mode")

        self.reset_btn = ctk.CTkButton(
            tools_row,
            text="↺ Reset",
            width=58,
            height=26,
            command=self._reset_view,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.reset_btn.grid(row=0, column=col_start + 3, padx=(0, 4))
        CTkToolTip(self.reset_btn, "Reset view to [-10, 10]")

        self.clear_btn = ctk.CTkButton(
            tools_row,
            text="🗑️ Clear",
            width=58,
            height=26,
            command=self._clear_all,
            font=Fonts.label_badge(),
            **Theme.BTN_ACTION,
        )
        self.clear_btn.grid(row=0, column=col_start + 4)
        CTkToolTip(self.clear_btn, "Clear all plotted functions")

        # Status / Coordinates / Error Label
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text="Ready • Scroll or drag to explore",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 6))

    def _build_graph_body(self, parent: ctk.CTkFrame) -> None:
        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=0)

        # 1. Matplotlib Canvas Frame
        self.canvas_frame = ctk.CTkFrame(
            body,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        # Matplotlib Figure & Subplot
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self._apply_theme_to_figure()

        # Canvas widget integration
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)

        # Matplotlib mouse event listeners
        self.canvas.mpl_connect("scroll_event", self._on_scroll_zoom)
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_motion)

        # 2. Function Cards List (Below Canvas)
        self.func_list_frame = ctk.CTkScrollableFrame(
            body,
            orientation="horizontal",
            height=58,
            fg_color=Theme.PANEL_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=10,
        )
        self.func_list_frame.grid(row=1, column=0, sticky="ew")

    # -------------------------------------------------------------------------
    # Theme & Styling
    # -------------------------------------------------------------------------
    def _apply_theme_to_figure(self) -> None:
        """Adapts the Matplotlib figure styling to match the current application theme."""
        is_dark = self.app.theme_mgr.current_mode == "dark"

        bg_color = "#0B1120" if is_dark else "#FFFFFF"
        axis_color = "#94A3B8" if is_dark else "#475569"
        grid_color = "#1E293B" if is_dark else "#E2E8F0"
        zero_line_color = "#475569" if is_dark else "#94A3B8"

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        # Spines
        self.ax.spines["left"].set_color(axis_color)
        self.ax.spines["bottom"].set_color(axis_color)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        # Ticks & labels
        self.ax.tick_params(colors=axis_color, which="both", labelsize=9)
        self.ax.xaxis.label.set_color(axis_color)
        self.ax.yaxis.label.set_color(axis_color)

        self._zero_line_color = zero_line_color
        self._grid_color = grid_color

    # -------------------------------------------------------------------------
    # Plotting & Viewport Rendering
    # -------------------------------------------------------------------------
    def _redraw_plot(self) -> None:
        """Clears and redraws all visible mathematical functions on the Cartesian grid."""
        self.ax.clear()
        self._apply_theme_to_figure()

        # Set viewport boundaries
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)

        # Draw Cartesian Grid
        self.ax.grid(True, linestyle="--", alpha=0.5, color=self._grid_color)

        # Draw Primary X and Y Coordinate Axes (x=0, y=0)
        self.ax.axhline(0, color=self._zero_line_color, linewidth=1.2, zorder=1)
        self.ax.axvline(0, color=self._zero_line_color, linewidth=1.2, zorder=1)

        # Generate sampling array across the current X viewport
        resolution = 1000
        x_vals = np.linspace(self.x_min, self.x_max, resolution)

        # Plot each active function
        functions = self.graph_engine.get_functions()
        for fn in functions:
            if not fn.visible:
                continue

            y_vals, err = GraphingEngine.evaluate_function(fn.clean_expr, x_vals)
            if err:
                fn.error = err
                continue

            fn.error = None
            self.ax.plot(
                x_vals,
                y_vals,
                color=fn.color,
                linestyle=fn.line_style,
                linewidth=2.0,
                label=f"y = {fn.expression}",
                zorder=2,
            )

        self.canvas.draw_idle()
        self._refresh_function_cards()

    def _refresh_function_cards(self) -> None:
        """Renders interactive badge cards for each active function."""
        for widget in self.func_list_frame.winfo_children():
            widget.destroy()

        functions = self.graph_engine.get_functions()
        if not functions:
            empty_lbl = ctk.CTkLabel(
                self.func_list_frame,
                text="No active plots • Enter a formula above to plot",
                font=Fonts.label_badge(),
                text_color=Theme.TEXT_SECONDARY,
            )
            empty_lbl.pack(side="left", padx=12, pady=12)
            return

        for fn in functions:
            card = ctk.CTkFrame(
                self.func_list_frame,
                fg_color=Theme.CARD_BG,
                border_color=Theme.BORDER_COLOR,
                border_width=1,
                corner_radius=8,
            )
            card.pack(side="left", padx=4, pady=4)

            # Visibility Checkbox
            check_var = ctk.BooleanVar(value=fn.visible)
            chk = ctk.CTkCheckBox(
                card,
                text="",
                variable=check_var,
                command=lambda f_id=fn.id: self._toggle_function_vis(f_id),
                width=20,
                checkbox_width=18,
                checkbox_height=18,
            )
            chk.pack(side="left", padx=(8, 4))
            CTkToolTip(chk, "Toggle plot visibility")

            # Color Bar
            color_bar = ctk.CTkFrame(
                card,
                fg_color=fn.color,
                width=10,
                height=22,
                corner_radius=3,
            )
            color_bar.pack(side="left", padx=(0, 6))

            # Expression Label
            label_text = f"y = {fn.expression}"
            expr_lbl = ctk.CTkLabel(
                card,
                text=label_text,
                font=Fonts.label_badge(),
                text_color=Theme.TEXT_PRIMARY,
            )
            expr_lbl.pack(side="left", padx=(0, 6))

            # Line Style Selector
            curr_style_label = self.REVERSE_STYLE_MAP.get(fn.line_style, "Solid")
            style_opt = ctk.CTkOptionMenu(
                card,
                values=list(self.STYLE_MAP.keys()),
                command=lambda val, f_id=fn.id: self._on_style_change(f_id, val),
                width=80,
                height=22,
                font=Fonts.label_badge(),
                fg_color=Theme.BTN_TOOL["fg_color"],
                button_color=Theme.BTN_TOOL["hover_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )
            style_opt.set(curr_style_label)
            style_opt.pack(side="left", padx=(0, 6))

            # Delete Button
            del_btn = ctk.CTkButton(
                card,
                text="✕",
                width=22,
                height=22,
                command=lambda f_id=fn.id: self._remove_function(f_id),
                font=ctk.CTkFont(size=11, weight="bold"),
                **Theme.BTN_COPY,
            )
            del_btn.pack(side="left", padx=(0, 6))
            CTkToolTip(del_btn, "Remove function")

    # -------------------------------------------------------------------------
    # Function Management Event Handlers
    # -------------------------------------------------------------------------
    def _on_add_button(self) -> None:
        expr = self.func_entry.get().strip()
        if not expr:
            return
        self._add_function_string(expr)
        self.func_entry.delete(0, "end")

    def _apply_preset(self, expr_str: str) -> None:
        self._add_function_string(expr_str)

    def _add_function_string(self, expr_str: str) -> None:
        selected_style = self.STYLE_MAP.get(self.style_var.get(), "-")
        fn, err = self.graph_engine.add_function(expr_str, line_style=selected_style)
        if err:
            self._show_error(err)
            return

        self._show_status(f"Plotted: y = {expr_str}")
        self._redraw_plot()

    def _remove_function(self, func_id: str) -> None:
        self.graph_engine.remove_function(func_id)
        self._redraw_plot()

    def _toggle_function_vis(self, func_id: str) -> None:
        self.graph_engine.toggle_visibility(func_id)
        self._redraw_plot()

    def _on_style_change(self, func_id: str, style_name: str) -> None:
        line_style = self.STYLE_MAP.get(style_name, "-")
        self.graph_engine.set_line_style(func_id, line_style)
        self._redraw_plot()

    def _clear_all(self) -> None:
        self.graph_engine.clear_functions()
        self._redraw_plot()
        self._show_status("All plots cleared")

    # -------------------------------------------------------------------------
    # Zoom, Pan & Navigation Controls
    # -------------------------------------------------------------------------
    def _zoom_in(self) -> None:
        self._zoom(0.8)

    def _zoom_out(self) -> None:
        self._zoom(1.25)

    def _zoom(self, factor: float, center_x: Optional[float] = None, center_y: Optional[float] = None) -> None:
        """Scales viewport boundaries around a center point (defaulting to viewport center)."""
        if center_x is None:
            center_x = (self.x_min + self.x_max) / 2.0
        if center_y is None:
            center_y = (self.y_min + self.y_max) / 2.0

        x_half = (self.x_max - self.x_min) * factor / 2.0
        y_half = (self.y_max - self.y_min) * factor / 2.0

        self.x_min = center_x - x_half
        self.x_max = center_x + x_half
        self.y_min = center_y - y_half
        self.y_max = center_y + y_half

        self._redraw_plot()

    def _toggle_pan(self) -> None:
        self.is_panning = not self.is_panning
        if self.is_panning:
            self.pan_btn.configure(
                fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
                text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
            )
            self._show_status("Pan mode ON: Click and drag on graph to pan")
        else:
            self.pan_btn.configure(
                fg_color=Theme.BTN_TOOL["fg_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )
            self._show_status("Pan mode OFF")

    def _reset_view(self) -> None:
        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -10.0, 10.0
        self._redraw_plot()
        self._show_status("View reset to [-10, 10]")

    # -------------------------------------------------------------------------
    # Interactive Matplotlib Mouse Events
    # -------------------------------------------------------------------------
    def _on_scroll_zoom(self, event) -> None:
        """Scroll wheel zoom centered at cursor position."""
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        factor = 0.85 if event.button == "up" else 1.15
        self._zoom(factor, center_x=event.xdata, center_y=event.ydata)

    def _on_mouse_press(self, event) -> None:
        """Initiates drag panning on mouse press."""
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        if self.is_panning or event.button in (2, 3):  # Middle click or pan mode
            self._pan_start = (event.xdata, event.ydata)

    def _on_mouse_release(self, event) -> None:
        """Terminates drag panning."""
        self._pan_start = None

    def _on_mouse_motion(self, event) -> None:
        """Updates cursor coordinates readout and pans if dragging."""
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        # Coordinate readout
        coord_str = f"x = {event.xdata:+.3f}, y = {event.ydata:+.3f}"

        if self._pan_start is not None:
            dx = event.xdata - self._pan_start[0]
            dy = event.ydata - self._pan_start[1]
            self.x_min -= dx
            self.x_max -= dx
            self.y_min -= dy
            self.y_max -= dy
            self._redraw_plot()
        else:
            self.status_label.configure(text=f"Cursor: {coord_str}", text_color=Theme.TEXT_SECONDARY)

    # -------------------------------------------------------------------------
    # Error & Status Messaging
    # -------------------------------------------------------------------------
    def _show_error(self, message: str) -> None:
        self.status_label.configure(text=f"⚠️ {message}", text_color=Theme.BTN_ACTION["fg_color"])
        if self._error_timer:
            self.after_cancel(self._error_timer)
        self._error_timer = self.after(3500, lambda: self.status_label.configure(
            text="Ready", text_color=Theme.TEXT_SECONDARY
        ))

    def _show_status(self, message: str) -> None:
        self.status_label.configure(text=f"✓ {message}", text_color=Theme.TEXT_SUCCESS)
        if self._error_timer:
            self.after_cancel(self._error_timer)
        self._error_timer = self.after(2500, lambda: self.status_label.configure(
            text="Ready", text_color=Theme.TEXT_SECONDARY
        ))
