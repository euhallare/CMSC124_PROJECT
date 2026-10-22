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

    #panel 2 — text editor

    def _build_editor(self, parent):
        frame = self._titled_frame(parent, "② Text Editor")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

        #line numbers + editor side by side
        inner = tk.Frame(frame, bg=BG_EDITOR)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.line_numbers = tk.Text(
            inner, width=4,
            bg="#16162a", fg=FG_DIM,
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED, padx=4,
            selectbackground="#16162a",
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        sb = tk.Scrollbar(inner, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            inner,
            bg=BG_EDITOR, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
            padx=8, pady=4,
            undo=True, wrap=tk.NONE,
            yscrollcommand=sb.set,
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._sync_scroll)

        self.editor.bind("<KeyRelease>", self._update_line_numbers)
        self.editor.bind("<MouseWheel>", self._on_mousewheel)

        #horizontal scrollbar
        hb = tk.Scrollbar(frame, orient=tk.HORIZONTAL,
                           command=self.editor.xview)
        hb.pack(fill=tk.X, padx=6)
        self.editor.config(xscrollcommand=hb.set)

    def _sync_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_mousewheel(self, event):
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_line_numbers(self, event=None):
        content = self.editor.get("1.0", tk.END)
        n_lines = content.count("\n")
        nums = "\n".join(str(i) for i in range(1, n_lines + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", nums)
        self.line_numbers.config(state=tk.DISABLED)

    #panel 3 — token list

    def _build_token_table(self, parent):
        frame = self._titled_frame(parent, "③ List of Tokens")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        cols = ("line", "type", "value")
        self.token_tree = self._make_treeview(frame, cols,
                                              headings=("Line", "Type", "Value"),
                                              widths=(50, 130, 200))

    #panel 4 — symbol table 

    def _build_symbol_table(self, parent):
        frame = self._titled_frame(parent, "④ Symbol Table")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 2))

        cols = ("name", "type", "value")
        self.symbol_tree = self._make_treeview(frame, cols,
                                               headings=("Variable", "Type", "Value"),
                                               widths=(120, 100, 160))

    #panel 5 — console
    
    def _build_console(self, parent):
        frame = self._titled_frame(parent, "⑤ Console")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

        self.console = scrolledtext.ScrolledText(
            frame,
            bg="#0d0d1a", fg=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED,
            padx=8, pady=4,
            height=6,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 2))
        self.console.tag_config("error", foreground=FG_RED)
        self.console.tag_config("ok",    foreground=FG_GREEN)
        self.console.tag_config("dim",   foreground=FG_DIM)

        #input row (for GIMMEH — ML3)
        input_row = tk.Frame(frame, bg=BG_PANEL)
        input_row.pack(fill=tk.X, padx=6, pady=(0, 6))

        tk.Label(input_row, text="Input:", bg=BG_PANEL,
                 fg=FG_DIM, font=FONT_UI).pack(side=tk.LEFT)

        self.console_input = tk.Entry(
            input_row,
            bg=BG_EDITOR, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
        )
        self.console_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

        send_btn = tk.Button(
            input_row, text="Send",
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI, relief=tk.FLAT,
            padx=8, cursor="hand2",
            activebackground="#4a4a6a",
        )
        send_btn.pack(side=tk.LEFT)

    #helpers

    def _titled_frame(self, parent, title: str) -> tk.LabelFrame:
        return tk.LabelFrame(
            parent, text=f"  {title}  ",
            bg=BG_PANEL, fg=FG_ACCENT,
            font=FONT_HEAD,
            relief=tk.FLAT,
            bd=1,
        )

    def _make_treeview(self, parent, cols, headings, widths) -> ttk.Treeview:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                        background=BG_TABLE, foreground=FG_TEXT,
                        fieldbackground=BG_TABLE, rowheight=24,
                        font=FONT_CODE)
        style.configure("Dark.Treeview.Heading",
                        background=BG_HEADER, foreground=FG_ACCENT,
                        font=FONT_HEAD, relief=tk.FLAT)
        style.map("Dark.Treeview",
                  background=[("selected", BG_HEADER)],
                  foreground=[("selected", FG_TEXT)])

        container = tk.Frame(parent, bg=BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        vsb = tk.Scrollbar(container, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(container, columns=cols, show="headings",
                            style="Dark.Treeview",
                            yscrollcommand=vsb.set)
        vsb.config(command=tree.yview)

        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor=tk.W, minwidth=40)

        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    #helpers

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open LOLCode file",
            filetypes=[("LOLCode files", "*.lol"), ("All files", "*.*")],
        )
        if not path:
            return
        self._load_file(path)

    def _load_file(self, path: str):
        try:
            with open(path, "r") as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return

        self.current_file = path
        filename = os.path.basename(path)
        self.file_label.config(text=filename)
        self.explorer_label.config(text=path, fg=FG_TEXT)
        self.root.title(f"LOLCode Interpreter — {filename}")

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", source)
        self._update_line_numbers()
        self._log(f"Loaded: {path}\n", tag="dim")