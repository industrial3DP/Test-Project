# Hello World Tkinter Tutorial

This small project demonstrates a minimal Tkinter GUI in Python that evolved into an interactive joke app. It showcases basic GUI programming, local LLM integration, and playful user interaction patterns.

## Files
- `python_test_0.1.py` — A well-commented Tkinter app featuring:
  - Interactive button that becomes increasingly difficult to click
  - Local LLM integration for dynamic responses using Ollama
  - Debug system for monitoring LLM interaction
  - Secret admin menu with advanced controls
  - Progressive difficulty system with visual effects

## Quick Start (Windows PowerShell)
```powershell
python "...\VS Workspaces\Test Project\python_test_0.1.py"
```

## What You'll Learn
- How to import and use `tkinter` and `messagebox`.
- Basic widget creation: `Label` and `Button`.
- Wiring a callback (`command=`) to react to user input.
- The meaning of the Tk event loop (`mainloop()`).

Notes and troubleshooting
- Tkinter is included with the standard CPython installer on Windows. If
  `import tkinter` fails, install Python from the official installer and
  ensure the "tcl/tk and IDLE" option is selected.
- This example uses a module-level variable for simplicity. In production
  code prefer a class-based structure for better encapsulation.

Ollama (local LLM) support
- This project can use a locally-installed Ollama model to generate dynamic
  snarky replies instead of static canned messages. Benefits: no network
  calls to remote APIs, more creative responses, and full local control.

Setup (Windows PowerShell)
1. Install Ollama and a model following Ollama's docs: https://ollama.ai
2. Verify `ollama` is in your PATH (PowerShell):
```powershell
ollama --help
```
3. (Optional) Choose or install a model. Set the model name in the environment
   variable `OLLAMA_MODEL` if you want a model other than the default used by
   the app. Example (PowerShell):
```powershell
$env:OLLAMA_MODEL = 'your_model_name'
```

How the app uses Ollama
- The app calls the Ollama CLI (`ollama generate <model> "prompt"`) on a
  background thread so the GUI doesn't freeze. If the CLI or model is not
  available or the call times out, the app falls back to canned snarky replies.
- The prompt is context-aware: it includes the click count and difficulty to
  produce tailored responses.

UI Features
- LLM Status Indicator: Located in the top-right corner
  - Green: LLM replies enabled
  - Red: LLM replies disabled
- Hidden Controls:
  - Right-click main label for secret menu with LLM options
  - Ctrl+L shortcut to toggle LLM on/off
  - Option to show permanent LLM toggle button
- Debug Window: Monitor LLM interactions and app state (via admin menu)
- Visual Feedback: Dynamic button effects and animations

Security and privacy
- All model generation happens locally via your Ollama installation. No
  content is sent to remote servers by this app unless you use a remote
  Ollama service intentionally.


New Features
- Click Counter: Tracks and displays button clicks in the main label
- Progressive Difficulty System:
  - Dynamic button movements with customizable patterns
  - Visual effects including shrinking, growing, and jiggling
  - Cursor evasion mechanics that increase with difficulty
- Secret Admin Menu (click title 100 times):
  - Button speed adjustment
  - Debug window toggle
  - Movement pattern selection
  - Visual effect customization
- The button remains intentionally catchable with persistence, though the 
  challenge increases with each click

If you want to explore further
- Convert the module-level state into an Application class.
- Add a UI control to toggle evasive behaviour on/off for experimentation.

Exercises (next steps for practice)
- Add a second button that restores the original label text.
- Use `grid()` instead of `pack()` to learn another geometry manager.
- Refactor the app into a class and move the callbacks into instance methods.

License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
