import tkinter as tk
from typing import Any
from pymsgbox import alert as _alert, confirm as _confirm, prompt as _prompt, OK_TEXT as OK, YES_TEXT as YES, NO_TEXT as NO, CANCEL_TEXT as CANCEL, IGNORE_TEXT as IGNORE, CONTINUE_TEXT as CONTINUE, RETRY_TEXT as RETRY

from ..framework.Decorators.AutomationDecorator import AutomationDecorator

class gui:
    OK = OK
    YES = YES
    NO = NO
    CANCEL = CANCEL
    IGNORE = IGNORE
    CONTINUE = CONTINUE
    RETRY = RETRY

    @AutomationDecorator
    @staticmethod
    def show(text, title = ""):
        return  _alert(str(text), str(title), _tkinter=False)

    @AutomationDecorator
    @staticmethod
    def confirm(text, title = "") -> bool:
        return _confirm(str(text), str(title), buttons=(YES, NO), _tkinter=False) == YES
    
    @AutomationDecorator
    @staticmethod
    def customWindow(text, title = "", buttons: Any = (OK, CANCEL)):
        return _confirm(str(text), str(title), buttons, _tkinter=False)

    @AutomationDecorator
    @staticmethod
    def ask(text, title = "", default = "") -> str:
        res = _prompt(str(text), str(title), default)
        if res is None:
            raise Exception("Input dialog was closed without a value")
        return res

    @AutomationDecorator
    @staticmethod
    def options(*options: str):
        selected_option = None

        def on_select(option):
            nonlocal selected_option
            selected_option = option
            root.destroy()

        root = tk.Tk()
        root.title("Select an Option")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - root.winfo_reqwidth()) // 2
        y = (screen_height - root.winfo_reqheight()) // 2
        root.geometry(f"+{x}+{y}")

        for option in options:
            frame = tk.Frame(root, padx=10, pady=10)
            frame.pack(fill=tk.BOTH, expand=True)
            button = tk.Button(frame, text=option, command=lambda o=option: on_select(o))
            button.pack(fill=tk.BOTH, expand=True)

        # root.protocol("WM_DELETE_WINDOW", root.quit)  # Handle window close button

        root.mainloop()

        if selected_option is None:
            raise Exception("Option selection was cancelled before a choice was made")

        return selected_option