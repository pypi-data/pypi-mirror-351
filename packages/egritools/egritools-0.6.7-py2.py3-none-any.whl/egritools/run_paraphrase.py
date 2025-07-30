"""
Launcher file to launch paraphrase app

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import os
import subprocess

def main():
    app_path = os.path.join(os.path.dirname(__file__), 'paraphrase.py')
    subprocess.run(['streamlit', 'run', app_path])

if __name__ == "__main__":
    main()