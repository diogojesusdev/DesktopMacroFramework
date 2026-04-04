import tkinter as tk
from typing import Callable

from DesktopAutomationFramework.framework.Variables import RVariables, RWVariables

from ..framework.types.MacroStatus import MacroStatus

class MacroMonitorGUI:
    def __init__(
        self,
        macro_name: str,
        interval_between_instructions: float,
        source_code: list[tuple[int, str]],
        onStart: Callable[[], None],
        onPause: Callable[[], None],
        onStop:  Callable[[], None],
        onSchedule: Callable[['MacroMonitorGUI', str], None],
        onUpdate: Callable[[], None]
    ) -> None:
        self.source_code = source_code
        self.root = tk.Tk()
        self.root.title("Monitor - DesktopAutomationFramework") # Minimalist name to avoid conflict with window.select() by title
        self.root.attributes('-topmost', 1) # Make window always on top
        screen_width = self.root.winfo_screenwidth()
        window_width = 550
        window_height = 600
        x_position = screen_width - window_width
        y_position = 0
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        title = tk.Label(self.root, text=f"'{macro_name}'", font=("Arial", 18))
        self.label = tk.Label(self.root, text=MacroStatus.READY.name, font=("Arial", 14, "bold"))
        interval_between_instructions_s_label = tk.Label(self.root, text=f"Interval Between Instructions: {interval_between_instructions}s", font=("Arial", 13))
        # updateBtn = tk.Button(self.root, text="Update", command=onUpdate, font=("Arial", 12))
        self.startBtn = tk.Button(self.root, text=RVariables.start_btn_text, command=onStart, font=("Arial", 12))
        self.pauseBtn = tk.Button(self.root, text=RVariables.pause_btn_text, command=onPause, font=("Arial", 12))
        self.stopBtn = tk.Button(self.root, text=RVariables.stop_btn_text, command=onStop, font=("Arial", 12))
        
        selected_option = tk.StringVar(self.root)
        selected_option.set("Schedule Run")
        def _onSchedule(time): onSchedule(self, time.split(' ')[0])
        option_menu = tk.OptionMenu(self.root, selected_option, "1 min", "5 mins", "10 mins", "30 mins", "60 mins", command=_onSchedule)
        
        # Create a code list
        self.listbox = tk.Listbox(self.root, font=("Arial", 12), width=60, height=15)# )
        for code_line in source_code:
            code_line = code_line[1]
            self.listbox.insert(tk.END, code_line)
        self.listbox.select_set(0)
        if source_code:
            RWVariables.highlightedMacroLineNumber = source_code[0][0]
        def on_item_selected(_):
            if not self.listbox.curselection():
                return
            # Get the index of the selected item
            if RWVariables.macroStatus is MacroStatus.RUNNING:
                self.listbox.selection_clear(0, tk.END)
            else:
                selected_index = self.listbox.curselection()[0]
                RWVariables.macroStartLineNumber = source_code[selected_index][0]
                RWVariables.highlightedMacroLineNumber = source_code[selected_index][0]
                onStop() # the flag indicates if the stop request was made by the user or the program
        self.listbox.bind("<<ListboxSelect>>", on_item_selected)
        
        # Packing
        title.pack(padx=5, pady=5)
        # updateBtn.pack(padx=5, pady=5)
        interval_between_instructions_s_label.pack(padx=5, pady=5)
        self.label.pack(padx=5, pady=5)
        self.listbox.pack()
        self.startBtn.pack(side=tk.LEFT)
        self.pauseBtn.pack(side=tk.LEFT)
        self.stopBtn.pack(side=tk.LEFT)
        option_menu.pack(side=tk.LEFT)
        pass

    def launchGUI(self):
        self.root.mainloop()

    def updateStatus(self, status: MacroStatus):
        def _change(): self.label.config(text=status.name)
        self.root.after(0, _change)

    def setMessage(self, msg: str):
        def _change(): self.label.config(text=break_text_into_lines(msg))
        self.root.after(0, _change)

    def updateInstruction(self, code_line: int):
        code_line = code_line
        def changeInstructionsWindow():
            self.listbox.selection_clear(0, tk.END)
            
            for idx, item in enumerate(self.source_code):
                if item[0] == code_line:
                    RWVariables.highlightedMacroLineNumber = code_line
                    self.listbox.select_set(idx)
                    # make sure user can see the items after the selected item
                    if idx > 4:
                        self.listbox.see(idx + 4)
                    else:
                        self.listbox.see(idx)

        self.root.after(0, changeInstructionsWindow)
        pass

    def showPopup(self, msg: str):
        popup = tk.Toplevel(self.root)
        popup.title("Popup Window")
        popup.attributes('-topmost', 1)

        # Calculate the screen width and height
        x = (popup.winfo_screenwidth() - popup.winfo_reqwidth()) // 2
        y = (popup.winfo_screenheight() - popup.winfo_reqheight()) // 2
        popup.geometry(f"+{x}+{y}")

        # Add content to the popup window
        label = tk.Label(popup, text=break_text_into_lines(msg))
        label.pack(padx=20, pady=20)

        # Add a button to close the popup
        close_button = tk.Button(popup, text="OK", command=popup.destroy)
        close_button.pack(pady=10)

        popup.wait_window()
    
def break_text_into_lines(text, words_per_line=6):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if len(current_line) >= words_per_line:
            lines.append(" ".join(current_line))
            current_line = []

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)