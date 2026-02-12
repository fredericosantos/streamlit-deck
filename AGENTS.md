# Agent Operational Guidelines: Streamlit Deck

This document provides instructions for agentic coding agents working on the `streamlit-deck` repository.

## 1. Environment & Build

The project uses `uv` for dependency management and execution, with Python 3.13+.

### Commands
- **Run Application:**
  ```bash
  uv run streamlit run src/streamlit_deck/main.py
  ```
- **Install/Sync Dependencies:**
  ```bash
  uv sync
  ```
- **Development Setup:**
  ```bash
  git clone https://github.com/fredericosantos/streamlit-deck
  cd streamlit-deck
  uv sync
  uv run streamlit run src/streamlit_deck/main.py
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
- **Type Checking (Future):**
  ```bash
  # When mypy is added
  uv run mypy src/
  ```
- **Testing:**
  *Note: Tests are not yet fully established. When adding tests, use `pytest`.*
  ```bash
  # Run all tests
  uv run pytest
  # Run a single test file
  uv run pytest tests/test_filename.py
  # Run tests with coverage
  uv run pytest --cov=src/streamlit_deck --cov-report=html
  # Run specific test function
  uv run pytest tests/test_filename.py::TestClass::test_function
  ```

## 2. Code Style & Conventions

### General
- **Python Version:** 3.13+
- **Formatting:** Adhere to standard Python PEP 8 conventions, enforced by Ruff.
- **Indentation:** 4 spaces.
- **Line Length:** 88 characters (Black/Ruff default).
- **Docstrings:** Use triple-quoted strings for all module, class, and function documentation.

### Type Hints
- **Strict Typing:** All function signatures must have type hints.
- Use `typing` module for complex types (`List`, `Dict`, `Optional`, `Union`, `Any`).
- Use modern type annotation syntax where possible.
- Example:
  ```python
  from typing import List, Dict, Optional, Any

  def execute_action(action_type: str, payload: str) -> str:
      ...

  def process_layout(layout: Dict[str, Any]) -> Optional[List[str]]:
      ...
  ```

### Imports
- **Grouping:** Standard library -> Third-party -> Local application.
- **Absolute Imports:** Prefer absolute imports for the internal package.
- **Import Sorting:** Ruff will handle import sorting automatically.
  ```python
  # Good
  import os
  import tempfile
  from typing import Dict, List, Optional

  import streamlit as st
  from PIL import Image

  from streamlit_deck.core.backend import config, base_executor
  from streamlit_deck.platform import get_apps
  ```

### Naming Conventions
- **Variables/Functions:** `snake_case` (e.g., `execute_hotkey`, `layout_data`, `get_app_icon`).
- **Classes:** `PascalCase` (e.g., `DeckController`, `LayoutManager`).
- **Constants:** `UPPER_CASE` (e.g., `LAYOUTS_DIR`, `KEY_MAP`, `MEDIA_MAP`).
- **Private Members:** Prefix with underscore (e.g., `_internal_method`).
- **Modules:** `snake_case` (e.g., `config.py`, `executor.py`).

### Error Handling
- Use `try/except` blocks for external interactions (IO, System Calls, Pynput).
- Return descriptive error strings or log errors rather than crashing the app, as this is a UI-driven tool.
- Use specific exception types when possible.
- Example:
  ```python
  try:
      # Critical operation
      with open(file_path, 'r') as f:
          return f.read()
  except FileNotFoundError:
      return f"File not found: {file_path}"
  except PermissionError:
      return f"Permission denied: {file_path}"
  except Exception as e:
      return f"Error reading file: {e}"
  ```

### Streamlit-Specific Patterns
- **Session State:** Use descriptive keys (e.g., `current_layout_name`, `edit_mode`).
- **Callbacks:** Define callback functions at module level, not inside UI blocks.
- **State Initialization:** Check and initialize session state at the top of the main function.
- **Temporary Files:** Clean up temp files immediately after use to prevent accumulation.
- **Image Handling:** Convert PIL images to bytes for Streamlit display.

### File Structure Patterns
- **Constants:** Define module-level constants at the top after imports.
- **Helper Functions:** Place utility functions before main UI logic.
- **Main Logic:** Use clear section dividers with comments (e.g., `# --- Sidebar ---`).
- **Configuration:** Keep UI configuration separate from business logic.

## 3. Project Structure

- **Source Root:** `src/streamlit_deck/`
- **Entry Points:**
  - `src/streamlit_deck/main.py` (Streamlit app)
  - `src/streamlit_deck/cli.py` (CLI wrapper)
- **Backend:** `src/streamlit_deck/backend/` (Logic for config and execution)
  - `config.py` - Configuration and layout management
  - `executor.py` - Action execution (hotkeys, scripts, mouse)
  - `apps.py` - Application detection and launching
- **UI:** `src/streamlit_deck/ui/` (Reusable components)
- **Configuration:** `src/streamlit_deck/.streamlit/config.toml` (Streamlit theme)
- **Runtime Data:** `layouts/` (JSON profiles) and `scripts/` (User scripts) are expected in the current working directory (CWD) when running.

## 4. Specific Patterns

### Keyboard/Mouse Control
- **Use `pynput`:** Not `pyautogui` for cross-platform compatibility.
- **Key Mapping:** Use the `KEY_MAP` in `executor.py` for string-to-key conversion.
- **Media Keys:** Support special media keys (volume, play/pause, etc.).

### Streamlit Best Practices
- **Session State:** Use `st.session_state` for all persistent state management.
- **Rerun Logic:** Use `st.rerun()` sparingly and only when necessary.
- **Containers:** Use `st.container()` for complex layouts.
- **Columns:** Use `st.columns()` for grid layouts.
- **Theme:** The theme is configured in `src/streamlit_deck/.streamlit/config.toml`. Do not hardcode colors in Python if possible; rely on the theme config.

### Icon and Image Handling
- **App Icons:** Extract from macOS .app bundles using PIL and convert to PNG bytes.
- **Caching:** Use hashed cache keys for app icon storage.
- **Display:** Show icons above buttons using `st.image()` for reliable rendering.
- **Temp Files:** Avoid temporary file creation - work directly with byte data.

### Configuration Management
- **JSON Storage:** Use JSON files for layout persistence.
- **Directory Creation:** Auto-create required directories.
- **Default Layouts:** Provide sensible defaults when files don't exist.
- **Validation:** Validate configuration data before use.

## 5. Development Workflow

1.  **Analyze:** Read `__init__.py` files first to understand package structure. When working on Streamlit code, search for and use appropriate skills (e.g., `choosing-streamlit-selection-widgets`).
2.  **Plan:** Propose changes before executing. Create todos for multi-step tasks.
3.  **Implement:** Edit files in `src/`. Follow the established patterns.
4.  **Verify:** Run the app to ensure UI renders correctly and actions trigger. Test on multiple platforms if possible.
5.  **Lint & Format:** Always run `uv run ruff check . && uv run ruff format .` before committing.
6.  **Commit:** Follow [Conventional Commits](https://www.conventionalcommits.org/) structure.
    -   `feat:` New feature.
    -   `fix:` Bug fix.
    -   `refactor:` Code change that neither fixes a bug nor adds a feature.
    -   `docs:` Documentation only changes.
    -   `style:` Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
    -   `chore:` Build process or auxiliary tool changes.
7.  **Push to Origin**: Always `git push origin master` after making changes. Do not accumulate local changes without pushing.

## 6. Quality Assurance

### Code Quality Checks
```bash
# Full quality check before PR
uv run ruff check . --fix
uv run ruff format .
python -m py_compile src/streamlit_deck/*.py
python -m py_compile src/streamlit_deck/**/*.py
```

### Testing Guidelines
- **Unit Tests:** Test individual functions and classes.
- **Integration Tests:** Test full workflows (layout loading, action execution).
- **UI Tests:** Verify Streamlit components render correctly.
- **Cross-Platform:** Test on macOS, Linux, and Windows when possible.

### Performance Considerations
- **Image Loading:** Cache app icons to avoid repeated extraction.
- **File I/O:** Minimize disk access in hot paths.
- **Memory:** Clean up temporary files and large objects.
- **UI Responsiveness:** Avoid blocking operations in UI threads.

## 7. Security Considerations

- **File Access:** Validate all file paths to prevent directory traversal.
- **Command Execution:** Sanitize script paths and commands.
- **Permissions:** Check file permissions before execution.
- **Network:** Be cautious with network-accessible Streamlit apps.
- **Secrets:** Never commit sensitive information or API keys.

## 8. Platform-Specific Notes

### macOS
- App icons extracted from `.app` bundles using PIL.
- Use `open` command for launching applications.
- Support for macOS-specific key mappings.

### Linux
- App icons from `.desktop` files.
- Use `subprocess` with `start_new_session` for detached execution.
- Support for Linux window managers.

### Windows
- Future support for Windows executables and shortcuts.
- Windows-specific key mappings and execution patterns.
