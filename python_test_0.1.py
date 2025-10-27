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
    - Show a short info dialog with progressively snarkier messages.
    - Increase difficulty: each level keeps previous behaviors and adds new ones.
    """
    global click_count, difficulty, mouse_evade_enabled

    click_count += 1

    # Update main label with an admonishing message and the current count
    if label is not None:
        messages = [
            "Tsk tsk... clicking buttons?",
            "Still clicking? How persistent.",
            "You just can't help yourself, can you?",
            "Now you're just being stubborn!",
            "Fine! Have it your way... for now."
        ]
        label.config(text=f"{messages[min(difficulty, len(messages)-1)]} Clicks: {click_count}")

    # Show a dialog with escalating snark
    messagebox.showinfo("Really?", f"Click #{click_count}... I see how it is.")

    # Advance difficulty and enable mouse-evade at level 3
    if click_count >= 5:  # Max difficulty
        difficulty = 4
    else:
        difficulty = click_count - 1
    mouse_evade_enabled = difficulty >= 3

    # Apply effects - they now stack with difficulty
    apply_post_click_effect()


def apply_post_click_effect() -> None:
    """Apply effects after each click, stacking them as difficulty increases.

    Progressive effects (they stack):
    0 - small random nudge
    1 - adds periodic size changes
    2 - adds stronger repositioning
    3 - enables mouse evasion + adds quick jiggle
    4 - everything gets more aggressive

    Effects stack and intensify but remain possible to click with persistence.
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

    # Level 0+: Small random nudge
    nx = random.randint(10, max(10, win_w - b_w - 10))
    ny = random.randint(40, max(40, win_h - b_h - 10))
    btn.place(x=nx, y=ny)

    # Level 1+: Add size changes
    if difficulty >= 1:
        if random.random() < 0.5:
            # Randomly shrink or grow, but stay clickable
            new_w = btn.cget("width")
            if random.random() < 0.5:
                new_w = max(6, new_w - 2)  # Shrink
            else:
                new_w = min(20, new_w + 2)  # Grow
            btn.config(width=new_w)

    # Level 2+: Add stronger repositioning
    if difficulty >= 2:
        # Occasionally make bigger jumps
        if random.random() < 0.3:
            nx = random.randint(10, max(10, win_w - b_w - 10))
            ny = random.randint(40, max(40, win_h - b_h - 10))
            btn.place(x=nx, y=ny)

    # Level 3+: Add jiggle animation
    if difficulty >= 3:
        # Quick jiggle with intensity based on difficulty
        intensity = 5 if difficulty < 4 else 8
        moves = [(-intensity, 0), (intensity, 0), (0, -intensity), (0, intensity)]
        for dx, dy in moves:
            try:
                cur_x = btn.winfo_x()
                cur_y = btn.winfo_y()
                nx = clamp(cur_x + dx, 0, max(0, win_w - b_w))
                ny = clamp(cur_y + dy, 40, max(40, win_h - b_h))
                btn.place(x=nx, y=ny)
                root.update()
            except tk.TclError:
                break

    # Level 4: Everything gets more intense
    if difficulty >= 4:
        # More frequent size changes
        if random.random() < 0.4:
            new_w = max(6, min(25, btn.cget("width") + random.randint(-3, 3)))
            btn.config(width=new_w)


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
