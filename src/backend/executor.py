import pyautogui
import subprocess
import os
import shlex
from typing import Optional

# Disable fail-safe for this application context if needed,
# but generally good to keep.
# pyautogui.FAILSAFE = True

SCRIPTS_DIR = "scripts"


def execute_hotkey(hotkey_string: str) -> str:
    """
    Executes a keyboard shortcut.
    Format example: "ctrl+c", "command+shift+4", "volumemute"
    """
    if not hotkey_string:
        return "No hotkey defined"

    try:
        keys = hotkey_string.lower().split("+")
        # Clean up whitespace
        keys = [k.strip() for k in keys]

        pyautogui.hotkey(*keys)
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
            # Try to make it executable? Or just warn?
            # Let's try to run it with 'sh' if it ends in .sh, otherwise generic execution
            pass

        # Run the script
        # Using Popen to run in background/detached might be better so UI doesn't hang?
        # But for 'Stream Deck' style, we usually want fire-and-forget.
        subprocess.Popen([script_path], cwd=os.getcwd())
        return f"Started script: {script_name}"
    except Exception as e:
        return f"Error running script: {e}"


def execute_action(action_type: str, payload: str) -> str:
    """
    Dispatcher for actions.
    """
    if action_type == "hotkey":
        return execute_hotkey(payload)
    elif action_type == "script":
        return execute_script(payload)
    else:
        return f"Unknown action type: {action_type}"
