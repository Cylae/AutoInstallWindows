import os
import sys

def modify_file():
    with open("personalize.py", "r") as f:
        content = f.read()

    # Replacement 1
    content = content.replace(
        "import tkinter as tk\nfrom tkinter import ttk, messagebox\nfrom pathlib import Path",
        "try:\n    import tkinter as tk\n    from tkinter import ttk, messagebox\n    TclError = tk.TclError\nexcept ImportError:\n    tk = None\n    ttk = None\n    messagebox = None\n\n    class TclError(Exception):\n        pass\n\nfrom pathlib import Path"
    )

    # Replacement 2
    content = content.replace(
        "class PersonalizationApp(tk.Tk):\n    def __init__(self, xml_path, content, defaults):\n        super().__init__()",
        "class PersonalizationApp(tk.Tk if tk else object):\n    def __init__(self, xml_path, content, defaults):\n        if tk is None:\n            raise ImportError(\"tkinter is not available\")\n        super().__init__()"
    )

    # Replacement 3
    content = content.replace(
        "    try:\n        # Check if we are running in an environment without a display\n        # e.g., SSH without X11. This is a common failure point for Tkinter\n        if not os.environ.get('DISPLAY') and platform.system() != \"Windows\":\n            raise tk.TclError(\"No display available\")\n\n        app = PersonalizationApp(xml_path, content, defaults)\n        app.mainloop()\n    except (tk.TclError, ImportError) as e:\n        print(f\"GUI not available ({e}). Falling back to CLI mode...\")\n        try:\n            cli_main(xml_path, content, defaults)\n        except EOFError:\n            print(\"Error: Interactive input required, but EOF reached. \"\n                  \"Please run this tool in an interactive terminal.\")\n            sys.exit(1)",
        "    try:\n        if tk is None:\n            raise ImportError(\"tkinter module not found\")\n        # Check if we are running in an environment without a display\n        # e.g., SSH without X11. This is a common failure point for Tkinter\n        if not os.environ.get('DISPLAY') and platform.system() != \"Windows\":\n            raise TclError(\"No display available\")\n\n        app = PersonalizationApp(xml_path, content, defaults)\n        app.mainloop()\n    except (TclError, ImportError) as e:\n        print(f\"GUI not available ({e}). Falling back to CLI mode...\")\n        try:\n            cli_main(xml_path, content, defaults)\n        except EOFError:\n            print(\"Error: Interactive input required, but EOF reached. \"\n                  \"Please run this tool in an interactive terminal.\")\n            sys.exit(1)"
    )

    with open("personalize.py", "w") as f:
        f.write(content)

modify_file()
