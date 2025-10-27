# Hello World Tkinter Tutorial

This small project demonstrates a minimal Tkinter GUI in Python. It's
intended as a tutorial/example you can read and run to learn the basics.

Files
- `python_test_0.1.py` — A short, well-commented Tkinter app: a label and a
  button. Clicking the button updates the label and shows an info dialog.
  The project has been extended into a joke app where the button becomes
  increasingly evasive: it moves, changes size, jiggles, and can evade the
  cursor after repeated clicks. A click counter tracks how many times the
  user has clicked the button.

Quick start (Windows PowerShell)
```powershell
python "...\VS Workspaces\Test Project\python_test_0.1.py"
```

What you'll learn
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

New behaviours (joke app)
- The app counts button clicks and displays the count in the main label.
- Each click increases the "difficulty" and triggers an effect:
  - small random moves, shrinking/growing, jiggle animation, and cursor-evade.
- The button remains clickable by design; the effects are intentionally
  mild so you can still catch it with persistence.

If you want to explore further
- Convert the module-level state into an Application class.
- Add a UI control to toggle evasive behaviour on/off for experimentation.

Exercises (next steps for practice)
- Add a second button that restores the original label text.
- Use `grid()` instead of `pack()` to learn another geometry manager.
- Refactor the app into a class and move the callbacks into instance methods.

License
- This small tutorial is MIT-style: use and adapt freely.
