# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:41:24 2025

@author: zshaf
"""

import tkinter as tk
from tkinter import ttk
from config import FRACTAL_SHADERS, FRACTAL_LABELS, COLOR_SCHEMES, MESH_LABELS

class ControlPanel:
    """
    A simple tkinter-based GUI for controlling fractal parameters.

    Usage:
        # In your main application:
        from gui import ControlPanel
        # FRACTAL_LABELS and COLOR_SCHEMES defined in your main
        panel = ControlPanel(viewer, FRACTAL_LABELS, COLOR_SCHEMES)
    """
    def __init__(self, viewer, fractal_labels: dict = FRACTAL_LABELS, color_schemes: list = COLOR_SCHEMES, mesh_labels: list = MESH_LABELS):
        self.viewer = viewer
        self.fractal_labels = fractal_labels
        self.color_schemes = color_schemes
        self.mesh_labels = mesh_labels

        # Build Tk root
        self.root = tk.Tk()
        self.root.title("Fractal Controls")

        # ----- Fractal Type -----
        ttk.Label(self.root, text="Fractal Type:").pack(anchor='w', padx=10, pady=(10, 0))
        self.fractal_var = tk.StringVar(value=self.viewer.current_shader_key)
        for key, label in self.fractal_labels.items():
            ttk.Radiobutton(
                self.root,
                text=label,
                variable=self.fractal_var,
                value=key,
                command=self._on_fractal_change
            ).pack(anchor='w', padx=20)

        # ----- Color Scheme -----
        ttk.Label(self.root, text="Color Scheme:").pack(anchor='w', padx=10, pady=(10, 0))
        self.color_var = tk.StringVar(value=self.color_schemes[self.viewer.color_scheme])
        combo = ttk.Combobox(
            self.root,
            values=self.color_schemes,
            textvariable=self.color_var,
            state='readonly'
        )
        combo.pack(fill='x', padx=20)
        combo.bind('<<ComboboxSelected>>', self._on_color_change)
        
        # --- mesh picker (buttons) ---
        ttk.Label(self.root, text="Mesh:").pack(anchor='w', padx=10, pady=(10,0))
        self.mesh_var = tk.StringVar(value=viewer.current_mesh)
        for key, label in MESH_LABELS.items():
            ttk.Radiobutton(
                self.root,
                text=label,
                variable=self.mesh_var,
                value=key,
                command=self._on_mesh_change
            ).pack(anchor='w', padx=20)


        # ----- Toggles -----
        self._add_checkbox(
            label="Animate (A)",
            var_name='animate',
            row_pad=(10, 0)
        )
        self._add_checkbox(
            label="Audio Anim (O)",
            var_name='audioAnimate'
        )
        self._add_checkbox(
            label="Shadows (X)",
            var_name='enable_shadows'
        )

        # ----- Actions -----
        ttk.Button(
            self.root,
            text="Reset View (R)",
            command=self._on_reset
        ).pack(fill='x', padx=10, pady=(20, 5))
# =============================================================================
#         ttk.Button(
#             self.root,
#             text="Save Screenshot",
#             command=self.viewer.save_screenshot
#         ).pack(fill='x', padx=10, pady=(0, 10))
# 
# =============================================================================
    def _add_checkbox(self, label, var_name, row_pad=(0,0)):
        """
        Helper to add a Checkbutton bound to viewer.<var_name>
        """
        var = tk.BooleanVar(value=getattr(self.viewer, var_name))
        setattr(self, f"{var_name}_var", var)
        ttk.Checkbutton(
            self.root,
            text=label,
            variable=var,
            command=lambda: setattr(self.viewer, var_name, var.get())
        ).pack(anchor='w', padx=10, pady=row_pad)

    def _on_fractal_change(self):
        key = self.fractal_var.get()
        self.viewer._switch_fractal(key)
        # keep GUI in sync
        self.viewer._sync_gui()

    def _on_color_change(self, event):
        idx = self.color_schemes.index(self.color_var.get())
        self.viewer.color_scheme = idx
        self.viewer._sync_gui()

    def _on_reset(self):
        self.viewer._reset_view()
        self.viewer._sync_gui()
        
    def _on_mesh_change(self, *_):
        choice = self.mesh_var.get()
        self.viewer._switch_mesh(choice)
        self.viewer._sync_gui()

    def mainloop(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()
