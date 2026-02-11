# Streamlit Deck

A customizable Stream Deck implementation running on your local machine, controlled via a web interface (perfect for iPad/Phone).

## Features

- **Customizable Grid**: Configure buttons with custom labels.
- **Hotkeys**: Trigger keyboard shortcuts on the host machine (e.g., `ctrl+c`, `volumemute`).
- **Scripts**: Execute local shell scripts or batch files.
- **Multiple Profiles**: Switch between different button layouts.
- **Web Interface**: Accessible from any device on your local network/tailnet.

## Installation (Recommended)

To install `streamlit-deck` as a permanent tool on your system using `uv`:

```bash
uv tool install git+https://github.com/fredericosantos/streamlit-deck
```

Once installed, you can run it from anywhere in your terminal:

```bash
streamlit-deck
```

The application will create `layouts/` and `scripts/` directories in your current working directory to store your configurations.

## Quick Try (Ephemeral)

If you just want to try it out without installing it globally, use `uvx`:

```bash
uvx --from git+https://github.com/fredericosantos/streamlit-deck streamlit-deck
```

## Development

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
-   `pynput`: Keyboard/Mouse control
