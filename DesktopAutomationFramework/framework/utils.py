import inspect
import os
import time
import traceback
import pyautogui
import pygetwindow as gw

from DesktopAutomationFramework.framework.types.CustomErrors import MacroStoppedError

from ..framework.types.MacroStatus import MacroStatus
from ..framework.Variables import RVariables, RWVariables

def handleMasterEventsWhileRunning(func, args):
    if RWVariables.stopMacro:
        RWVariables.stopMacro = False
        raise MacroStoppedError("Macro Stopped")
    
    if not RVariables.resumeMacroFlag.is_set():
        print("[PAUSED] at", func.__name__, args)
        RWVariables.macroStatus = MacroStatus.PAUSED
        tryUpdateMacroStatusGUI()

    updatePlayButtonsConfigs()
    
    RVariables.resumeMacroFlag.wait()

    if RWVariables.stopMacro:
        RWVariables.stopMacro = False
        raise MacroStoppedError("Macro Stopped")

    RWVariables.macroStatus = MacroStatus.RUNNING
            
    updatePlayButtonsConfigs()
    tryUpdateMacroStatusGUI()

def updatePlayButtonsConfigs():
    ENABLED_BG = "white" 
    ENABLED_FG = "black" 
    DISABLED_BG = "light gray" 
    DISABLED_FG = "gray" 

    if RWVariables.macroMonitorShared is None: return
    
    def _reconfig():
        # print("RECONFIG => ", RWVariables.macroStatus)
        if RWVariables.macroMonitorShared is None: return
        if RWVariables.macroStatus is MacroStatus.READY:
            RWVariables.macroMonitorShared.startBtn.config(text=RVariables.start_btn_text, bg=ENABLED_BG, fg=ENABLED_FG)
            RWVariables.macroMonitorShared.pauseBtn.config(bg=DISABLED_BG, fg=DISABLED_FG)
            RWVariables.macroMonitorShared.stopBtn.config(bg=DISABLED_BG, fg=DISABLED_FG)
        elif RWVariables.macroStatus is MacroStatus.PAUSED:
            RWVariables.macroMonitorShared.startBtn.config(text=RVariables.start_btn_text_paused, bg=ENABLED_BG, fg=ENABLED_FG)
            RWVariables.macroMonitorShared.pauseBtn.config(bg=DISABLED_BG, fg=DISABLED_FG)
            RWVariables.macroMonitorShared.stopBtn.config(bg=ENABLED_BG, fg=ENABLED_FG)
        elif RWVariables.macroStatus is MacroStatus.RUNNING:
            RWVariables.macroMonitorShared.startBtn.config(text=RVariables.start_btn_text, bg=DISABLED_BG, fg=DISABLED_FG)
            RWVariables.macroMonitorShared.pauseBtn.config(bg=ENABLED_BG, fg=ENABLED_FG)
            RWVariables.macroMonitorShared.stopBtn.config(bg=ENABLED_BG, fg=ENABLED_FG)
    RWVariables.macroMonitorShared.root.after(0, _reconfig)

def checkActiveWindow():
    """ 
    Is the active window the expected one?
    if not try to select it
    check again
    if not raise exception 
    """
    if RWVariables.expectedWindowTitle is None: return
    
    try:
        initial_window_title = str(gw.getActiveWindowTitle()).lower()
    except:
        return
    
    # initial_window_title can be None sometimes (e.g., Windows Bar open). Just ignore that case
    if initial_window_title is None or initial_window_title.find(RWVariables.expectedWindowTitle) != -1:
        return
    
    # Active window is not the expected one. Try changing it
    windows = gw.getWindowsWithTitle(RWVariables.expectedWindowTitle)
    
    if len(windows) > 0:
        # Very important! If user clicks out and time.sleep() is not called, the window will be None
        time.sleep(1)
        
        # gw.getWindowsWithTitle(windows[0].title)
        window = windows[0]
        window.activate()
        
        time.sleep(1)

        try:
            actual_window_title = str(gw.getActiveWindowTitle()).lower()
        except: 
            return
        
        # Active window is not the expected one. Try changing it
        if actual_window_title.find(RWVariables.expectedWindowTitle) != -1:
            # SUCCESS: Able to recover (PRINTING WRONG VAR)
            print("Recovered window", "From:", initial_window_title, "To:", actual_window_title)
            return
        else:
            raise Exception("Was not in expected window and could not recover. Expected:", RWVariables.expectedWindowTitle, "Got:", initial_window_title)
    else:
        raise Exception("Was not in expected window and could not recover")

def get_source_around_line(window_size=8):
    frame = inspect.currentframe()
    if frame is None: raise Exception("Could not get code from stackframe")
    
    # Go 2 layers down
    caller_frame = frame.f_back
    if caller_frame is None: raise Exception("Could not get code from stackframe")
    caller_frame= caller_frame.f_back
    if caller_frame is None: raise Exception("Could not get code from stackframe")
    
    source_lines, start_line = inspect.getsourcelines(caller_frame)
    # jump annotation + def <fun_name>()
    source_lines = source_lines[2:]
    start_line += 2

    line_idx_abs = caller_frame.f_lineno - start_line

    # Calculate the start and end line numbers for the window
    start_line = max(0, line_idx_abs - window_size // 2)
    end_line = min(len(source_lines), line_idx_abs + (window_size // 2) + 1)

    # Extract the lines within the window
    window_lines = source_lines[start_line:end_line]
    line_index_rel = line_idx_abs - start_line

    return window_lines, line_index_rel

def get_full_source_code() -> list[tuple[int, str]]:
    frame = inspect.currentframe()
    if frame is None: raise Exception("Could not get code from stackframe")
    
    # Go 2 layers down
    caller_frame = frame.f_back
    if caller_frame is None: raise Exception("Could not get code from stackframe")
    caller_frame= caller_frame.f_back
    if caller_frame is None: raise Exception("Could not get code from stackframe")
    
    source_lines, start_line = inspect.getsourcelines(caller_frame)
    source_lines = [(start_line + i + 1, line.rstrip('\n')) for i, line in enumerate(source_lines)]
    source_lines = list(filter(lambda x: x[1] != "", source_lines))
    index = next((i for i, line in enumerate(source_lines) if "def macro(" in line[1]), None)
    if index is not None:
        source_lines = source_lines[index+1:]
        
    return source_lines

def get_macro_failure_line(error: Exception, macro_file_path: str) -> int | None:
    trace = traceback.extract_tb(error.__traceback__)
    normalized_macro_path = os.path.normcase(os.path.abspath(macro_file_path))

    for frame in reversed(trace):
        frame_path = os.path.normcase(os.path.abspath(frame.filename))
        if frame_path == normalized_macro_path:
            return frame.lineno

    return None

def tryUpdateMacroStatusGUI():
    if RWVariables.macroMonitorShared is None: return
    RWVariables.macroMonitorShared.updateStatus(RWVariables.macroStatus)

def showMacroErrorGUI(error_msg: str):
    if RWVariables.macroMonitorShared is None: raise Exception("MacroMonitor not initialized")
    RWVariables.macroMonitorShared.setMessage("ERROR: " + error_msg)