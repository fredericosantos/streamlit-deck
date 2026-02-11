# Streamlit Deck

A customizable Stream Deck implementation running on your local machine, controlled via a web interface (perfect for iPad/Phone).

## Features

- **Customizable Grid**: Configure buttons with custom labels.
- **Hotkeys**: Trigger keyboard shortcuts on the host machine (e.g., `ctrl+c`, `volumemute`).
- **Scripts**: Execute local shell scripts or batch files.
- **Multiple Profiles**: Switch between different button layouts.
- **Web Interface**: Accessible from any device on your local network/tailnet.

## Installation

1.  **Clone & Install**:
    ```bash
    git clone <repo_url>
    cd streamlit-deck
    uv sync
    ```

    *Note: This project uses `uv` for dependency management.*

2.  **Platform Specifics (macOS)**:
    -   You may need to grant **Accessibility** permissions to your terminal (e.g., iTerm, Terminal) or Python for `pyautogui` to control the keyboard.
    -   Go to `System Settings` -> `Privacy & Security` -> `Accessibility` and add your terminal application.

## Usage

1.  **Start the App**:
    ```bash
    uv run streamlit run app.py
    ```

2.  **Access**:
    -   Open the URL shown in the terminal (usually `http://localhost:8501`) on your local machine.
    -   To access from your iPad/Phone, ensure you are on the same network (or Tailnet) and use the `Network URL` displayed in the terminal output.

3.  **Configuration**:
    -   Toggle **Edit Mode** in the sidebar.
    -   Click a button in the grid to configure it.
    -   Choose **Hotkey** or **Script**.
    -   **Hotkeys**: Enter keys separated by `+` (e.g., `command+space`, `ctrl+alt+delete`).
    -   **Scripts**: Add executable scripts to the `scripts/` directory, then select them in the dropdown.

## adding Scripts

Place your executable scripts (`.sh`, `.py`, `.bat`) in the `scripts/` directory. Ensure they have execution permissions (`chmod +x script.sh`).

## Dependencies

-   `streamlit`: UI
-   `pyautogui`: Keyboard/Mouse control
