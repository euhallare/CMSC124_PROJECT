"""
LOLCode Interpreter GUI
CMSC 124 - S-3L | Group EJDB

Main GUI application using tkinter.
Wires together the lexer (ML1), parser (ML2), and interpreter (ML3).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading

from lexer import Lexer, TT_NEWLINE, TT_EOF
from parser import Parser
from interpreter import Interpreter


# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK    = "#1e1e2e"
BG_PANEL   = "#27273a"
BG_EDITOR  = "#1a1a2a"
BG_TABLE   = "#22223a"
BG_HEADER  = "#313152"
FG_TEXT    = "#cdd6f4"
FG_DIM     = "#7f849c"
FG_ACCENT  = "#89b4fa"
FG_GREEN   = "#a6e3a1"
FG_RED     = "#f38ba8"
FG_YELLOW  = "#f9e2af"
FONT_CODE  = ("Consolas", 11)
FONT_UI    = ("Segoe UI", 10)
FONT_HEAD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 12, "bold")


class FileBrowserDialog(tk.Toplevel):
    """Dark-themed file picker with Back, Up, and Home navigation."""

    def __init__(self, parent: tk.Tk, initial_dir: str):
        super().__init__(parent)
        self.title("Open LOLCode File")
        self.configure(bg=BG_DARK)
        self.geometry("680x460")
        self.minsize(520, 360)
        self.transient(parent)
        self.grab_set()

        self.selected_file: str | None = None
        self.current_dir: str = os.path.abspath(initial_dir)
        self.history: list[str] = []
        self.show_all_files = tk.BooleanVar(value=False)

        self._build_dialog()
        self._populate_dir(self.current_dir, record_history=False)

        # Center over parent window
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<BackSpace>", lambda e: self._go_back())

    def _build_dialog(self):
        # Navigation bar
        nav = tk.Frame(self, bg=BG_PANEL, pady=6, padx=8)
        nav.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.back_btn = tk.Button(
            nav, text="← Back",
            command=self._go_back,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_HEAD, relief=tk.FLAT,
            padx=10, pady=3, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
            state=tk.DISABLED,
        )
        self.back_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.up_btn = tk.Button(
            nav, text="↑ Up",
            command=self._go_up,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI, relief=tk.FLAT,
            padx=10, pady=3, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
        )
        self.up_btn.pack(side=tk.LEFT, padx=(0, 4))

        home_btn = tk.Button(
            nav, text="⌂ Project",
            command=self._go_project,
            bg=BG_HEADER, fg=FG_ACCENT,
            font=FONT_UI, relief=tk.FLAT,
            padx=10, pady=3, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_ACCENT,
        )
        home_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.path_var = tk.StringVar(value=self.current_dir)
        path_entry = tk.Entry(
            nav, textvariable=self.path_var,
            bg=BG_EDITOR, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=(0, 4))
        path_entry.bind("<Return>", lambda e: self._navigate_to(self.path_var.get()))

        # File list container
        list_frame = tk.Frame(self, bg=BG_PANEL)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        vsb = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            bg=BG_EDITOR, fg=FG_TEXT,
            selectbackground=BG_HEADER, selectforeground=FG_ACCENT,
            font=FONT_CODE, relief=tk.FLAT,
            activestyle="none",
            yscrollcommand=vsb.set,
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        vsb.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self._on_double_click)
        self.listbox.bind("<Return>", self._on_double_click)

        # Bottom action bar
        bottom = tk.Frame(self, bg=BG_PANEL, pady=6, padx=8)
        bottom.pack(fill=tk.X, padx=8, pady=(4, 8))

        filter_cb = tk.Checkbutton(
            bottom, text="Show all file types",
            variable=self.show_all_files,
            command=lambda: self._populate_dir(self.current_dir, record_history=False),
            bg=BG_PANEL, fg=FG_DIM,
            selectcolor=BG_EDITOR,
            activebackground=BG_PANEL, activeforeground=FG_TEXT,
            font=FONT_UI,
        )
        filter_cb.pack(side=tk.LEFT)

        cancel_btn = tk.Button(
            bottom, text="Cancel",
            command=self.destroy,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI, relief=tk.FLAT,
            padx=14, pady=4, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(6, 0))

        open_btn = tk.Button(
            bottom, text="Open",
            command=self._confirm_selection,
            bg=FG_GREEN, fg=BG_DARK,
            font=FONT_HEAD, relief=tk.FLAT,
            padx=18, pady=4, cursor="hand2",
            activebackground="#7dc97a", activeforeground=BG_DARK,
        )
        open_btn.pack(side=tk.RIGHT)

    def _populate_dir(self, target_dir: str, record_history: bool = True):
        if not os.path.isdir(target_dir):
            messagebox.showerror("Folder Not Found", f"Cannot access:\n{target_dir}", parent=self)
            return

        if record_history and target_dir != self.current_dir:
            self.history.append(self.current_dir)

        self.current_dir = os.path.abspath(target_dir)
        self.path_var.set(self.current_dir)
        self.back_btn.config(state=tk.NORMAL if self.history else tk.DISABLED)

        self.listbox.delete(0, tk.END)
        self._entries: list[tuple[str, str]] = []  # (kind, full_path)

        try:
            items = os.listdir(self.current_dir)
        except PermissionError:
            messagebox.showerror("Access Denied", "Permission denied for this folder.", parent=self)
            return

        dirs = sorted([d for d in items if os.path.isdir(os.path.join(self.current_dir, d))], key=str.lower)
        files = sorted([f for f in items if os.path.isfile(os.path.join(self.current_dir, f))], key=str.lower)

        for d in dirs:
            full = os.path.join(self.current_dir, d)
            self._entries.append(("dir", full))
            self.listbox.insert(tk.END, f"📁  {d}/")
            self.listbox.itemconfig(tk.END, fg=FG_ACCENT)

        for f in files:
            if not self.show_all_files.get() and not f.lower().endswith(".lol"):
                continue
            full = os.path.join(self.current_dir, f)
            self._entries.append(("file", full))
            self.listbox.insert(tk.END, f"📄  {f}")
            self.listbox.itemconfig(tk.END, fg=FG_TEXT)

    def _navigate_to(self, path: str):
        path = path.strip()
        if os.path.isfile(path) and path.lower().endswith(".lol"):
            self.selected_file = path
            self.destroy()
            return
        self._populate_dir(path, record_history=True)

    def _go_back(self):
        if not self.history:
            return
        prev = self.history.pop()
        self._populate_dir(prev, record_history=False)

    def _go_up(self):
        parent = os.path.dirname(self.current_dir)
        if parent and parent != self.current_dir:
            self._populate_dir(parent, record_history=True)

    def _go_project(self):
        self._populate_dir(os.getcwd(), record_history=True)

    def _on_double_click(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        kind, full_path = self._entries[sel[0]]
        if kind == "dir":
            self._populate_dir(full_path, record_history=True)
        else:
            self.selected_file = full_path
            self.destroy()

    def _confirm_selection(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        kind, full_path = self._entries[sel[0]]
        if kind == "dir":
            self._populate_dir(full_path, record_history=True)
        else:
            self.selected_file = full_path
            self.destroy()


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("LOLCode Interpreter — CMSC 124 Group EJDB")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1280x800")
        self.root.minsize(960, 620)

        self.current_file: str | None = None

        # ── GIMMEH input synchronisation ──────────────────────────────────
        self._waiting_for_input: bool = False
        self._input_event: threading.Event = threading.Event()
        self._input_value: str = ""

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        # 1. Top Toolbar
        self._build_toolbar()

        # 2. Fixed Bottom Input Row (packed BEFORE main panes so it is always anchored)
        self._build_input_bar()

        # 3. Main Vertical Split: Top Workspace vs. Bottom Full-Width Console
        outer_v = tk.PanedWindow(
            self.root, orient=tk.VERTICAL,
            bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT
        )
        outer_v.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # Top Horizontal Split: Left (File + Editor) vs. Right (Tokens + Symbol Table)
        top_h = tk.PanedWindow(
            outer_v, orient=tk.HORIZONTAL,
            bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT
        )
        outer_v.add(top_h, minsize=280, stretch="always")

        # ── Left Column: Compact File Explorer + Text Editor ──────────────
        left_col = tk.Frame(top_h, bg=BG_DARK)
        top_h.add(left_col, minsize=340, stretch="always")

        self._build_file_explorer(left_col)
        self._build_editor(left_col)

        # ── Top-Right Column: Lexemes/Tokens & Symbol Table Side-by-Side ───
        right_h = tk.PanedWindow(
            top_h, orient=tk.HORIZONTAL,
            bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT
        )
        top_h.add(right_h, minsize=460, stretch="always")

        token_frame = self._titled_frame(right_h, "Lexemes / Tokens")
        right_h.add(token_frame, minsize=230, stretch="always")
        self._build_token_table(token_frame)

        symbol_frame = self._titled_frame(right_h, "Symbol Table")
        right_h.add(symbol_frame, minsize=210, stretch="always")
        self._build_symbol_table(symbol_frame)

        # ── Bottom Pane: Execute Bar + Full-Width Console ─────────────────
        bottom_area = tk.Frame(outer_v, bg=BG_DARK)
        outer_v.add(bottom_area, minsize=180, stretch="always")

        self.run_btn = tk.Button(
            bottom_area,
            text="▶  EXECUTE",
            command=self._run,
            bg=FG_GREEN, fg=BG_DARK,
            font=FONT_HEAD,
            relief=tk.FLAT, pady=5,
            cursor="hand2",
            activebackground="#7dc97a", activeforeground=BG_DARK,
        )
        self.run_btn.pack(fill=tk.X, pady=(2, 4))

        console_frame = self._titled_frame(bottom_area, "Console")
        console_frame.pack(fill=tk.BOTH, expand=True)
        self._build_console(console_frame)

    # ── Toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=46)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))
        bar.pack_propagate(False)

        tk.Label(
            bar, text="LOLCode Interpreter",
            bg=BG_PANEL, fg=FG_ACCENT, font=FONT_TITLE
        ).pack(side=tk.LEFT, padx=12)

        clear_btn = tk.Button(
            bar, text="🧹  Clear",
            command=self._clear_all,
            bg=BG_HEADER, fg=FG_YELLOW,
            font=FONT_UI,
            relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_YELLOW,
        )
        clear_btn.pack(side=tk.RIGHT, padx=(4, 12), pady=8)

        save_btn = tk.Button(
            bar, text="💾  Save",
            command=self._save_file,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI,
            relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
        )
        save_btn.pack(side=tk.RIGHT, padx=4, pady=8)

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

    # ── Panel 1 — File Explorer Bar ───────────────────────────────────────

    def _build_file_explorer(self, parent):
        bar = tk.Frame(
            parent, bg=BG_PANEL,
            highlightbackground=BG_HEADER, highlightthickness=1
        )
        bar.pack(fill=tk.X, pady=(0, 4))

        self.explorer_label = tk.Label(
            bar,
            text="(None)",
            bg=BG_PANEL, fg=FG_DIM, font=FONT_UI,
            anchor="w", padx=10, pady=5,
        )
        self.explorer_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        folder_btn = tk.Button(
            bar, text="📂",
            command=self._open_file,
            bg=BG_HEADER, fg=FG_ACCENT,
            font=FONT_UI, relief=tk.FLAT,
            padx=10, pady=3, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
        )
        folder_btn.pack(side=tk.RIGHT)

    # ── Panel 2 — Text Editor ─────────────────────────────────────────────

    def _build_editor(self, parent):
        frame = self._titled_frame(parent, "Text Editor")
        frame.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(frame, bg=BG_EDITOR)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 2))

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

        hb = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.editor.xview)
        hb.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.editor.config(xscrollcommand=hb.set)

        self._update_line_numbers()

    def _sync_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_mousewheel(self, event):
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_line_numbers(self, event=None):
        content = self.editor.get("1.0", tk.END)
        n_lines = max(1, content.count("\n"))
        nums = "\n".join(str(i) for i in range(1, n_lines + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", nums)
        self.line_numbers.config(state=tk.DISABLED)

    # ── Panel 3 — Token List ──────────────────────────────────────────────

    def _build_token_table(self, parent):
        cols = ("line", "type", "value")
        self.token_tree = self._make_treeview(
            parent, cols,
            headings=("Line", "Classification", "Lexeme"),
            widths=(45, 130, 120),
        )

    # ── Panel 4 — Symbol Table ────────────────────────────────────────────

    def _build_symbol_table(self, parent):
        cols = ("name", "type", "value")
        self.symbol_tree = self._make_treeview(
            parent, cols,
            headings=("Identifier", "Type", "Value"),
            widths=(100, 80, 120),
        )

    # ── Panel 5 — Console ─────────────────────────────────────────────────

    def _build_console(self, parent):
        self.console = scrolledtext.ScrolledText(
            parent,
            bg="#0d0d1a", fg=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED,
            padx=8, pady=6,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.console.tag_config("error",  foreground=FG_RED)
        self.console.tag_config("ok",     foreground=FG_GREEN)
        self.console.tag_config("dim",    foreground=FG_DIM)
        self.console.tag_config("input",  foreground=FG_YELLOW)
        self.console.tag_config("prompt", foreground=FG_ACCENT)

    # ── Fixed Bottom Input Row (GIMMEH) ───────────────────────────────────

    def _build_input_bar(self):
        input_bar = tk.Frame(
            self.root, bg=BG_PANEL, height=40,
            highlightbackground=BG_HEADER, highlightthickness=1
        )
        input_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 8))
        input_bar.pack_propagate(False)

        self._input_indicator = tk.Label(
            input_bar, text="●",
            bg=BG_PANEL, fg=FG_DIM, font=FONT_UI,
        )
        self._input_indicator.pack(side=tk.LEFT, padx=(10, 4))

        tk.Label(
            input_bar, text="GIMMEH Input:",
            bg=BG_PANEL, fg=FG_DIM, font=FONT_HEAD
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.console_input = tk.Entry(
            input_bar,
            bg=BG_EDITOR, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            disabledbackground="#161624",
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED,
        )
        self.console_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        self.console_input.bind("<Return>", lambda e: self._send_input())

        self.send_btn = tk.Button(
            input_bar, text="Send",
            command=self._send_input,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_HEAD, relief=tk.FLAT,
            padx=14, cursor="hand2",
            activebackground="#4a4a6a", activeforeground=FG_TEXT,
            state=tk.DISABLED,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(4, 8), pady=6)

    # ── GIMMEH input handling ─────────────────────────────────────────────

    def _enable_input(self):
        self._waiting_for_input = True
        self._input_indicator.config(fg=FG_GREEN)
        self.console_input.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.console_input.focus_set()

    def _disable_input(self):
        self._waiting_for_input = False
        self._input_indicator.config(fg=FG_DIM)
        self.console_input.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

    def _send_input(self):
        if not self._waiting_for_input:
            return
        value = self.console_input.get()
        self.console_input.delete(0, tk.END)
        self._disable_input()
        self._log(f"» {value}\n", tag="input")
        self._input_value = value
        self._input_event.set()

    # ── Interpreter callbacks (called from worker thread) ─────────────────

    def _interp_output(self, text, end="\n"):
        full = text + end
        self.root.after(0, lambda t=full: self._log(t))

    def _interp_input(self, prompt: str) -> str:
        self._input_event.clear()
        self.root.after(0, lambda p=prompt: (
            self._log(f"{p}", tag="prompt"),
            self._enable_input(),
        ))
        self._input_event.wait()
        return self._input_value

    def _interp_update(self, variables: dict):
        self.root.after(0, lambda d=dict(variables): self._refresh_symbol_table(d))

    # ── Symbol table refresh ──────────────────────────────────────────────

    def _refresh_symbol_table(self, variables: dict):
        self._clear_tree(self.symbol_tree)
        for name, lv in variables.items():
            if lv.type == "NUMBAR":
                display_val = f"{lv.value:.2f}" if isinstance(lv.value, float) else str(lv.value)
            elif lv.type == "TROOF":
                display_val = "WIN" if lv.value else "FAIL"
            elif lv.type == "NOOB":
                display_val = "NOOB"
            else:
                display_val = str(lv.value)
            self.symbol_tree.insert("", tk.END, values=(name, lv.type, display_val))

    # ── Clear workspace (keeps editor intact) ─────────────────────────────

    def _clear_all(self):
        self._clear_tree(self.token_tree)
        self._clear_tree(self.symbol_tree)
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

    # ── Run pipeline ──────────────────────────────────────────────────────

    def _run(self):
        source = self.editor.get("1.0", tk.END)
        if not source.strip():
            self._log("Nothing to run — editor is empty.\n", tag="error")
            return

        self._clear_tree(self.token_tree)
        self._clear_tree(self.symbol_tree)
        self._log("─" * 48 + "\n", tag="dim")

        # 1. Lex
        lexer  = Lexer(source)
        tokens = lexer.tokenize()

        visible = [t for t in tokens if t.token_type not in (TT_NEWLINE, TT_EOF)]
        for tok in visible:
            self.token_tree.insert("", tk.END, values=(tok.line_num, tok.token_type, tok.value))

        if lexer.errors:
            for err in lexer.errors:
                self._log(f"[LEXER ERROR] {err}\n", tag="error")
            return

        # 2. Parse
        parser = Parser(tokens)
        tree   = parser.parse()

        if parser.errors:
            for err in parser.errors:
                self._log(f"[SYNTAX ERROR] {err}\n", tag="error")
            return

        # 3. Interpret (in background thread)
        self.run_btn.config(state=tk.DISABLED)

        interp = Interpreter(
            output_fn=self._interp_output,
            input_fn=self._interp_input,
            update_fn=self._interp_update,
        )

        def worker():
            interp.run(tree)
            self.root.after(0, lambda: self._run_finished(interp))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _run_finished(self, interp: Interpreter):
        if interp.errors:
            for err in interp.errors:
                self._log(f"[RUNTIME ERROR] {err}\n", tag="error")
        self.run_btn.config(state=tk.NORMAL)
        self._disable_input()

    # ── Helpers ───────────────────────────────────────────────────────────

    def _titled_frame(self, parent, title: str) -> tk.LabelFrame:
        return tk.LabelFrame(
            parent, text=f"  {title}  ",
            bg=BG_PANEL, fg=FG_ACCENT,
            font=FONT_HEAD,
            relief=tk.FLAT, bd=1,
        )

    def _make_treeview(self, parent, cols, headings, widths) -> ttk.Treeview:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Treeview",
            background=BG_TABLE, foreground=FG_TEXT,
            fieldbackground=BG_TABLE, rowheight=24,
            font=FONT_CODE,
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=BG_HEADER, foreground=FG_ACCENT,
            font=FONT_HEAD, relief=tk.FLAT,
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", BG_HEADER)],
            foreground=[("selected", FG_TEXT)],
        )

        container = tk.Frame(parent, bg=BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        vsb = tk.Scrollbar(container, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(
            container, columns=cols, show="headings",
            style="Dark.Treeview", yscrollcommand=vsb.set,
        )
        vsb.config(command=tree.yview)

        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor=tk.W, minwidth=40)

        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def _open_file(self):
        start_dir = os.path.dirname(self.current_file) if self.current_file else os.getcwd()
        dialog = FileBrowserDialog(self.root, initial_dir=start_dir)
        self.root.wait_window(dialog)
        if dialog.selected_file:
            self._load_file(dialog.selected_file)

    def _load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return

        self.current_file = path
        filename = os.path.basename(path)
        self.explorer_label.config(text=f"📄  {filename}", fg=FG_TEXT)
        self.root.title(f"LOLCode Interpreter — {filename}")

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", source)
        self._update_line_numbers()
        self._log(f"Loaded: {path}\n", tag="dim")

    def _save_file(self):
        path = self.current_file
        if not path:
            path = filedialog.asksaveasfilename(
                title="Save LOLCode file",
                defaultextension=".lol",
                filetypes=[("LOLCode files", "*.lol"), ("All files", "*.*")],
            )
            if not path:
                return

        try:
            content = self.editor.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            return

        self.current_file = path
        filename = os.path.basename(path)
        self.explorer_label.config(text=f"📄  {filename}", fg=FG_TEXT)
        self.root.title(f"LOLCode Interpreter — {filename}")
        self._log(f"Saved: {path}\n", tag="dim")

    def _log(self, text: str, tag: str = ""):
        self.console.config(state=tk.NORMAL)
        if tag:
            self.console.insert(tk.END, text, tag)
        else:
            self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def _clear_tree(self, tree: ttk.Treeview):
        for item in tree.get_children():
            tree.delete(item)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app  = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()