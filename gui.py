"""
LOLCODE Interpreter GUI
CMSC 124 - S-3L | Group EJDB

Main GUI application using tkinter.
Wires together the lexer (ML1), parser (ML2), and interpreter (ML3).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os

from lexer import Lexer, TT_NEWLINE, TT_EOF


#colour palette
BG_DARK    = "#1e1e2e"   # main background
BG_PANEL   = "#27273a"   # panel / frame background
BG_EDITOR  = "#1a1a2a"   # code editor background
BG_TABLE   = "#22223a"   # treeview background
BG_HEADER  = "#313152"   # treeview heading background
FG_TEXT    = "#cdd6f4"   # primary text
FG_DIM     = "#7f849c"   # secondary / dim text
FG_ACCENT  = "#89b4fa"   # accent (blue)
FG_GREEN   = "#a6e3a1"   # success / green
FG_RED     = "#f38ba8"   # error / red
FG_YELLOW  = "#f9e2af"   # warning / yellow
FONT_CODE  = ("Consolas", 11)
FONT_UI    = ("Segoe UI", 10)
FONT_HEAD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 12, "bold")


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("LOLCode Interpreter — CMSC 124 Group EJDB")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)

        self.current_file: str | None = None

        self._build_ui()

    #UI construction 

    def _build_ui(self):
        """Build all panels."""
        #top toolbar
        self._build_toolbar()

        #main pane: left column | right column
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                              bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        #left column: file explorer + text editor
        left = tk.Frame(main, bg=BG_DARK)
        main.add(left, minsize=350)

        self._build_file_explorer(left)
        self._build_editor(left)

        #right column: token list | symbol table | console
        right = tk.Frame(main, bg=BG_DARK)
        main.add(right, minsize=400)

        self._build_token_table(right)
        self._build_symbol_table(right)
        self._build_console(right)

    #toolbar

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=48)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))
        bar.pack_propagate(False)

        title = tk.Label(bar, text="LOLCode Interpreter",
                         bg=BG_PANEL, fg=FG_ACCENT,
                         font=FONT_TITLE)
        title.pack(side=tk.LEFT, padx=12)

        #Run button — right side
        self.run_btn = tk.Button(
            bar, text="▶  Execute / Run",
            command=self._run,
            bg=FG_GREEN, fg=BG_DARK,
            font=FONT_HEAD,
            relief=tk.FLAT, padx=16, pady=4,
            cursor="hand2",
            activebackground="#7dc97a", activeforeground=BG_DARK,
        )
        self.run_btn.pack(side=tk.RIGHT, padx=12, pady=8)

        #Open file button
        open_btn = tk.Button(
            bar, text="📂  Open File",
            command=self._open_file,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI,
            relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
        )
        open_btn.pack(side=tk.RIGHT, padx=4, pady=8)

        #current file label
        self.file_label = tk.Label(bar, text="No file selected",
                                   bg=BG_PANEL, fg=FG_DIM, font=FONT_UI)
        self.file_label.pack(side=tk.RIGHT, padx=12)

    #panel 1 — file explorer

    def _build_file_explorer(self, parent):
        frame = self._titled_frame(parent, "① File Explorer")
        frame.pack(fill=tk.X, padx=4, pady=(4, 2))

        inner = tk.Frame(frame, bg=BG_PANEL)
        inner.pack(fill=tk.X, padx=6, pady=6)

        self.explorer_label = tk.Label(
            inner,
            text="No file loaded — click Open File or drag a .lol file",
            bg=BG_PANEL, fg=FG_DIM, font=FONT_UI,
            anchor="w", wraplength=340,
        )
        self.explorer_label.pack(fill=tk.X)