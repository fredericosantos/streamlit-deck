import subprocess
import os
from pynput.keyboard import Key, Controller as KeyboardController, KeyCode
from pynput.mouse import Button, Controller as MouseController
from typing import Union
from streamlit_deck.backend import apps

keyboard = KeyboardController()
mouse = MouseController()

SCRIPTS_DIR = "scripts"

# Map string names to pynput Keys
KEY_MAP = {
    # Modifiers
    "ctrl": Key.ctrl,
    "shift": Key.shift,
    "alt": Key.alt,
    "opt": Key.alt,  # Mac alias
    "cmd": Key.cmd,
    "command": Key.cmd,  # Mac alias
    "super": Key.cmd,  # Linux/Windows key often mapped to cmd in pynput on Mac
    "win": Key.cmd,
    # Function Keys
    "f1": Key.f1,
    "f2": Key.f2,
    "f3": Key.f3,
    "f4": Key.f4,
    "f5": Key.f5,
    "f6": Key.f6,
    "f7": Key.f7,
    "f8": Key.f8,
    "f9": Key.f9,
    "f10": Key.f10,
    "f11": Key.f11,
    "f12": Key.f12,
    "f13": Key.f13,
    "f14": Key.f14,
    "f15": Key.f15,
    "f16": Key.f16,
    "f17": Key.f17,
    "f18": Key.f18,
    "f19": Key.f19,
    "f20": Key.f20,
    # Navigation / Editing
    "enter": Key.enter,
    "return": Key.enter,
    "esc": Key.esc,
    "escape": Key.esc,
    "space": Key.space,
    "tab": Key.tab,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "home": Key.home,
    "end": Key.end,
    "pageup": Key.page_up,
    "pagedown": Key.page_down,
    "capslock": Key.caps_lock,
    # Media Keys
    "volumemute": Key.media_volume_mute,
    "volumeup": Key.media_volume_up,
    "volumedown": Key.media_volume_down,
    "playpause": Key.media_play_pause,
    "nexttrack": Key.media_next,
    "prevtrack": Key.media_previous,
}

MOUSE_MAP = {
    "left_click": Button.left,
    "right_click": Button.right,
    "middle_click": Button.middle,
    "double_left_click": "double_left",
}


def get_key_object(key_name: str) -> Union[Key, KeyCode]:
    """
    Convert a string key name to a pynput Key or KeyCode object.
    """
    key_name = key_name.lower().strip()

    # Check known special keys
    if key_name in KEY_MAP:
        return KEY_MAP[key_name]

    # Handle single characters (e.g. 'a', '1', '.')
    if len(key_name) == 1:
        return KeyCode.from_char(key_name)

    # Fallback: try to just use the character if it's not a known special key
    # This might fail for unknown long strings, but is a reasonable default
    try:
        return KeyCode.from_char(key_name[0])
    except (ValueError, TypeError):
        return None


def execute_hotkey(hotkey_string: str) -> str:
    """
    Executes a keyboard shortcut using pynput.
    Format example: "ctrl+c", "command+shift+4", "volumemute"
    """
    if not hotkey_string:
        return "No hotkey defined"

    try:
        parts = hotkey_string.split("+")
        keys_to_press = []

        for part in parts:
            key_obj = get_key_object(part)
            if key_obj:
                keys_to_press.append(key_obj)
            else:
                return f"Unknown key: {part}"

        # Press keys in order
        for k in keys_to_press:
            keyboard.press(k)

        # Release keys in reverse order
        for k in reversed(keys_to_press):
            keyboard.release(k)

        return f"Executed hotkey: {hotkey_string}"
    except Exception as e:
        return f"Error executing hotkey: {e}"


def execute_script(script_name: str) -> str:
    """
    Executes a script from the scripts directory.
    """
    if not script_name:
        return "No script selected"

    script_path = os.path.join(SCRIPTS_DIR, script_name)

    if not os.path.exists(script_path):
        return f"Script not found: {script_name}"

    try:
        # Check if executable
        if not os.access(script_path, os.X_OK):
            # On Linux/Mac, we can try to chmod it, but usually user should do this.
            pass

        # Run the script in detached mode / background
        subprocess.Popen([script_path], cwd=os.getcwd())
        return f"Started script: {script_name}"
    except Exception as e:
        return f"Error running script: {e}"


def execute_mouse(action: str) -> str:
    """
    Executes a mouse action.
    """
    try:
        if action == "double_left_click":
            mouse.click(Button.left, 2)
            return "Executed double left click"

        if action in MOUSE_MAP:
            btn = MOUSE_MAP[action]
            mouse.click(btn)
            return f"Executed mouse click: {action}"

        return f"Unknown mouse action: {action}"
    except Exception as e:
        return f"Error executing mouse action: {e}"


def execute_action(action_type: str, payload: str) -> str:
    """
    Dispatcher for actions.
    """
    if action_type == "hotkey":
        return execute_hotkey(payload)
    elif action_type == "script":
        return execute_script(payload)
    elif action_type == "mouse":
        return execute_mouse(payload)
    elif action_type == "app":
        return apps.launch_app(payload)
    else:
        return f"Unknown action type: {action_type}"
