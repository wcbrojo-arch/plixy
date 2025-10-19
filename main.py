# plixy_app.py
import tkinter as tk
from tkinter import ttk
import re, random

# ---------- Plixy Interpreter ----------
class PlixyInterpreter:
    def __init__(self, output_fn):
        self.vars = {}
        self.output = output_fn
        self.windows = []              # (win, canvas, frame)
        self.current_font = ("Arial", 16)
        self.ai_enabled = False
        self.last_textbox = None
        self.last_button = None

    def run(self, code: str):
        lines = [l.rstrip() for l in code.splitlines() if l.strip()]
        for line in lines:
            try:
                # print
                if line.startswith("print "):
                    expr = line[6:]
                    msg = str(self.safe_eval(expr))
                    if self.ai_enabled:
                        msg = self.ai_response(msg)
                    self.output(msg)
                    continue

                # let assignment (supports dot paths)
                if line.startswith("let "):
                    m = re.match(r"let\s+([\w\.]+)\s*=\s*(.+)", line)
                    if m:
                        path, expr = m.groups()
                        value = expr.strip()
                        if value.lower() == "blank" and path == "window.run.window.play":
                            self.create_blank_window()
                            self.set_var(path, "<BlankWindow>")
                        else:
                            self.set_var(path, self.safe_eval(expr))
                        continue

                # draw text
                if line.startswith("local print"):
                    m = re.match(r'local\s+print\s*=\s*"(.*)"\s*=\s*print', line)
                    if m:
                        self.draw_text(m.group(1))
                        continue

                # set font
                if line.startswith("local font"):
                    m = re.match(r'local\s+font\s*=\s*"(.*)"\s*local\.print', line)
                    if m:
                        self.set_font(m.group(1))
                        continue

                # button
                if line.startswith("local button"):
                    m = re.match(r'local\s+button\s*=\s*create\s*=\s*"(.*)"\s*print', line)
                    if m:
                        self.create_button(m.group(1))
                        continue

                # textbox
                if line.startswith("local text"):
                    m = re.match(r'local\s+text\s*=\s*"(.*)"\s*here\s*=\s*textbox', line)
                    if m:
                        self.create_textbox(m.group(1))
                        continue

                # scroll area
                if line.startswith("local scroll") and "weel = print" in line:
                    self.create_scroll_area()
                    continue

                # enable toy AI
                if line.startswith("local think") and "create.ai.print" in line:
                    self.ai_enabled = True
                    self.output("Basic AI enabled. `print` will reply playfully.")
                    continue

                # colors
                if line.startswith("local color"):
                    m = re.match(r'local\s+color\s*=\s*"(.*)"\s*\.run', line)
                    if m:
                        self.apply_color(m.group(1))
                        continue

                # window title
                if line.startswith("local title"):
                    m = re.match(r'local\s+title\s*=\s*"(.*)"\s*of\s*window\.run', line)
                    if m:
                        self.set_window_title(m.group(1))
                        continue

                self.output(f"Unknown command: {line}")
            except Exception as e:
                self.output(f"[Plixy ERROR] {type(e).__name__}: {e}\nLine: {line}")

    # ---------- helpers ----------
    def set_var(self, path, value):
        parts = path.split(".")
        d = self.vars
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value

    def get_var(self, path):
        parts = path.split(".")
        d = self.vars
        for p in parts:
            if isinstance(d, dict) and p in d:
                d = d[p]
            else:
                return None
        return d

    def safe_eval(self, expr: str):
        # Replace variable names (incl. dot paths) with their values if defined
        def repl(m):
            name = m.group(0)
            val = self.get_var(name)
            return str(val) if val is not None else name
        replaced = re.sub(r"[A-Za-z_][\w\.]*", repl, expr)
        # Try Python eval for math/expressions, else return a cleaned string literal
        try:
            return eval(replaced, {}, {})
        except Exception:
            s = replaced.strip()
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                return s[1:-1]
            return s

    def create_blank_window(self):
        # Create a new top-level window and canvas
        win = tk.Toplevel()
        win.title("Plixy Window")
        win.geometry("500x360")
        frame = tk.Frame(win, bg="white")
        frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(frame, bg="white")
        canvas.pack(fill="both", expand=True)
        self.windows.append((win, canvas, frame))
        self.output("Window created.")

    def draw_text(self, text, x=250, y=180):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        _, canvas, _ = self.windows[-1]
        canvas.create_text(x, y, text=text, font=self.current_font, fill="black")

    def set_font(self, fontname):
        self.current_font = (fontname, 16)
        self.output(f"Font set to {fontname}")

    def create_button(self, text):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        _, _, frame = self.windows[-1]
        btn = tk.Button(frame, text=text, command=lambda: self.output(f"Button '{text}' clicked"))
        btn.pack(pady=10)
        self.last_button = btn
        self.output("Button created.")

    def create_textbox(self, placeholder):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        _, _, frame = self.windows[-1]
        entry = tk.Entry(frame, font=self.current_font)
        entry.insert(0, placeholder)
        entry.pack(pady=10)
        entry.bind("<Return>", lambda e: self.output(f"Textbox input: {entry.get()}"))
        self.last_textbox = entry
        self.output("Textbox created.")

    def create_scroll_area(self):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        _, _, frame = self.windows[-1]
        text_widget = tk.Text(frame, wrap="word", height=10, width=50)
        scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        text_widget.insert("1.0", "Scroll area ready.\n" + "\n".join([f"Line {i}" for i in range(1, 80)]))
        self.output("Scroll area created.")

    def apply_color(self, spec):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        win, canvas, frame = self.windows[-1]
        spec = spec.lower()
        if "background" in spec:
            frame.config(bg="lightblue"); canvas.config(bg="lightblue")
            self.output("Background color changed.")
        elif "textbox" in spec and self.last_textbox:
            self.last_textbox.config(bg="lightyellow")
            self.output("Textbox color changed.")
        elif "button" in spec and self.last_button:
            self.last_button.config(bg="lightgreen")
            self.output("Button color changed.")
        else:
            self.output("No matching element for color change.")

    def set_window_title(self, title):
        if not self.windows:
            self.output("No window. Use: let window.run.window.play = blank")
            return
        win, _, _ = self.windows[-1]
        win.title(title)
        self.output(f"Window title set to '{title}'")

    def ai_response(self, msg):
        responses = [
            f"You said: {msg}",
            f"I’m thinking about '{msg}'...",
            f"Interesting—tell me more about {msg}.",
            f"Why do you say '{msg}'?",
            f"'{msg}' makes me curious."
        ]
        return random.choice(responses)

# ---------- App with tabs, working Run, Beginner + Expert ----------
def main():
    root = tk.Tk()
    root.title("Plixy Interpreter")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Scripts tab
    scripts_frame = ttk.Frame(notebook)
    notebook.add(scripts_frame, text="Scripts")

    code_box = tk.Text(
        scripts_frame, height=20, width=80,
        bg="#1e1e1e", fg="#dcdcdc", insertbackground="white"
    )
    code_box.pack(padx=10, pady=10, fill="both", expand=True)

    # Output tab
    output_frame = ttk.Frame(notebook)
    notebook.add(output_frame, text="Output")

    output_box = tk.Text(
        output_frame, height=15, width=80,
        bg="#252526", fg="#9cdcfe", state="disabled"
    )
    output_box.pack(padx=10, pady=10, fill="both", expand=True)

    # Beginner Script tab
    beginner_frame = ttk.Frame(notebook)
    notebook.add(beginner_frame, text="Beginner Script")

    beginner_box = tk.Text(
        beginner_frame, height=20, width=80,
        bg="#f7f7f7", fg="#222"
    )
    beginner_box.pack(padx=10, pady=10, fill="both", expand=True)
    beginner_code = """# Beginner Plixy Script
let window.run.window.play = blank
local title = "Beginner Window" of window.run
local print = "Hello, world!" = print
local button = create = "Click Me!" print
"""
    beginner_box.insert("1.0", beginner_code)
    beginner_box.config(state="disabled")  # read-only

    # Output function
    def write_output(msg):
        output_box.config(state="normal")
        output_box.insert(tk.END, msg + "\n")
        output_box.config(state="disabled")
        output_box.see(tk.END)

    # Run logic
    def run_code():
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.config(state="disabled")
        interp = PlixyInterpreter(write_output)
        interp.run(code_box.get("1.0", tk.END))
        notebook.select(output_frame)

    # Buttons under notebook
    run_button = tk.Button(root, text="Run Plixy Code", command=run_code, bg="#007acc", fg="white")
    run_button.pack(pady=6)

    def load_expert_script():
        expert_code = """# Expert Plixy Script
let window.run.window.play = blank
local title = "Expert Window" of window.run
local font = "Courier" local.print
local print = "Welcome to Expert Mode!" = print
local button = create = "Click Me!" print
local text = "Type here..." here = textbox
local scroll = weel = print
local color = "background" .run
local color = "textbox" .run
local color = "button" .run
local think = create.ai.print
print "Testing AI response"
"""
        code_box.delete("1.0", tk.END)
        code_box.insert("1.0", expert_code)
        notebook.select(scripts_frame)

    expert_button = tk.Button(root, text="Load Expert Script", command=load_expert_script, bg="#444", fg="white")
    expert_button.pack(pady=3)

    # Starter demo in Scripts tab (known-good)
    code_box.insert("1.0", """let window.run.window.play = blank
local title = "My First Plixy Window" of window.run
local font = "Courier" local.print
local print = "Hello Plixy!" = print
local button = create = "Click Me!" print
local text = "Type here..." here = textbox
local scroll = weel = print
local color = "background" .run
local color = "textbox" .run
local color = "button" .run
local think = create.ai.print
print "What do you think?"
""")

    root.mainloop()

if __name__ == "__main__":
    main()
