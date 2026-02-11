# Agent Operational Guidelines: Streamlit Deck

This document provides instructions for agentic coding agents working on the `streamlit-deck` repository.

## 1. Environment & Build

The project uses `uv` for dependency management and execution.

### Commands
- **Run Application:**
  ```bash
  uv run streamlit run src/streamlit_deck/main.py
  ```
- **Install/Sync Dependencies:**
  ```bash
  uv sync
  ```
- **Linting (Ruff):**
  ```bash
  # Check for linting errors
  uv run ruff check .
  # Fix auto-fixable errors
  uv run ruff check --fix .
  ```
- **Formatting:**
  ```bash
  uv run ruff format .
  ```
- **Testing:**
  *Note: Tests are not yet fully established. If adding tests, use `pytest`.*
  ```bash
  # Run all tests
  uv run pytest
  # Run a single test file
  uv run pytest tests/test_filename.py
  ```

## 2. Code Style & Conventions

### General
- **Python Version:** 3.13+
- **Formatting:** Adhere to standard Python PEP 8 conventions, enforced by Ruff.
- **Indentation:** 4 spaces.

### Type Hints
- **Strict Typing:** All function signatures must have type hints.
- Use `typing` module for complex types (`List`, `Dict`, `Optional`, `Union`, `Any`).
- Example:
  ```python
  def execute_action(action_type: str, payload: str) -> str:
      ...
  ```

### Imports
- **Grouping:** Standard library -> Third-party -> Local application.
- **Absolute Imports:** Prefer absolute imports for the internal package.
  ```python
  # Good
  from streamlit_deck.backend import config
  
  # Avoid if possible (unless within same sub-package)
  from . import config
  ```

### Naming
- **Variables/Functions:** `snake_case` (e.g., `execute_hotkey`, `layout_data`).
- **Classes:** `PascalCase` (e.g., `DeckController`).
- **Constants:** `UPPER_CASE` (e.g., `LAYOUTS_DIR`, `KEY_MAP`).

### Error Handling
- Use `try/except` blocks for external interactions (IO, System Calls, Pynput).
- Return descriptive error strings or log errors rather than crashing the app, as this is a UI-driven tool.
- Example:
  ```python
  try:
      # Critical operation
  except Exception as e:
      return f"Error executing operation: {e}"
  ```

## 3. Project Structure
- **Source Root:** `src/streamlit_deck/`
- **Entry Point:** `src/streamlit_deck/main.py` (Streamlit app), `src/streamlit_deck/cli.py` (CLI wrapper).
- **Backend:** `src/streamlit_deck/backend/` (Logic for config and execution).
- **UI:** `src/streamlit_deck/ui/` (Reusable components).
- **Runtime Data:** `layouts/` (JSON profiles) and `scripts/` (User scripts) are expected in the current working directory (CWD) when running.

## 4. Specific Patterns
- **Keyboard Control:** Use `pynput` (not `pyautogui`). Use the `KEY_MAP` in `executor.py` for string-to-key conversion.
- **Streamlit:** Use `st.session_state` for state management (e.g., `edit_mode`, `current_layout`).
- **Theme:** The theme is configured in `src/streamlit_deck/.streamlit/config.toml`. Do not hardcode colors in Python if possible; rely on the theme config.

## 5. Development Workflow
1.  **Analyze:** Read `__init__.py` files first to understand package structure. When working on Streamlit code, search for and use appropriate skills (e.g., `choosing-streamlit-selection-widgets`).
2.  **Plan:** Propose changes before executing.
3.  **Implement:** Edit files in `src/`.
4.  **Verify:** Run the app to ensure UI renders correctly and actions trigger.
5.  **Commit:** Follow [Conventional Commits](https://www.conventionalcommits.org/) structure.
    -   `feat:` New feature.
    -   `fix:` Bug fix.
    -   `refactor:` Code change that neither fixes a bug nor adds a feature.
    -   `docs:` Documentation only changes.
    -   `style:` Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
    -   `chore:` Build process or auxiliary tool changes.
    -   **Push to Origin**: Always `git push origin master` after making changes. Do not accumulate local changes without pushing.
