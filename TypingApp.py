import tkinter as tk
import random
import time
import os


# ==========================
# MODE SELECTOR
# ==========================
# 1 = random words (nonsense)
# 2 = dictionary words based on allowed letters
# 3 = raw book text (ignores allowed letters)
MODE = 2


# ==========================
# CONFIG
# ==========================

ALLOWED_CHARS = "asdfjkl;gh"

# Random generator settings (Mode 1 only)
RANDOM_MIN_LEN = 2
RANDOM_MAX_LEN = 4

WORD_COUNT = 50

BACKGROUND = "#000000"
TEXT_COLOR_DEFAULT = "#BEBABA"
TEXT_COLOR_CORRECT = "#238616"
TEXT_COLOR_ERROR   = "#EA5B5B"
CURSOR_COLOR       = "#1E1E1E"

FONT_FAMILY = "FiraCode Nerd Font"
FONT_SIZE = 20

END_SCREEN_ENABLED = True

KEY_SOUND = ""
ERROR_SOUND = ""


# ==========================
# RANDOM WORD MODE (Mode 1)
# ==========================

def generate_random_words(chars, count, min_len, max_len):
    words = []
    for _ in range(count):
        length = random.randint(min_len, max_len)
        words.append("".join(random.choice(chars) for _ in range(length)))
    return " ".join(words)


# ==========================
# DICTIONARY MODE (Mode 2)
# ==========================

def load_dictionary(path="words/words.txt"):
    """Load a dictionary file into a list of words."""
    if not os.path.exists(path):
        print("ERROR: Dictionary file not found:", path)
        return []

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            words = [w.strip().lower() for w in f if w.strip()]
        return words
    except Exception as e:
        print("ERROR reading dictionary:", e)
        return []


def filter_dictionary_by_allowed_letters(words, allowed):
    """Return only words made entirely of letters in ALLOWED_CHARS."""
    allowed_set = set(allowed)
    filtered = []

    for w in words:
        if all((c in allowed_set) for c in w):
            filtered.append(w)

    return filtered


def generate_dictionary_words():
    """Generate words from dictionary using allowed letters. Mode 2."""
    dictionary = load_dictionary("words/words.txt")

    valid_words = filter_dictionary_by_allowed_letters(dictionary, ALLOWED_CHARS)

    if not valid_words:
        print("ERROR: No dictionary words can be formed using:", ALLOWED_CHARS)
        print("Falling back to MODE 1 (random letters).")
        return generate_random_words(ALLOWED_CHARS, WORD_COUNT, RANDOM_MIN_LEN, RANDOM_MAX_LEN)

    return " ".join(random.choice(valid_words) for _ in range(WORD_COUNT))


# ==========================
# BOOK MODE (Mode 3)
# ==========================

def load_random_book_text():
    folder = "books"
    if not os.path.exists(folder):
        return "NO BOOKS FOUND — create a folder named 'books' and add .txt files."

    files = [f for f in os.listdir(folder) if f.lower().endswith(".txt")]
    if not files:
        return "NO .TXT FILES IN books/ — download books."

    path = os.path.join(folder, random.choice(files))

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except:
        return "FAILED TO READ BOOK FILE."

    words = text.split()
    if len(words) < 200:
        chunk = words
    else:
        start = random.randint(0, len(words) - 200)
        chunk = words[start:start + 200]

    return " ".join(chunk)


# ==========================
# MAIN MODE LOGIC
# ==========================

def get_text_for_mode():
    if MODE == 1:
        return generate_random_words(ALLOWED_CHARS, WORD_COUNT, RANDOM_MIN_LEN, RANDOM_MAX_LEN)

    elif MODE == 2:
        return generate_dictionary_words()

    elif MODE == 3:
        return load_random_book_text()

    else:
        return "INVALID MODE"


# ==========================
# SOUND (unused)
# ==========================

def play_sound(path):
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

        self.target_text = get_text_for_mode()
        self.index = 0
        self.started = False
        self.finished = False

        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.correct_keystrokes = 0

        self.end_win = None

        self.build_ui()

        self.root.bind("<Key>", self.on_key)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<Control-r>", self.reset_session)
        self.root.bind("<Control-R>", self.reset_session)

    def build_ui(self):
        top_bar = tk.Frame(self.root, bg=BACKGROUND)
        top_bar.pack(side="top", fill="x")

        reset_button = tk.Button(
            top_bar, text="⟳", command=self.reset_session,
            fg="#777", bg=BACKGROUND,
            activeforeground="#fff", activebackground=BACKGROUND,
            font=(FONT_FAMILY, 16),
            bd=0, highlightthickness=0, padx=10
        )
        reset_button.pack(side="right", padx=(0, 4), pady=10)

        fullscreen_button = tk.Button(
            top_bar, text="⛶", command=self.toggle_fullscreen,
            fg="#777", bg=BACKGROUND,
            activeforeground="#fff", activebackground=BACKGROUND,
            font=(FONT_FAMILY, 16),
            bd=0, highlightthickness=0, padx=10
        )
        fullscreen_button.pack(side="right", padx=12, pady=10)

        # typing area
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

        self.text_widget.tag_config("correct", foreground=TEXT_COLOR_CORRECT)
        self.text_widget.tag_config("error", foreground=TEXT_COLOR_ERROR, background="#401010")
        self.text_widget.tag_config("cursor", background=CURSOR_COLOR)

        if self.target_text:
            self.text_widget.tag_add("cursor", "1.0", "1.0+1c")

        self.text_widget.config(state="disabled")
        self.text_widget.pack(expand=True, fill="both")

    # RESET
    def reset_session(self, event=None):
        if self.end_win and self.end_win.winfo_exists():
            self.end_win.destroy()

        self.end_win = None
        self.target_text = get_text_for_mode()
        self.index = 0
        self.started = False
        self.finished = False

        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.correct_keystrokes = 0

        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", self.target_text)

        self.text_widget.tag_remove("correct", "1.0", "end")
        self.text_widget.tag_remove("error", "1.0", "end")
        self.text_widget.tag_remove("cursor", "1.0", "end")

        if self.target_text:
            self.text_widget.tag_add("cursor", "1.0", "1.0+1c")

        self.text_widget.config(state="disabled")
        return "break"

    # FULLSCREEN
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.root.attributes("-fullscreen", False)
            self.is_fullscreen = False

    # CURSOR
    def move_cursor(self):
        self.text_widget.config(state="normal")
        self.text_widget.tag_remove("cursor", "1.0", "end")
        pos = f"1.0+{self.index}c"
        self.text_widget.tag_add("cursor", pos, f"{pos}+1c")
        self.text_widget.config(state="disabled")

    # BACKSPACE
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

    # KEY INPUT
    def on_key(self, event):
        if self.finished:
            return

        if event.keysym == "BackSpace":
            self.handle_backspace()
            return

        ch = " " if event.keysym == "space" else event.char
        if not ch or len(ch) != 1:
            return

        if not self.started:
            self.started = True
            self.start_time = time.time()

        if self.index >= len(self.target_text):
            self.finish()
            return

        expected = self.target_text[self.index]
        self.total_keystrokes += 1

        tag = "correct" if ch == expected else "error"
        if tag == "correct":
            self.correct_keystrokes += 1

        self.text_widget.config(state="normal")
        pos = f"1.0+{self.index}c"
        self.text_widget.tag_add(tag, pos, f"{pos}+1c")
        self.text_widget.config(state="disabled")

        self.index += 1
        if self.index >= len(self.target_text):
            self.finish()
        else:
            self.move_cursor()

    # FINISH
    def finish(self):
        if self.finished:
            return

        self.finished = True
        self.end_time = time.time()

        self.text_widget.config(state="normal")
        self.text_widget.tag_remove("cursor", "1.0", "end")
        self.text_widget.config(state="disabled")

        total_chars = len(self.target_text)

        correct_final = 0
        ranges = self.text_widget.tag_ranges("correct")
        for i in range(0, len(ranges), 2):
            correct_final += int(self.text_widget.count(ranges[i], ranges[i+1], "chars")[0])

        accuracy_corrected = (correct_final / total_chars * 100) if total_chars else 0
        accuracy_raw = (self.correct_keystrokes / self.total_keystrokes * 100) if self.total_keystrokes else 0

        duration = self.end_time - self.start_time
        words = len(self.target_text.split())

        wpm = (words / duration * 60) if duration > 0 else 0
        lpm = (total_chars / duration * 60) if duration > 0 else 0

        if END_SCREEN_ENABLED:
            self.show_end_screen(accuracy_corrected, accuracy_raw, duration, wpm, lpm)
        else:
            self.reset_session()

    # END SCREEN
    def show_end_screen(self, accuracy_corrected, accuracy_raw, duration, wpm, lpm):
        win = tk.Toplevel(self.root)
        self.end_win = win

        win.title("Results")
        win.configure(bg=BACKGROUND)
        win.geometry("700x350")
        win.grab_set()
        win.focus_force()

        frame = tk.Frame(win, bg=BACKGROUND, padx=30, pady=30)
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame, text="Session Finished",
            font=(FONT_FAMILY, FONT_SIZE + 4, "bold"),
            fg=TEXT_COLOR_CORRECT, bg=BACKGROUND
        ).pack(anchor="w", pady=(0, 15))

        data = [
            f"Accuracy (corrected): {accuracy_corrected:.1f}%",
            f"Accuracy (raw):       {accuracy_raw:.1f}%",
            f"Time:                 {duration:.2f} s",
            f"WPM:                  {wpm:.2f}",
            f"LPM:                  {lpm:.2f}",
        ]

        for line in data:
            tk.Label(
                frame, text=line,
                font=(FONT_FAMILY, FONT_SIZE - 2),
                fg="#bbbbbb", bg=BACKGROUND,
                anchor="w"
            ).pack(anchor="w")

        def close():
            self.reset_session()

        win.bind("<Return>", lambda e: close())

        tk.Button(
            frame, text="Next (Enter)",
            command=close, fg="#fff", bg="#222",
            activeforeground="#fff", activebackground="#333",
            font=(FONT_FAMILY, FONT_SIZE - 2),
            bd=0, padx=10, pady=5
        ).pack(anchor="e", pady=(20, 0))



# MAIN
if __name__ == "__main__":
    root = tk.Tk()
    TypingApp(root)
    root.mainloop()
