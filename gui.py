"""
LOLCODE Interpreter GUI
CMSC 124 - S-3L | Group EJDB

Main GUI application using tkinter.
Wires together the lexer (ML1), parser (ML2), and interpreter (ML3).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import io
import threading
from syntax_analyzer import Parser, print_tree

from lexer import Lexer, TT_NEWLINE, TT_EOF
from syntax_analyzer import Parser, print_tree
from interpreter import Interpreter


# ── colour palette ────────────────────────────────────────────────────────────
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


def tree_to_string(node):
    """Capture print_tree output as a string."""
    buf = io.StringIO()
    import sys
    old = sys.stdout
    sys.stdout = buf
    print_tree(node)
    sys.stdout = old
    return buf.getvalue()


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("LOLCode Interpreter — CMSC 124 Group EJDB")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)

        self.current_file: str | None = None

        # ── GIMMEH input synchronisation ──────────────────────────────────
        # The interpreter runs in a worker thread.  When it needs input it
        # sets _waiting_for_input = True, blocks on _input_event, and reads
        # _input_value once the main thread releases the event.
        self._waiting_for_input: bool = False
        self._input_event: threading.Event = threading.Event()
        self._input_value: str = ""

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        self._build_toolbar()

        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                              bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left = tk.Frame(main, bg=BG_DARK)
        main.add(left, minsize=350)

        self._build_file_explorer(left)
        self._build_editor(left)

        right = tk.PanedWindow(main, orient=tk.VERTICAL,
                               bg=BG_DARK, sashwidth=5, sashrelief=tk.FLAT)
        main.add(right, minsize=400)

        token_frame = self._titled_frame(right, "③ List of Tokens")
        right.add(token_frame, minsize=80)
        self._build_token_table(token_frame)

        symbol_frame = self._titled_frame(right, "④ Symbol Table")
        right.add(symbol_frame, minsize=80)
        self._build_symbol_table(symbol_frame)

        console_frame = self._titled_frame(right, "⑤ Console")
        right.add(console_frame, minsize=120)
        self._build_console(console_frame)

    # ── toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=48)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))
        bar.pack_propagate(False)

        tk.Label(bar, text="LOLCode Interpreter",
                 bg=BG_PANEL, fg=FG_ACCENT, font=FONT_TITLE).pack(side=tk.LEFT, padx=12)

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

        self.file_label = tk.Label(bar, text="No file selected",
                                   bg=BG_PANEL, fg=FG_DIM, font=FONT_UI)
        self.file_label.pack(side=tk.RIGHT, padx=12)

    # ── panel 1 — file explorer ───────────────────────────────────────────

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

    # ── panel 2 — text editor ─────────────────────────────────────────────

    def _build_editor(self, parent):
        frame = self._titled_frame(parent, "② Text Editor")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

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

        hb = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.editor.xview)
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

    # ── panel 3 — token list ──────────────────────────────────────────────

    def _build_token_table(self, parent):
        cols = ("line", "type", "value")
        self.token_tree = self._make_treeview(parent, cols,
                                              headings=("Line", "Type", "Value"),
                                              widths=(50, 130, 200))

    # ── panel 4 — symbol table ────────────────────────────────────────────

    def _build_symbol_table(self, parent):
        cols = ("name", "type", "value")
        self.symbol_tree = self._make_treeview(parent, cols,
                                               headings=("Variable", "Type", "Value"),
                                               widths=(120, 100, 160))

    # ── panel 5 — console ─────────────────────────────────────────────────

    def _build_console(self, parent):
        self.console = scrolledtext.ScrolledText(
            parent,
            bg="#0d0d1a", fg=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED,
            padx=8, pady=4,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 2))
        self.console.tag_config("error",  foreground=FG_RED)
        self.console.tag_config("ok",     foreground=FG_GREEN)
        self.console.tag_config("dim",    foreground=FG_DIM)
        self.console.tag_config("input",  foreground=FG_YELLOW)
        self.console.tag_config("prompt", foreground=FG_ACCENT)

        # input row (GIMMEH)
        input_row = tk.Frame(parent, bg=BG_PANEL)
        input_row.pack(fill=tk.X, padx=6, pady=(0, 6))

        self._input_indicator = tk.Label(
            input_row, text="●",
            bg=BG_PANEL, fg=FG_DIM, font=FONT_UI,
        )
        self._input_indicator.pack(side=tk.LEFT, padx=(0, 2))

        tk.Label(input_row, text="Input:", bg=BG_PANEL,
                 fg=FG_DIM, font=FONT_UI).pack(side=tk.LEFT)

        self.console_input = tk.Entry(
            input_row,
            bg=BG_EDITOR, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            font=FONT_CODE, relief=tk.FLAT,
            state=tk.DISABLED,           # only enabled while GIMMEH is waiting
        )
        self.console_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self.console_input.bind("<Return>", lambda e: self._send_input())

        self.send_btn = tk.Button(
            input_row, text="Send",
            command=self._send_input,
            bg=BG_HEADER, fg=FG_TEXT,
            font=FONT_UI, relief=tk.FLAT,
            padx=8, cursor="hand2",
            activebackground="#4a4a6a",
            state=tk.DISABLED,           # only enabled while GIMMEH is waiting
        )
        self.send_btn.pack(side=tk.LEFT)

    # ── GIMMEH input handling ─────────────────────────────────────────────

    def _enable_input(self):
        """Called (via root.after) when the interpreter is waiting for input."""
        self._waiting_for_input = True
        self._input_indicator.config(fg=FG_GREEN)
        self.console_input.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.console_input.focus_set()

    def _disable_input(self):
        """Lock the input row again after input was consumed."""
        self._waiting_for_input = False
        self._input_indicator.config(fg=FG_DIM)
        self.console_input.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

    def _send_input(self):
        """User clicked Send (or pressed Enter) — unblock the interpreter."""
        if not self._waiting_for_input:
            return
        value = self.console_input.get()
        self.console_input.delete(0, tk.END)
        self._disable_input()
        self._log(f"» {value}\n", tag="input")
        self._input_value = value
        self._input_event.set()   # wake the blocked interpreter thread

    # ── interpreter callbacks (called from worker thread) ─────────────────

    def _interp_output(self, text, end="\n"):
        """VISIBLE output — schedule on the main thread."""
        full = text + end
        self.root.after(0, lambda t=full: self._log(t))

    def _interp_input(self, prompt: str) -> str:
        """
        GIMMEH input — block the worker thread until the user sends text.
        Must NOT be called from the main thread.
        """
        self._input_event.clear()
        # enable input row on main thread
        self.root.after(0, lambda p=prompt: (
            self._log(f"{p}", tag="prompt"),
            self._enable_input(),
        ))
        self._input_event.wait()   # block until _send_input() sets the event
        return self._input_value

    def _interp_update(self, variables: dict):
        """Symbol table refresh — schedule on the main thread."""
        self.root.after(0, lambda d=dict(variables): self._refresh_symbol_table(d))

    # ── symbol table refresh ──────────────────────────────────────────────

    def _refresh_symbol_table(self, variables: dict):
        self._clear_tree(self.symbol_tree)
        for name, lv in variables.items():
            # format the Python value for display
            if lv.type == 'NUMBAR':
                display_val = f"{lv.value:.2f}" if isinstance(lv.value, float) else str(lv.value)
            elif lv.type == 'TROOF':
                display_val = "WIN" if lv.value else "FAIL"
            elif lv.type == 'NOOB':
                display_val = "NOOB"
            else:
                display_val = str(lv.value)
            self.symbol_tree.insert("", tk.END, values=(name, lv.type, display_val))

    # ── run pipeline ──────────────────────────────────────────────────────

    def _run(self):
        source = self.editor.get("1.0", tk.END)
        if not source.strip():
            self._log("Nothing to run — editor is empty.\n", tag="error")
            return

        # clear previous results
        self._clear_tree(self.token_tree)
        self._clear_tree(self.symbol_tree)
        self._log("─" * 48 + "\n", tag="dim")
        self._log("Running...\n", tag="dim")

        # ── 1. lex ────────────────────────────────────────────────────────
        lexer  = Lexer(source)
        tokens = lexer.tokenize()

        visible = [t for t in tokens if t.token_type not in (TT_NEWLINE, TT_EOF)]
        for tok in visible:
            self.token_tree.insert("", tk.END, values=(tok.line_num, tok.token_type, tok.value))

        if lexer.errors:
            for err in lexer.errors:
                self._log(f"[LEXER ERROR] {err}\n", tag="error")
            self._log(f"{len(visible)} token(s) found with {len(lexer.errors)} error(s).\n", tag="error")
            return

        self._log(f"Tokenization complete — {len(visible)} tokens found.\n", tag="ok")

        # ── 2. parse ──────────────────────────────────────────────────────
        parser = Parser(tokens)
        tree   = parser.parse()

        if parser.errors:
            for err in parser.errors:
                self._log(f"[SYNTAX ERROR] {err}\n", tag="error")
            return

        self._log("Syntax analysis complete — no syntax errors.\n", tag="ok")
        self._log("\nParse Tree:\n", tag="dim")
        self._log(tree_to_string(tree) + "\n", tag="dim")

        # ── 3. interpret (in background thread) ──────────────────────────
        self.run_btn.config(state=tk.DISABLED)
        self._log("─" * 48 + "\n", tag="dim")
        self._log("Executing...\n", tag="dim")

        interp = Interpreter(
            output_fn=self._interp_output,
            input_fn=self._interp_input,
            update_fn=self._interp_update,
        )

        def worker():
            interp.run(tree)
            # back on main thread: report errors + re-enable run button
            self.root.after(0, lambda: self._run_finished(interp))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _run_finished(self, interp: Interpreter):
        """Called on the main thread after the interpreter thread exits."""
        if interp.errors:
            for err in interp.errors:
                self._log(f"[RUNTIME ERROR] {err}\n", tag="error")
        else:
            self._log("Execution complete.\n", tag="ok")
        self.run_btn.config(state=tk.NORMAL)
        self._disable_input()

    # ── helpers ───────────────────────────────────────────────────────────

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
                            style="Dark.Treeview", yscrollcommand=vsb.set)
        vsb.config(command=tree.yview)

        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor=tk.W, minwidth=40)

        tree.pack(fill=tk.BOTH, expand=True)
        return tree

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


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app  = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()