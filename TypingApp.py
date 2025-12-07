import tkinter as tk
import random
import time
import os

# ==========================
# CONFIG
# ==========================

ALLOWED_CHARS = "jkl;"
WORD_COUNT = 200
MIN_WORD_LEN = 3
MAX_WORD_LEN = 7

KEY_SOUND = ""
ERROR_SOUND = ""

# Toggle this to show/hide the end screen
END_SCREEN_ENABLED = False

BACKGROUND = "#050505"
TEXT_COLOR_DEFAULT = "#333333"
TEXT_COLOR_CORRECT = "#9DFF91"
TEXT_COLOR_ERROR   = "#FF6B6B"
CURSOR_COLOR       = "#1E1E1E"

FONT_FAMILY = "FiraCode Nerd Font"
FONT_SIZE = 20


# ==========================
# HELPERS
# ==========================

def generate_text(chars, word_count, min_len, max_len):
    words = []
    for _ in range(word_count):
        length = random.randint(min_len, max_len)
        words.append("".join(random.choice(chars) for _ in range(length)))
    return " ".join(words)


def play_sound(path):
    if not path or not os.path.exists(path):
        return
    # try:
    #     # winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    # except:
        pass


# ==========================
# MAIN APP
# ==========================

class TypingApp:
    def __init__(self, root):
        self.root = root

        self.root.title("typing")
        self.root.configure(bg=BACKGROUND)
        self.root.geometry("1200x600")
        self.is_fullscreen = False

        self.target_text = generate_text(ALLOWED_CHARS, WORD_COUNT, MIN_WORD_LEN, MAX_WORD_LEN)
        self.index = 0
        self.started = False
        self.finished = False

        # Stats
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0        # all typed chars (no backspaces)
        self.correct_keystrokes = 0      # chars that were correct at the moment of typing

        self.build_ui()

        self.root.bind("<Key>", self.on_key)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

    def build_ui(self):
        top_bar = tk.Frame(self.root, bg=BACKGROUND)
        top_bar.pack(side="top", fill="x")

        self.fullscreen_button = tk.Button(
            top_bar,
            text="⛶",
            command=self.toggle_fullscreen,
            fg="#777",
            bg=BACKGROUND,
            activeforeground="#fff",
            activebackground=BACKGROUND,
            font=(FONT_FAMILY, 16),
            bd=0,
            highlightthickness=0,
            padx=10
        )
        self.fullscreen_button.pack(side="right", padx=16, pady=10)

        # TEXT WIDGET
        self.text_widget = tk.Text(
            self.root,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=BACKGROUND,
            fg=TEXT_COLOR_DEFAULT,
            wrap="word",
            bd=0,
            highlightthickness=0,
            padx=80,
            pady=40,
            spacing3=8,
            height=6
        )

        self.text_widget.insert("1.0", self.target_text)

        # ---- TAGS (important part) ----
        self.text_widget.tag_config(
            "correct",
            foreground=TEXT_COLOR_CORRECT,
            # optional: subtle background for correct chars
            # background="#102810"
        )
        self.text_widget.tag_config(
            "error",
            foreground=TEXT_COLOR_ERROR,
            background="#401010"  # <-- this makes wrong spaces VISIBLE
        )
        self.text_widget.tag_config("cursor", background=CURSOR_COLOR)
        # -------------------------------

        if len(self.target_text) > 0:
            self.text_widget.tag_add("cursor", "1.0", "1.0+1c")

        self.text_widget.config(state="disabled")
        self.text_widget.pack(expand=True, fill="both")

    # --- Fullscreen handling ---
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)

    # --- Cursor movement ---
    def move_cursor(self):
        self.text_widget.config(state="normal")
        self.text_widget.tag_remove("cursor", "1.0", "end")
        if 0 <= self.index < len(self.target_text):
            pos = f"1.0+{self.index}c"
            self.text_widget.tag_add("cursor", pos, f"{pos}+1c")
        self.text_widget.config(state="disabled")

    # --- Backspace ---
    def handle_backspace(self):
        if self.finished or self.index == 0:
            return
        self.index -= 1
        self.text_widget.config(state="normal")
        pos = f"1.0+{self.index}c"
        self.text_widget.tag_remove("correct", pos, f"{pos}+1c")
        self.text_widget.tag_remove("error", pos, f"{pos}+1c")
        self.text_widget.config(state="disabled")
        self.move_cursor()

    # --- Key input ---
    def on_key(self, event):
        if self.finished:
            return

        # Backspace: doesn't count in accuracy stats
        if event.keysym == "BackSpace":
            self.handle_backspace()
            return

        # Normalize char (especially for space)
        if event.keysym == "space":
            ch = " "
        else:
            ch = event.char

        # Ignore non-character keys
        if not ch or len(ch) != 1:
            return

        # Start timer on very first typed character
        if not self.started:
            self.started = True
            self.start_time = time.time()

        if self.index >= len(self.target_text):
            self.finish()
            return

        expected = self.target_text[self.index]

        # Count raw keystrokes (no backspaces)
        self.total_keystrokes += 1

        # SAME BEHAVIOR FOR ALL CHARS (including spaces):
        if ch == expected:
            tag = "correct"
            self.correct_keystrokes += 1
            play_sound(KEY_SOUND)
        else:
            tag = "error"
            play_sound(ERROR_SOUND)

        self.text_widget.config(state="normal")
        pos = f"1.0+{self.index}c"
        self.text_widget.tag_add(tag, pos, f"{pos}+1c")
        self.text_widget.config(state="disabled")

        # Always advance; you can fix with Backspace
        self.index += 1
        if self.index >= len(self.target_text):
            self.finish()
        else:
            self.move_cursor()

    def finish(self):
        if self.finished:
            return

        self.finished = True
        self.end_time = time.time()

        self.text_widget.config(state="normal")
        self.text_widget.tag_remove("cursor", "1.0", "end")
        self.text_widget.config(state="disabled")

        # ==========================
        # STATS CALCULATION
        # ==========================
        total_chars = len(self.target_text)

        # Final accuracy (with backspace correction)
        ranges = self.text_widget.tag_ranges("correct")
        correct_final = 0
        for i in range(0, len(ranges), 2):
            correct_final += int(self.text_widget.count(ranges[i], ranges[i+1], "chars")[0])

        if total_chars > 0:
            accuracy_corrected = (correct_final / total_chars) * 100.0
        else:
            accuracy_corrected = 0.0

        # Raw accuracy (WITHOUT backspace correction)
        if self.total_keystrokes > 0:
            accuracy_raw = (self.correct_keystrokes / self.total_keystrokes) * 100.0
        else:
            accuracy_raw = 0.0

        # Time and WPS
        if self.start_time is not None and self.end_time is not None:
            duration = max(self.end_time - self.start_time, 0.0)
        else:
            duration = 0.0

        word_count = len(self.target_text.split())
        if duration > 0:
            wps = (word_count / duration)*60
        else:
            wps = 0.0

        if END_SCREEN_ENABLED:
            self.show_end_screen(
                accuracy_corrected=accuracy_corrected,
                accuracy_raw=accuracy_raw,
                duration=duration,
                wps=wps
            )

    # --- End screen ---
    def show_end_screen(self, accuracy_corrected, accuracy_raw, duration, wps):
        end_win = tk.Toplevel(self.root)
        end_win.title("Results")
        end_win.configure(bg=BACKGROUND)

        end_win.geometry("700x320")

        container = tk.Frame(end_win, bg=BACKGROUND, padx=30, pady=30)
        container.pack(expand=True, fill="both")

        title_label = tk.Label(
            container,
            text="Session Finished",
            font=(FONT_FAMILY, FONT_SIZE + 4, "bold"),
            fg=TEXT_COLOR_CORRECT,
            bg=BACKGROUND
        )
        title_label.pack(anchor="w", pady=(0, 15))

        def fmt_pct(x):
            return f"{x:.1f}%"

        def fmt_time(t):
            return f"{t:.2f} s"

        def fmt_wps(v):
            return f"{v:.2f} wps"

        stats = [
            f"Accuracy (with correction):    {fmt_pct(accuracy_corrected)}",
            f"Accuracy (without correction): {fmt_pct(accuracy_raw)}",
            f"Time:                          {fmt_time(duration)}",
            f"WPM:                          {fmt_wps(wps)}",
        ]

        for line in stats:
            lbl = tk.Label(
                container,
                text=line,
                font=(FONT_FAMILY, FONT_SIZE - 2),
                fg="#bbbbbb",
                bg=BACKGROUND,
                anchor="w",
                justify="left"
            )
            lbl.pack(anchor="w")

        close_btn = tk.Button(
            container,
            text="Close",
            command=end_win.destroy,
            fg="#ffffff",
            bg="#222222",
            activeforeground="#ffffff",
            activebackground="#333333",
            font=(FONT_FAMILY, FONT_SIZE - 2),
            bd=0,
            padx=10,
            pady=5
        )
        close_btn.pack(anchor="e", pady=(20, 0))


if __name__ == "__main__":
    root = tk.Tk()
    TypingApp(root)
    root.mainloop()
