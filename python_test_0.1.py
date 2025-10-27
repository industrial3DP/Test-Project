#!/usr/bin/env python3
"""Tkinter Hello World tutorial example

This file is a compact, well-commented example intended for learning how
to build a tiny GUI with the Python standard library's Tkinter module.

Contract (tiny):
- Input: user clicks button in the GUI.
- Output: label text is updated and an informational dialog appears.
- Error modes: If Tkinter is not available (rare on standard Windows CPython),
  importing tkinter will raise ImportError and the script will fail early.

Run: python python_test_0.1.py

Learning goals:
- Understand the basic Tk event loop and widget callbacks.
- See how to create a label and a button and react to clicks.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
import random
import math


# Module state (kept simple for the tutorial). In a real app prefer a class.
label: Optional[tk.Label] = None
btn: Optional[tk.Button] = None
click_count: int = 0
# difficulty cycles through behaviors and increases the "evasion".
difficulty: int = 0
# when True the button will try to evade the mouse motion
mouse_evade_enabled: bool = False


def on_click() -> None:
    """Handle an actual click on the button.

    - Increment the click counter and update the label with an admonishment.
    - Show a short info dialog (keeps the joke tone).
    - Trigger the next difficulty behaviour so the button becomes harder to
      click next time.
    """
    global click_count, difficulty, mouse_evade_enabled

    click_count += 1

    # Update main label with an admonishing message and the current count.
    if label is not None:
        label.config(text=f"Bad Human! Clicks: {click_count}")

    # A short info dialog for fun.
    messagebox.showinfo("Info", f"You clicked {click_count} time(s).")

    # Advance difficulty and enable mouse-evade on higher levels.
    difficulty = (difficulty + 1) % 5
    mouse_evade_enabled = difficulty >= 3

    # Apply the immediate post-click effect so the button moves/changes now.
    apply_post_click_effect()


def apply_post_click_effect() -> None:
    """Apply an effect after each click to make the button harder to catch.

    Effects cycle by `difficulty`:
    0 - small random move
    1 - shrink (narrower)
    2 - grow (bigger)
    3 - enable mouse-evade and do a quick jiggle
    4 - stronger random reposition

    The effects are intentionally mild so the button remains clickable.
    """
    if btn is None:
        return

    # Ensure geometry info is up-to-date
    root = btn.master
    root.update_idletasks()

    win_w = root.winfo_width()
    win_h = root.winfo_height()
    b_w = btn.winfo_width()
    b_h = btn.winfo_height()

    def clamp(x, a, b):
        return max(a, min(b, x))

    if difficulty == 0:
        # small random nudges
        nx = random.randint(10, max(10, win_w - b_w - 10))
        ny = random.randint(40, max(40, win_h - b_h - 10))
        btn.place(x=nx, y=ny)

    elif difficulty == 1:
        # shrink but keep clickable: width is in text units, minimum 6
        new_w = max(6, btn.cget("width") - 3)
        btn.config(width=new_w)

    elif difficulty == 2:
        # grow a bit, to make it awkward
        new_w = min(30, btn.cget("width") + 4)
        btn.config(width=new_w)

    elif difficulty == 3:
        # quick jiggle: perform a few tiny moves
        for dx, dy in ((-10, 0), (10, 0), (0, -6), (0, 6)):
            try:
                cur_x = btn.winfo_x()
                cur_y = btn.winfo_y()
                nx = clamp(cur_x + dx, 0, max(0, win_w - b_w))
                ny = clamp(cur_y + dy, 40, max(40, win_h - b_h))
                btn.place(x=nx, y=ny)
                root.update()
            except tk.TclError:
                # GUI might close during animation; ignore safely
                break

    elif difficulty == 4:
        # stronger reposition but still inside window
        nx = random.randint(10, max(10, win_w - b_w - 10))
        ny = random.randint(40, max(40, win_h - b_h - 10))
        btn.place(x=nx, y=ny)


def on_mouse_move(event: tk.Event) -> None:
    """When the mouse moves, optionally nudge the button away if it's close.

    This is the "evade" behavior: when enabled the button will try to move
    away from the cursor if the cursor gets within a threshold distance.
    It makes clicking harder but not impossible.
    """
    if not mouse_evade_enabled or btn is None:
        return

    # Button geometry
    bx = btn.winfo_x()
    by = btn.winfo_y()
    bw = btn.winfo_width()
    bh = btn.winfo_height()

    # Cursor
    cx, cy = event.x, event.y

    # Compute button center
    bc_x = bx + bw / 2
    bc_y = by + bh / 2

    # Distance from cursor to button center
    dist = math.hypot(bc_x - cx, bc_y - cy)

    # If too close, move the button away proportionally to distance
    threshold = 100
    if dist < threshold and dist > 1:
        # Vector from cursor to button center
        vx = bc_x - cx
        vy = bc_y - cy
        # Normalize and scale by a small step
        step = int(max(20, (threshold - dist) / 2))
        nx = int(bx + (vx / dist) * step)
        ny = int(by + (vy / dist) * step)

        # Keep inside window (leave top area for the label)
        root = btn.master
        win_w = root.winfo_width()
        win_h = root.winfo_height()
        nx = max(0, min(nx, win_w - bw))
        ny = max(40, min(ny, win_h - bh))
        btn.place(x=nx, y=ny)


def build_ui(root: tk.Tk) -> None:
    """Create the widgets and lay them out inside the provided root window.

    This version places the button using `place()` so we can move it freely.
    """
    global label, btn

    # A simple label with a readable font size.
    label = tk.Label(root, text="Don't Click the Button!", font=("Segoe UI", 14))
    label.pack(pady=(12, 8))

    # The button is wired to call `on_click` when pressed. We place it at a
    # starting coordinate; subsequent effects will reposition it.
    btn = tk.Button(root, text="No Click Zone", width=12, command=on_click)
    # initial placement (x,y) inside window; y>40 leaves space for the label
    btn.place(x=100, y=50)

    # Bind mouse motion to enable evasive behaviour when activated.
    root.bind('<Motion>', on_mouse_move)



def main() -> None:
    """Application entry point: create the root window, build UI, and run.

    Important: Tkinter runs an event loop with `mainloop()`; the program
    remains responsive while the loop is running and returns only after the
    user closes the window.
    """
    # Create the main application window
    root = tk.Tk()
    root.title("Human Testing App")
    # Set a reasonable default size. The layout will still expand if needed.
    root.geometry("320x120")

    # Build the user interface
    build_ui(root)

    # Start the Tk event loop. This call is blocking until the window closes.
    root.mainloop()


if __name__ == "__main__":
    # Protect the entry point so importing this module doesn't start the UI.
    main()
