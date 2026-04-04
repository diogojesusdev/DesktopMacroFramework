import datetime
from functools import wraps
import inspect
import os
import subprocess
import sys
import threading
import time

from DesktopAutomationFramework.framework.types.CustomErrors import MacroStoppedError

from ..MacroMonitorGUI import MacroMonitorGUI
from ..types.MacroStatus import MacroStatus
from ..utils import get_full_source_code, get_macro_failure_line, showMacroErrorGUI, tryUpdateMacroStatusGUI, updatePlayButtonsConfigs
from ..Variables import RVariables, RWVariables
from ..SelfUpdate import SelfUpdate
from ...automation.Variables import vars


class Macro:
    source_code: list[tuple[int, str]] = []
    
    def __init__(self):
        global source_code
        self.auto_run = False
        self.exit_after_run = False
        Macro.source_code = get_full_source_code()
        
        for arg in sys.argv:
            if arg.startswith('--interval_s='):
                RVariables.time_between_actions_s = float(arg.replace('--interval_s=', ''))
            elif arg == '--auto-run':
                self.auto_run = True
            elif arg == '--exit-after-run':
                self.exit_after_run = True
        
    def __call__(self, func):
        macro_file_path = inspect.getsourcefile(func) or os.path.abspath(sys.argv[0])
        # Start/Resume       
        @wraps(func) 
        def wrapper():
            # Runs once: when macro() is called
            if not os.path.exists(vars.output_folder):
                os.makedirs(vars.output_folder)
                print("Created output folder")
            else:
                print("Output folder already exists")

            def recursive_macro_runner(errored_on_previous_run: bool = False, auto_run: bool = False):
                try:
                    RWVariables.expectedWindowTitle = None
                    RVariables.logger.new_file()
                    RWVariables.macroStatus = MacroStatus.READY
                    if RWVariables.macroMonitorShared is not None and RWVariables.highlightedMacroLineNumber is not None:
                        RWVariables.macroMonitorShared.updateInstruction(RWVariables.highlightedMacroLineNumber)
                    updatePlayButtonsConfigs()
                    if not errored_on_previous_run:
                        tryUpdateMacroStatusGUI()
                    else:
                        # Reset Error
                        errored_on_previous_run = False
                        # Leave the error message there
                        pass

                    print("[READY]")
                    
                    if auto_run:
                        # Start running macro immediately
                        RVariables.resumeMacroFlag.set()
                    else:
                        # Pause and wait until started
                        RVariables.resumeMacroFlag.clear()
                        RVariables.resumeMacroFlag.wait()
                        
                    RWVariables.macroStatus = MacroStatus.RUNNING
                    print("[RUNNING]")
                    tryUpdateMacroStatusGUI()
                    # Call macro() function
                    func()
                except Exception as e:
                    errored_on_previous_run = True
                    error_message = str(e)

                    failed_line_number = get_macro_failure_line(e, macro_file_path)
                    if failed_line_number is not None:
                        RWVariables.highlightedMacroLineNumber = failed_line_number
                        if RWVariables.macroMonitorShared is not None:
                            RWVariables.macroMonitorShared.updateInstruction(failed_line_number)
                    
                    showMacroErrorGUI(error_message)
                    RVariables.logger.error(error_message)
                    
                    # if RWVariables.macroMonitorShared is not None:
                    #     RWVariables.macroMonitorShared.showPopup(error_message)
                finally:
                    if self.exit_after_run:
                        os._exit(1)
                    # Call itself again
                    recursive_macro_runner(errored_on_previous_run, auto_run=False)
            
            RWVariables.macroMonitorShared = MacroMonitorGUI(
                RVariables.macro_name,
                RVariables.time_between_actions_s,
                Macro.source_code,
                self.onMacroStartResume,
                self.onMacroPause,
                self.onMacroStop,
                self.onMacroSchedule,
                onUpdate=SelfUpdate
            )
            
            # Start Macro Runner Thread
            thread = threading.Thread(target=lambda: recursive_macro_runner(errored_on_previous_run=False, auto_run=self.auto_run))
            thread.daemon = True # If main thread dies it dies too
            thread.start()
            
            updatePlayButtonsConfigs()
            
            # ! Blocks the main thread on tkinter GUI
            RWVariables.macroMonitorShared.launchGUI()
        
        wrapper() # start execution
        return wrapper
    
    def onMacroStartResume(self):
        if RWVariables.macroStatus is MacroStatus.PAUSED or RWVariables.macroStatus is MacroStatus.READY:
            time.sleep(3)
            RVariables.resumeMacroFlag.set()
            updatePlayButtonsConfigs()
        
    @staticmethod
    def onMacroPause():
        if RWVariables.macroStatus is MacroStatus.RUNNING:
            RVariables.resumeMacroFlag.clear()
            updatePlayButtonsConfigs()
    
    def onMacroStop(self):
        if RWVariables.macroStatus is MacroStatus.RUNNING or RWVariables.macroStatus is MacroStatus.PAUSED:
            RWVariables.stopMacro = True
            updatePlayButtonsConfigs()
            if RWVariables.macroStatus is MacroStatus.PAUSED:
                # Make thread resume in order to realize it should stop
                RVariables.resumeMacroFlag.set()
    
    def onMacroSchedule(self, macroMonitor: MacroMonitorGUI, time: str):
        start_time = datetime.datetime.now() + datetime.timedelta(minutes=float(time))
        start_time_str = start_time.strftime("%H:%M:%S")
        start_time_str_name = start_time.strftime("%H-%M-%S")
        
        abs_script_location = os.path.abspath(sys.argv[0])
        args = ' '.join(sys.argv[1:])
        
        command = f"pythonw \"{abs_script_location}\" {args}"

        schtasks_command = f"schtasks /create /sc once /tn DesktopAutomation_{RVariables.macro_name}_{start_time_str_name} /tr \"{command}\" /st {start_time_str} /F"

        print("Scheduling task:", schtasks_command)

        try:
            result = subprocess.run(schtasks_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Task scheduled successfully.")
            print("Command output:", result.stdout.decode())
            exit()
        except subprocess.CalledProcessError as e:
            print("Error scheduling task:", e.stderr.decode())
            macroMonitor.showPopup(f"Error scheduling task: {e.stderr.decode()}")