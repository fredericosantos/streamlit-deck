# Streamlit Deck

A customizable Stream Deck implementation running on your local machine, controlled via a web interface (perfect for iPad/Phone).

## Features

- **Customizable Grid**: Configure buttons with custom labels.
- **Hotkeys**: Trigger keyboard shortcuts on the host machine (e.g., `ctrl+c`, `volumemute`).
- **Scripts**: Execute local shell scripts or batch files.
- **Multiple Profiles**: Switch between different button layouts.
- **Web Interface**: Accessible from any device on your local network/tailnet.

## Quick Start (via `uvx`)

You can run the application directly from the repository using `uvx` (part of the `uv` toolchain). This is the recommended way to try it out without cloning manually.

```bash
uvx --from git+https://github.com/fredericosantos/streamlit-deck streamlit-deck
```

This command will:
1.  Download the application.
2.  Install dependencies in an isolated environment.
3.  Launch the Streamlit server.
4.  Create `layouts/` and `scripts/` directories in your current folder for your configuration.

## Installation (Manual)

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/fredericosantos/streamlit-deck
    cd streamlit-deck
    uv sync
    ```

2.  **Run**:
    ```bash
    uv run streamlit run src/streamlit_deck/main.py
    ```

## Usage

1.  **Access**:
    -   Open the URL shown in the terminal (usually `http://localhost:8501`) on your local machine.
    -   To access from your iPad/Phone, ensure you are on the same network (or Tailnet) and use the `Network URL`.

2.  **Configuration**:
    -   Toggle **Edit Mode** in the sidebar.
    -   Click a button in the grid to configure it.
    -   **Hotkeys**: Enter keys separated by `+` (e.g., `command+space`, `ctrl+alt+delete`).
    -   **Scripts**: Add executable scripts to the `scripts/` directory (created in your current folder), then select them in the dropdown.
    -   **Important**: Ensure scripts have execution permissions (`chmod +x script.sh`).

## Dependencies

-   `streamlit`: UI
-   `pyautogui`: Keyboard/Mouse control
