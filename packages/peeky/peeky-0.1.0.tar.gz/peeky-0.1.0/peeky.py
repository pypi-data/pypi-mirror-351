#!/usr/bin/env python
"""
Simple entry point script for Peeky.

This script is the main entry point for the peeky command.
For Linux/Mac users, make this file executable with:
    chmod +x peeky.py
Then run with:
    ./peeky.py command
"""

import sys
import os

# Add the script's directory to the Python path if it's not already there
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from peeky.main import main

if __name__ == "__main__":
    main() 