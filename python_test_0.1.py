#!/usr/bin/env python3
# Copyright (c) 2025 industrial3DP
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Interactive Mouse Precision Game with Tkinter and Local AI

This application demonstrates advanced GUI programming concepts using Python's
Tkinter library, combined with local AI integration through Ollama. It started
as a simple Hello World but evolved into an engaging mouse precision game.

Key Features:
1. Interactive GUI with dynamic button behavior
2. Local AI integration for personalized responses
3. Progressive difficulty system
4. Debug capabilities and logging
5. Secret admin menu with advanced controls

Technical Components:
- Tkinter: Core GUI framework from Python standard library
- Ollama: Local AI model integration for dynamic responses
- Threading: Background tasks for AI communication
- Event handling: Mouse tracking and button movement

Learning Goals:
1. Basic Tkinter concepts:
   - Event loop and widget callbacks
   - Dynamic widget manipulation
   - Custom event binding
2. Advanced GUI techniques:
   - Widget animation and movement
   - Mouse position tracking
   - Dynamic difficulty scaling
3. AI Integration:
   - Local model communication
   - Asynchronous processing
   - Error handling and fallbacks
4. Development best practices:
   - Comprehensive logging
   - Debug capabilities
   - User feedback systems

Usage: python python_test_0.1.py

Note: The app requires Tkinter (included with standard Python) and optionally
Ollama for AI features. See README.md for full setup instructions."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
import random
import math
import threading
import os
import subprocess
import shutil
from typing import Callable
from typing import Optional as _Opt
import time
import ollama


#
# MODULE STATE AND CONFIGURATION
# ----------------------------
# These variables control the application's behavior and state.
# In a larger application, this would be organized into classes,
# but for teaching purposes we keep it simple with module-level state.
#

# UI Elements - initialized in build_ui()
label: Optional[tk.Label] = None          # Main text label at top
counter_label: Optional[tk.Label] = None  # Click counter display
btn: Optional[tk.Button] = None           # The button users try to click
llm_toggle_btn: Optional[tk.Button] = None # Optional LLM control button
llm_indicator: Optional[tk.Label] = None   # Shows LLM status (top-right)
root_win: Optional[tk.Tk] = None          # Main application window

# Game State
click_count: int = 0           # Number of times button was clicked
difficulty: int = 0           # Current game level (0-4)
mouse_evade_enabled: bool = False  # True when button should dodge cursor
llm_enabled: bool = True      # Whether to use AI for responses

# Theme Configuration
# ------------------
# Color scheme and dynamic theming for the application

def _apply_dynamic_theme(root_window: tk.Tk) -> None:
    """Apply dynamic color theme based on current difficulty."""
    colors = get_dynamic_colors(difficulty)
    root_window.configure(**colors['window'])
    if label is not None:
        label.configure(**colors['window'])
    if counter_label is not None:
        counter_label.configure(**colors['window'])
    if btn is not None:
        btn.configure(**colors['button'])

THEME = {
    'dark': {
        'window': {
            # Root window uses special property names
            'bg': '#1e1e1e',  # Dark background
        },
        'button': {
            'background': '#2d2d2d',
            'foreground': '#ffffff',
            'activebackground': '#3d3d3d',
            'activeforeground': '#ffffff'
        },
        'label': {
            'background': '#1e1e1e',
            'foreground': '#ffffff'
        },
        'messagebox': {
            'bg': '#1e1e1e',
            'fg': '#ffffff'
        }
    }
}

# Dynamic color intensities that increase with difficulty
INTENSITY_COLORS = [
    '#1e1e1e',  # Base dark
    '#1e1e2e',  # Slightly more intense
    '#1e1e3e',  # Medium intensity
    '#1e1e4e',  # High intensity
    '#1e1e5e'   # Maximum intensity
]

# Dialog color schemes for each difficulty level
DIALOG_THEMES = [
    {  # Level 0 - Professional
        'bg': '#2d2d2d',
        'fg': '#ffffff',
        'font': ('Segoe UI', 10, 'normal'),
        'title': 'Really?'
    },
    {  # Level 1 - Mild Annoyance
        'bg': '#2d2d35',
        'fg': "#55E0B7",  # Orange
        'font': ('Segoe UI', 10, 'bold'),
        'title': 'Oh Really?'
    },
    {  # Level 2 - Clear Frustration
        'bg': '#2d2d3d',
        'fg': "#00AAC09B",  # Coral
        'font': ('Segoe UI', 11, 'bold'),
        'title': 'REALLY??'
    },
    {  # Level 3 - Heavy Sarcasm
        'bg': '#2d2d45',
        'fg': "#6d49a7",  # Bright Red
        'font': ('Segoe UI', 12, 'bold'),
        'title': 'SERIOUSLY?!'
    },
    {  # Level 4 - Maximum Frustration
        'bg': '#2d2d4d',
        'fg': "#A1448A",  # Pure Red
        'font': ('Segoe UI', 13, 'bold'),
        'title': 'OH COME ON!!'
    }
]

def get_dynamic_colors(difficulty: int) -> dict:
    """Get color scheme based on current difficulty level."""
    base_color = INTENSITY_COLORS[min(difficulty, len(INTENSITY_COLORS)-1)]
    glow_intensity = min(difficulty * 20 + 40, 255)  # Increases with difficulty
    
    return {
        'window': {
            'bg': base_color,  # Root window uses 'bg' not 'background'
        },
        'button': {
            'background': f'#2d2d{min(difficulty * 15 + 45, 99):02d}',
            'foreground': f'#{glow_intensity:02x}{glow_intensity:02x}{glow_intensity:02x}',
            'activebackground': f'#3d3d{min(difficulty * 15 + 45, 99):02d}',
            'activeforeground': '#ffffff'
        }
    }

# Title variations by difficulty level
WINDOW_TITLES = [
    # Level 0 - Basic
    [
        "Human Testing App",
        "Click Testing Initiative",
        "Button Interaction Study",
        "Human Behavior Analysis",
        "Persistence Evaluation"
    ],
    # Level 1 - Mildly Annoyed
    [
        "Please Stop Clicking",
        "Unnecessary Click Counter",
        "Button Abuse Monitor",
        "Click Addiction Study",
        "Persistent Clicker Assessment"
    ],
    # Level 2 - Getting Irritated
    [
        "Seriously, Stop Clicking",
        "Chronic Click Syndrome",
        "Button Harassment Log",
        "Compulsive Clicking Monitor",
        "Why Are You Still Here?"
    ],
    # Level 3 - Very Annoyed
    [
        "This Is Getting Ridiculous",
        "Professional Click Pest",
        "Button Torment Tracker",
        "Obsessive Click Disorder",
        "Don't You Have Better Things To Do?"
    ],
    # Level 4 - Maximum Frustration
    [
        "PLEASE STOP CLICKING",
        "Pathological Button Pusher",
        "Maximum Click Tolerance Exceeded",
        "You're Still Here?!",
        "Click Crisis Level: MAXIMUM"
    ]
]

def get_window_title() -> str:
    """Generate a window title based on current difficulty and click count."""
    # Get the list of titles for current difficulty
    titles = WINDOW_TITLES[min(difficulty, len(WINDOW_TITLES)-1)]
    # Use click count to cycle through titles
    return titles[click_count % len(titles)]

#
# CONFIGURATION AND CONSTANTS
# -------------------------
# Application settings and configuration values
#

# AI/LLM Configuration
# -------------------
# Ollama is used for generating dynamic responses. These settings control
# the model selection and timeout behavior.
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "tinyllama:latest")
OLLAMA_TIMEOUT_SEC = 30  # Allows time for model startup/download

# Fallback Messages
# ----------------
# Used when AI is disabled or unavailable. These provide a consistent
# experience even without the AI component.
FALLBACK_SNARK = [
    "Oh, clicking buttons are we? How... predictable.",
    "Your persistence is amusing, but futile.",
    "Do you really have nothing better to do?",
    "Ah, humans and their compulsive button-clicking.",
    "This is becoming rather pathetic, isn't it?",
]

# Debug System Configuration
# ------------------------
# Comprehensive logging system for development and troubleshooting
debug_enabled: bool = True                 # Master debug switch
debug_window: _Opt[tk.Toplevel] = None    # Debug UI window
debug_text_widget: _Opt[tk.Text] = None   # Debug text display
debug_log_lines: list[str] = []           # Log history

# System Monitoring
# ---------------
# Controls for background service monitoring
_heartbeat_running = False                # Heartbeat thread status
_HEARTBEAT_INTERVAL = 8                   # Check interval (seconds)


def on_click() -> None:
    """Handle button clicks and manage game progression.
    
    This is the main game logic handler that:
    1. Updates the click counter
    2. Changes the display message based on difficulty
    3. Triggers AI response generation if enabled
    4. Increases game difficulty and adds new behaviors
    5. Applies visual and movement effects to the button
    
    The difficulty system is progressive, with each level adding new
    behaviors while keeping previous ones:
    - Level 0: Basic movement
    - Level 1: Size changes
    - Level 2: Enhanced movement
    - Level 3: Mouse evasion + animations
    - Level 4: Maximum difficulty with all effects
    """
    global click_count, difficulty, mouse_evade_enabled

    click_count += 1

    # Update main label with an admonishing message and the current count
    if label is not None:
        messages = [
            # Level 0 - Mild surprise/amusement
            [
                "Tsk tsk... clicking buttons?",
                "Oh look, someone found the button.",
                "Really? The button caught your eye?",
                "I see you've discovered clicking.",
                "Another enthusiastic button pusher..."
            ],
            # Level 1 - Growing annoyance
            [
                "Still clicking? How persistent.",
                "Don't you have better hobbies?",
                "This button pushing is getting old.",
                "Yes, it's still a button.",
                "Your dedication is... questionable."
            ],
            # Level 2 - Clear frustration
            [
                "You just can't help yourself, can you?",
                "Are we having fun yet?",
                "This is becoming rather tedious.",
                "Some people never learn...",
                "Must. Keep. Clicking. Right?"
            ],
            # Level 3 - Heavy sarcasm
            [
                "Now you're just being stubborn!",
                "Congratulations on your persistence.",
                "Achievement Unlocked: Master Irritator",
                "I'm not impressed, just disappointed.",
                "Your dedication to annoyance is remarkable."
            ],
            # Level 4 - Maximum sass
            [
                "Fine! Have it your way... for now.",
                "You've reached peak button pusher status.",
                "I hope you're proud of yourself.",
                "This is your life now, isn't it?",
                "Well done. You've broken all records of stubbornness."
            ]
        ]
        # Get messages for current difficulty and cycle through them based on click count
        level_messages = messages[min(difficulty, len(messages)-1)]
        message_index = click_count % len(level_messages)
        label.config(text=level_messages[message_index])
        
    # Update click counter
    if counter_label is not None:
        counter_label.config(text=f"Clicks: {click_count}")

    # Prepare a context-aware prompt for the LLM with escalating frustration
    personalities = [
        "mildly annoyed but professional",  # Level 0
        "visibly irritated",                # Level 1
        "thoroughly exasperated",           # Level 2
        "at your wit's end",               # Level 3
        "completely done with humanity"     # Level 4
    ]
    
    intensity_words = [
        "persists in",           # Level 0
        "stubbornly continues",  # Level 1
        "refuses to stop",       # Level 2
        "obsessively keeps",     # Level 3
        "maniacally insists on"  # Level 4
    ]
    
    # Base prompt
    prompt = (
        f"You are a snarky AI assistant who is {personalities[difficulty]}. "
        f"A particularly stubborn user {intensity_words[difficulty]} clicking your button "
        f"({click_count} times now). Express your growing frustration in one short, "
        f"sharp sentence (under 60 chars). Be rude or inappropriate as needed."
    )
    
    # Add model-specific adjustments
    if OLLAMA_MODEL.lower().startswith("tinyllama"):
        prompt += " And please, no mentions of tea whatsoever."

    # If LLM is enabled try to fetch a snarky reply asynchronously; otherwise
    # show a fallback message immediately.
    if llm_enabled:
        # run the generation in a background thread to avoid freezing the UI
        threading.Thread(target=_fetch_and_show_snark, args=(prompt,), daemon=True).start()
    else:
        messagebox.showinfo("Really?", f"Click #{click_count}... I see how it is.")

    # Advance difficulty and enable mouse-evade at level 3
    if click_count >= 5:  # Max difficulty
        difficulty = 4
    else:
        difficulty = click_count - 1
    mouse_evade_enabled = difficulty >= 3

    # Update window title
    if root_win is not None:
        root_win.title(get_window_title())
        # Apply dynamic theme updates
        _apply_dynamic_theme(root_win)

    # Apply effects - they now stack with difficulty
    apply_post_click_effect()


def apply_post_click_effect() -> None:
    """Applies progressive visual and movement effects to the button based on difficulty level.
    
    This function implements the core gameplay mechanics that make the button
    increasingly challenging to click. Effects are cumulative and scale with
    difficulty, but are carefully tuned to remain possible with persistence.
    
    Difficulty Levels and Effects:
    
    Level 0 - Basic Movement
    - Small random position changes
    - Limited movement range
    - Predictable patterns
    
    Level 1 - Size Manipulation
    - Random button size changes
    - Maintains minimum clickable size
    - 50% chance of size change per click
    
    Level 2 - Enhanced Movement
    - Larger position changes
    - Occasional corner jumps
    - More frequent repositioning
    - Tighter edge margins
    
    Level 3 - Advanced Evasion
    - Mouse cursor tracking
    - Button actively evades cursor
    - Quick jiggle animations
    - Diagonal movements
    
    Level 4 - Maximum Challenge
    - All previous effects intensified
    - More aggressive size changes
    - Random visual styling
    - Increased movement frequency
    - Variable button appearance
    
    Technical Implementation:
    - Uses geometry manager place() for precise positioning
    - Monitors window boundaries to keep button accessible
    - Implements smooth animations with update_idletasks()
    - Manages multiple simultaneous effects
    
    Note: All effects are designed to be frustrating but fair - the button
    should always be technically possible to click with enough persistence.
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
        # More frequent and varied jumps
        if random.random() < 0.4:  # Increased frequency
            # Sometimes make extreme jumps to corners
            if random.random() < 0.3:
                corners = [
                    (5, 40),  # Top-left
                    (win_w - b_w - 5, 40),  # Top-right
                    (5, win_h - b_h - 5),  # Bottom-left
                    (win_w - b_w - 5, win_h - b_h - 5)  # Bottom-right
                ]
                nx, ny = random.choice(corners)
            else:
                # Normal random position but with tighter edge margins
                nx = random.randint(5, max(5, win_w - b_w - 5))
                ny = random.randint(40, max(40, win_h - b_h - 5))
            btn.place(x=nx, y=ny)

    # Level 3+: Add jiggle animation
    if difficulty >= 3:
        # Quick jiggle with intensity based on difficulty
        intensity = 5 if difficulty < 4 else 12  # More intense at max difficulty
        # Add diagonal movements for more unpredictable motion
        moves = [
            (-intensity, 0), (intensity, 0),  # Horizontal
            (0, -intensity), (0, intensity),  # Vertical
            (-intensity, -intensity), (intensity, intensity),  # Diagonal
            (intensity, -intensity), (-intensity, intensity)   # Diagonal
        ]
        # Randomize the move sequence
        random.shuffle(moves)
        for dx, dy in moves:
            try:
                cur_x = btn.winfo_x()
                cur_y = btn.winfo_y()
                # Add slight randomness to each movement
                rdx = dx + random.randint(-2, 2)
                rdy = dy + random.randint(-2, 2)
                nx = clamp(cur_x + rdx, 0, max(0, win_w - b_w))
                ny = clamp(cur_y + rdy, 40, max(40, win_h - b_h))
                btn.place(x=nx, y=ny)
                root.update()
            except tk.TclError:
                break

    # Level 4: Everything gets more intense
    if difficulty >= 4:
        # More aggressive size changes
        if random.random() < 0.6:  # Increased frequency
            new_w = max(4, min(30, btn.cget("width") + random.randint(-4, 4)))  # Wider range
            new_h = random.randint(1, 3)  # Height variation
            btn.config(width=new_w, height=new_h)
            
            # Randomly change button appearance
            styles = [
                {"relief": "raised", "borderwidth": 2},
                {"relief": "sunken", "borderwidth": 3},
                {"relief": "ridge", "borderwidth": 4},
                {"relief": "groove", "borderwidth": 3},
                {"relief": "flat", "borderwidth": 1}
            ]
            style = random.choice(styles)
            btn.config(**style)
            
            # Random color changes
            colors = ["SystemButtonFace", "lightgray", "gray85", "gray75", "white"]
            btn.config(bg=random.choice(colors))


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


def _generate_with_ollama(prompt: str) -> str:
    """Generate a short reply using the Ollama Python client.

    Returns the generated string or error message on failure.
    """
    try:
        _log_debug("Initializing Ollama client...")
        client = ollama.Client(host="http://localhost:11434")
        
        try:
            # First check if the model is available
            _log_debug(f"Checking if model {OLLAMA_MODEL} is available...")
            models = client.list()
            _log_debug(f"Got models response: {models}")  # Debug the actual response
            
            # Extract model names from response
            model_names = []
            try:
                for m in models.models:  # models.models is a list of Model objects
                    model_names.append(m.model)  # .model attribute contains the name
            except Exception as e:
                _log_debug(f"Model parsing error: {e}, raw models: {models}")
                return f"Error: Could not parse model list"
            
            _log_debug(f"Available models: {model_names}")
            model_available = OLLAMA_MODEL in model_names
            
            if not model_available:
                msg = f"Model {OLLAMA_MODEL} not found. Available models: {model_names}"
                _log_debug(f"ERROR: {msg}")
                return f"Error: {msg}"

            # Generate the response
            _log_debug(f"Generating response with model {OLLAMA_MODEL}...")
            response = client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                stream=False
            )
            return response['response'].strip()

        except ollama.RequestError as e:
            msg = f"Ollama request failed: {str(e)}"
            _log_debug(f"ERROR: {msg}")
            return f"Error: {msg}"
            
    except Exception as e:
        msg = f"Ollama client error: {str(e)}"
        _log_debug(f"ERROR: {msg}")
        return f"Error: {msg}"
def _fetch_and_show_snark(prompt: str) -> None:
    """Background worker: ask Ollama for a snarky reply, then show it on the UI thread."""
    if not llm_enabled:
        text = random.choice(FALLBACK_SNARK)
        _log_debug("LLM disabled, using fallback message")
    else:
        _log_debug("Attempting to generate response with Ollama...")
        text = _generate_with_ollama(prompt)
        if text.startswith("Error:"):
            _log_debug(f"Ollama error: {text}")
            text = f"Falling back to: {random.choice(FALLBACK_SNARK)}"
        elif not text:
            _log_debug("No response from Ollama, using fallback")
            text = random.choice(FALLBACK_SNARK)

    def _show():
        try:
            # Log to debug before showing message box
            _log_debug(f"Message box text: {text}")
            
            # Create a custom dialog with dynamic styling
            dialog = tk.Toplevel(root_win)
            theme = DIALOG_THEMES[min(difficulty, len(DIALOG_THEMES)-1)]
            
            # Configure dialog appearance
            dialog.configure(bg=theme['bg'])
            dialog.title(theme['title'])
            dialog.transient(root_win)  # Make dialog modal
            dialog.grab_set()
            
            # Center the dialog on screen
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            
            # Add message with dynamic styling
            msg = tk.Label(dialog, 
                         text=text,
                         wraplength=250,  # Enable text wrapping
                         justify='center',
                         bg=theme['bg'],
                         fg=theme['fg'],
                         font=theme['font'],
                         pady=20)
            msg.pack(expand=True, fill='both')
            
            # Add OK button with matching style
            btn_frame = tk.Frame(dialog, bg=theme['bg'])
            btn_frame.pack(pady=(0, 10))
            
            ok_btn = tk.Button(btn_frame, 
                             text="OK",
                             command=dialog.destroy,
                             bg=theme['bg'],
                             fg=theme['fg'],
                             activebackground=theme['bg'],
                             activeforeground=theme['fg'],
                             font=('Segoe UI', 9, 'bold'),
                             width=10)
            ok_btn.pack(pady=5)
            
            # Position dialog relative to parent
            if root_win:
                x = root_win.winfo_x() + (root_win.winfo_width() - dialog.winfo_reqwidth()) // 2
                y = root_win.winfo_y() + (root_win.winfo_height() - dialog.winfo_reqheight()) // 2
                dialog.geometry(f"+{x}+{y}")
            
            # Animate entry if at higher difficulty
            if difficulty >= 2:
                dialog.attributes('-alpha', 0.0)
                for i in range(11):
                    dialog.attributes('-alpha', i * 0.1)
                    dialog.update()
                    time.sleep(0.02)
            
            # Add shake effect at max difficulty
            if difficulty >= 4:
                orig_x = dialog.winfo_x()
                orig_y = dialog.winfo_y()
                for _ in range(3):  # Shake 3 times
                    for dx, dy in [(5,5), (-10,-5), (5,0), (0,-5), (5,5)]:
                        dialog.geometry(f"+{orig_x + dx}+{orig_y + dy}")
                        dialog.update()
                        time.sleep(0.05)
                dialog.geometry(f"+{orig_x}+{orig_y}")
            
            # Focus the OK button
            ok_btn.focus_set()
            
            # Handle Enter key
            dialog.bind('<Return>', lambda e: dialog.destroy())
            
        except tk.TclError:
            # UI closed
            pass

    # Schedule on main thread if we have the root, otherwise call directly
    try:
        if root_win is not None:
            root_win.after(0, _show)
        else:
            _show()
    except Exception:
        # last-resort direct call
        try:
            _show()
        except Exception:
            pass


def _log_debug(msg: str) -> None:
    """Append a timestamped message to an internal debug log and show it
    in the debug window if it's open and debug is enabled."""
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    debug_log_lines.append(line)
    if debug_enabled and debug_text_widget is not None:
        try:
            debug_text_widget.config(state='normal')
            debug_text_widget.insert('end', line + '\n')
            debug_text_widget.see('end')
            debug_text_widget.config(state='disabled')
        except Exception:
            pass


def _show_debug_window() -> None:
    """Create or raise a debug log window (Toplevel) with controls."""
    global debug_window, debug_text_widget, debug_enabled
    if debug_window is not None:
        try:
            debug_window.lift()
            debug_window.focus_force()  # Force focus when showing errors
            return
        except Exception:
            debug_window = None

    debug_window = tk.Toplevel(root_win if root_win is not None else None)
    debug_window.title('Debug Log (Text can be selected/copied here)')
    debug_window.geometry('800x400')  # Made window larger for better visibility

    txt = tk.Text(debug_window, wrap='none')
    txt.pack(fill='both', expand=True)
    txt.insert('end', '\n'.join(debug_log_lines) + ('\n' if debug_log_lines else ''))
    txt.config(state='disabled')
    debug_text_widget = txt

    frm = tk.Frame(debug_window)
    frm.pack(fill='x')

    def _save():
        try:
            path = os.path.join(os.getcwd(), 'ollama_debug.log')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(debug_log_lines))
            messagebox.showinfo('Saved', f'Debug log saved to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not save log: {e}')

    def _clear():
        nonlocal txt
        debug_log_lines.clear()
        txt.config(state='normal')
        txt.delete('1.0', 'end')
        txt.config(state='disabled')

    btn_save = tk.Button(frm, text='Save log', command=_save)
    btn_save.pack(side='left', padx=4, pady=4)
    btn_clear = tk.Button(frm, text='Clear', command=_clear)
    btn_clear.pack(side='left', padx=4, pady=4)
    chk_var = tk.BooleanVar(value=debug_enabled)

    def _on_chk():
        # update the global debug flag from the checkbox
        global debug_enabled
        debug_enabled = chk_var.get()

    chk = tk.Checkbutton(frm, text='Enable debug logging', variable=chk_var, command=_on_chk)
    chk.pack(side='right', padx=4, pady=4)


def _ollama_heartbeat_once() -> dict:
    """Perform one quick check using the Ollama Python client.

    Returns a dict with keys: 'service' (bool), 'model' (bool), 'debug' (str).
    """
    debug = []
    model_present = False
    service_running = False

    try:
        client = ollama.Client(host="http://localhost:11434")
        try:
            # Try to list models - this will fail if service isn't running
            models = client.list()
            service_running = True
            debug.append("Ollama service is running")
            debug.append(f"Raw models response: {models}")
            
            # Extract model names from response
            model_names = []
            try:
                for m in models.models:  # models.models is a list of Model objects
                    model_names.append(m.model)  # .model attribute contains the name
            except Exception as e:
                debug.append(f"Model parsing error: {e}")
                model_names = []
            
            debug.append(f"Extracted model names: {model_names}")
            if OLLAMA_MODEL in model_names:
                model_present = True
                debug.append(f"Model {OLLAMA_MODEL} is available")
            else:
                debug.append(f"Model {OLLAMA_MODEL} not found. Available: {model_names}")
                
        except ollama.RequestError as e:
            debug.append(f"Ollama service error: {e}")
            
    except Exception as e:
        debug.append(f"Failed to connect to Ollama: {e}")

    return {
        'service': service_running,
        'model': model_present,
        'debug': '; '.join(debug)
    }




def _ollama_heartbeat_loop() -> None:
    """Background loop that periodically pings the local Ollama CLI and
    updates the LLM indicator and debug log.
    """
    global _heartbeat_running
    _heartbeat_running = True
    while _heartbeat_running:
        try:
            res = _ollama_heartbeat_once()
            s = ''
            color = 'red'
            if not res['service']:
                s = 'LLM: Off (no service)'
                color = 'red'
            else:
                if res['model']:
                    s = 'LLM: On (ready)'
                    color = 'green'
                else:
                    s = 'LLM: On (no model)'
                    color = 'orange'

            # schedule UI update
            def _update_ui():
                try:
                    if llm_indicator is not None:
                        llm_indicator.config(text=s, fg=color)
                except Exception:
                    pass

            if root_win is not None:
                try:
                    root_win.after(0, _update_ui)
                except Exception:
                    pass

            # log debug info when errors or debug enabled
            if res['debug']:
                _log_debug(f"Heartbeat: {res['debug']}")
            elif debug_enabled:
                _log_debug(f"Heartbeat: service={res['service']} model={res['model']}")

        except Exception as e:
            _log_debug(f'Heartbeat loop error: {e}')

        time.sleep(_HEARTBEAT_INTERVAL)


def start_heartbeat() -> None:
    """Start the background heartbeat thread (idempotent)."""
    global _heartbeat_running
    if _heartbeat_running:
        return
    t = threading.Thread(target=_ollama_heartbeat_loop, daemon=True)
    t.start()


def _ollama_quick_check() -> None:
    """Do a single quick check and update the UI indicator immediately.

    This is used at startup so the UI doesn't show a misleading On state
    before we've verified ollama/model availability.
    """
    try:
        res = _ollama_heartbeat_once()
        if not res['cli']:
            s = 'LLM: Off (no ollama)'
            color = 'red'
        else:
            if res['model']:
                s = 'LLM: On (ready)'
                color = 'green'
            else:
                s = 'LLM: On (no model)'
                color = 'orange'

        def _update():
            try:
                if llm_indicator is not None:
                    llm_indicator.config(text=s, fg=color)
            except Exception:
                pass

        if root_win is not None:
            try:
                root_win.after(0, _update)
            except Exception:
                pass

        if res["debug"]:
            _log_debug(f'Quick check: {res["debug"]}')
        else:
            _log_debug(f'Quick check: cli={res["service"]} model={res["model"]}')
    except Exception as e:
        _log_debug(f'Quick check failed: {e}')


def build_ui(root: tk.Tk) -> None:
    """Constructs and initializes the complete application user interface.
    
    Creates and configures all UI elements including:
    1. Main title label
    2. Interactive button with initial placement
    3. LLM status indicator
    4. Hidden context menu for advanced features
    5. Keyboard shortcuts
    6. Debug window controls
    
    The UI uses multiple layout managers:
    - pack() for vertical stacking (label)
    - place() for precise positioning (button, indicators)
    
    Layout Strategy:
    - Button uses place() for free movement during gameplay
    - LLM indicator stays in top-right corner
    - Debug window is a separate Toplevel window
    - Context menu appears on right-click of main label
    
    Args:
        root: The main Tk window that will contain all widgets
    """
    global label, btn

    # Title label with a readable font size
    label = tk.Label(root, text="Don't Click the Button!", 
                     font=("Segoe UI", 14), 
                     **THEME['dark']['label'])
    label.pack(pady=(12, 4))

    # Click counter display below the title
    global counter_label
    counter_label = tk.Label(root, text="Clicks: 0", 
                            font=("Segoe UI", 10),
                            **THEME['dark']['label'])
    counter_label.pack(pady=(0, 8))

    # The button is wired to call `on_click` when pressed. We place it at a
    # starting coordinate; subsequent effects will reposition it.
    btn = tk.Button(root, text="Do NOT Click.", 
                    width=16, command=on_click,
                    **THEME['dark']['button'])
    # initial placement (x,y) inside window; y>40 leaves space for the label
    btn.place(x=100, y=50)

    def _apply_dynamic_theme(root_window: tk.Tk) -> None:
        """Apply dynamic color theme based on current difficulty."""
        colors = get_dynamic_colors(difficulty)
        root_window.configure(**colors['window'])
        if label is not None:
            label.configure(**colors['window'])
        if counter_label is not None:
            counter_label.configure(**colors['window'])
        if btn is not None:
            btn.configure(**colors['button'])
    
    # Initial dynamic theme application
    _apply_dynamic_theme(root)

    # Bind mouse motion to enable evasive behaviour when activated.
    root.bind('<Motion>', on_mouse_move)

    # LLM status indicator (top-right). Visible always so user knows whether
    # the app will attempt to call the local Ollama model.
    global llm_indicator
    llm_indicator = tk.Label(root, text="LLM: Checking...",
                             font=("Segoe UI", 9), fg=("orange"))

    def _place_indicator():
        try:
            w = root.winfo_width()
            llm_indicator.place(x=max(8, w - 100), y=6)
        except Exception:
            pass

    root.after(50, _place_indicator)

    # Do a one-off quick check immediately so the indicator reflects reality
    # instead of just the `llm_enabled` flag. Run in background so startup
    # isn't blocked.
    threading.Thread(target=_ollama_quick_check, daemon=True).start()

    # Start the regular heartbeat loop (idempotent)
    start_heartbeat()

    # Hidden toggle: right-click the main label to open a small context menu.
    menu = tk.Menu(root, tearoff=0)

    def _toggle_llm():
        global llm_enabled
        llm_enabled = not llm_enabled
        if llm_indicator is not None:
            llm_indicator.config(text=f"LLM: {'On' if llm_enabled else 'Off'}",
                                 fg=("green" if llm_enabled else "red"))

    def _show_llm_button(r: tk.Tk):
        """Reveal the hidden LLM toggle button (for debugging)."""
        global llm_toggle_btn
        if llm_toggle_btn is None:
            llm_toggle_btn = tk.Button(r, text=f"LLM: {'On' if llm_enabled else 'Off'}",
                                       command=_toggle_llm)
            llm_toggle_btn.place(x=100, y=90)
        else:
            # bring to front
            llm_toggle_btn.lift()

    menu.add_command(label="Toggle LLM (secret)", command=_toggle_llm)
    menu.add_command(label="Show LLM Button", command=lambda: _show_llm_button(root))
    menu.add_separator()
    menu.add_command(label="Show Debug Window", command=_show_debug_window)
    menu.add_command(label="Clear Debug Log", command=lambda: _show_debug_window() or debug_text_widget.master.after(100, lambda: debug_text_widget and debug_text_widget.delete('1.0', 'end')))

    def _on_label_rclick(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    label.bind('<Button-3>', _on_label_rclick)  # right-click on label

    # Keyboard shortcut: Ctrl+L toggles LLM
    root.bind_all('<Control-l>', lambda e: _toggle_llm())

def main() -> None:
    """Application entry point: create the root window, build UI, and run.

    Important: Tkinter runs an event loop with `mainloop()`; the program
    remains responsive while the loop is running and returns only after the
    user closes the window.
    """
    # Create the main application window
    root = tk.Tk()
    root.title(get_window_title())  # Set initial title
    # Set a reasonable default size. The layout will still expand if needed.
    root.geometry("320x120")

    # Apply dark theme to root window
    root.configure(**THEME['dark']['window'])
    
    # Override default dialog colors for message boxes
    root.option_add('*Dialog.msg.bg', THEME['dark']['messagebox']['bg'])
    root.option_add('*Dialog.msg.fg', THEME['dark']['messagebox']['fg'])
    root.option_add('*Dialog.bg', THEME['dark']['messagebox']['bg'])
    root.option_add('*Dialog.fg', THEME['dark']['messagebox']['fg'])
    root.option_add('*Dialog.Button.bg', THEME['dark']['button']['background'])
    root.option_add('*Dialog.Button.fg', THEME['dark']['button']['foreground'])

    # Build the user interface
    global root_win
    root_win = root
    build_ui(root)

    # Start the Tk event loop. This call is blocking until the window closes.
    root.mainloop()


if __name__ == "__main__":
    # Protect the entry point so importing this module doesn't start the UI.
    main()
