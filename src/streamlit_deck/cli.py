import sys
import os
from streamlit.web import cli as stcli


def run():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "main.py")

    # Construct the command for streamlit
    # We set argv as if we called "streamlit run file.py"
    sys.argv = [
        "streamlit",
        "run",
        filename,
        "--theme.base=dark",
        "--theme.primaryColor=#ff0000",
        "--theme.backgroundColor=#000000",
        "--theme.secondaryBackgroundColor=#111111",
        "--theme.textColor=#ffffff",
        "--theme.borderColor=#333333",
        "--theme.font='IBM Plex Mono':https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap",
    ]

    sys.exit(stcli.main())
