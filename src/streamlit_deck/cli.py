import sys
import os
from streamlit.web import cli as stcli


def run():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "main.py")

    # Construct the command for streamlit
    # We set argv as if we called "streamlit run file.py"
    sys.argv = ["streamlit", "run", filename]

    sys.exit(stcli.main())
