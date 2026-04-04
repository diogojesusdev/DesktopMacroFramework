import os
import sys
import threading
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from ..framework.MacroMonitorGUI import MacroMonitorGUI

from ..framework.Logger import Logger
from ..framework.types.MacroStatus import MacroStatus

# READ-ONLY
class RVariables:
    start_btn_text = "Play"
    start_btn_text_paused = "Continue"
    
    pause_btn_text = "Pause"
    stop_btn_text = "Stop"
    
    macro_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    macro_name = os.path.basename(macro_path)
    logger = Logger(macro_path)
    
    # Control macro pausing (default: not set)
    resumeMacroFlag = threading.Event()
    time_between_actions_s: float = 1 # default is 1 second

# READ-WRITE
class RWVariables:
    macroMonitorShared: Optional["MacroMonitorGUI"] = None
    
    stopMacro: bool = False
    highlightedMacroLineNumber: Optional[int] = None
    # Reset at macro restart. When set, the instructions on previous line numbers are skipped
    macroStartLineNumber: Optional[int] = None
    macroStatus: MacroStatus = MacroStatus.READY
    expectedWindowTitle: None | str = None