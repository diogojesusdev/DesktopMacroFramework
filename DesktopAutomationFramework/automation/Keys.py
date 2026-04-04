import enum
from pynput.keyboard import Key as OriginalKey

class MyKey(enum.Enum):
    alt = "alt"
    alt_gr = "alt_gr"
    backspace = "backspace"
    caps_lock = "caps_lock"
    win = "win"
    ctrl = "ctrl"
    delete = "delete"
    down = "down"
    end = "end"
    enter = "enter"
    esc = "esc"
    f1 = "f1"
    f2 = "f2"
    f3 = "f3"
    f4 = "f4"
    f5 = "f5"
    f6 = "f6"
    f7 = "f7"
    f8 = "f8"
    f9 = "f9"
    f10 = "f10"
    f11 = "f11"
    f12 = "f12"
    home = "home"
    left = "left"
    page_down = "page_down"
    page_up = "page_up"
    right = "right"
    shift = "shift"
    space = "space"
    tab = "tab"
    up = "up"
    insert = "insert"
    menu = "menu"
    num_lock = "num_lock"
    pause = "pause"
    print_screen = "print_screen"
    scroll_lock = "scroll_lock"

def convert_to_original_key(custom_key: MyKey):
    key_mapping = {
        MyKey.alt: OriginalKey.alt,
        MyKey.alt_gr: OriginalKey.alt_gr,
        MyKey.backspace: OriginalKey.backspace,
        MyKey.caps_lock: OriginalKey.caps_lock,
        MyKey.win: OriginalKey.cmd,
        MyKey.ctrl: OriginalKey.ctrl,
        MyKey.delete: OriginalKey.delete,
        MyKey.down: OriginalKey.down,
        MyKey.end: OriginalKey.end,
        MyKey.enter: OriginalKey.enter,
        MyKey.esc: OriginalKey.esc,
        MyKey.f1: OriginalKey.f1,
        MyKey.f2: OriginalKey.f2,
        MyKey.f3: OriginalKey.f3,
        MyKey.f4: OriginalKey.f4,
        MyKey.f5: OriginalKey.f5,
        MyKey.f6: OriginalKey.f6,
        MyKey.f7: OriginalKey.f7,
        MyKey.f8: OriginalKey.f8,
        MyKey.f9: OriginalKey.f9,
        MyKey.f10: OriginalKey.f10,
        MyKey.f11: OriginalKey.f11,
        MyKey.f12: OriginalKey.f12,
        MyKey.home: OriginalKey.home,
        MyKey.left: OriginalKey.left,
        MyKey.page_down: OriginalKey.page_down,
        MyKey.page_up: OriginalKey.page_up,
        MyKey.right: OriginalKey.right,
        MyKey.shift: OriginalKey.shift,
        MyKey.space: OriginalKey.space,
        MyKey.tab: OriginalKey.tab,
        MyKey.up: OriginalKey.up,
        MyKey.insert: OriginalKey.insert,
        MyKey.menu: OriginalKey.menu,
        MyKey.num_lock: OriginalKey.num_lock,
        MyKey.pause: OriginalKey.pause,
        MyKey.print_screen: OriginalKey.print_screen,
        MyKey.scroll_lock: OriginalKey.scroll_lock
    }
    result = key_mapping.get(custom_key)
    if result is None: raise Exception(f"Unsupported key '{custom_key}'")
    return result