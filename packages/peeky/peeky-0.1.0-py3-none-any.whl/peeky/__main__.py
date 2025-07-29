#!/usr/bin/env python
"""
Entry point for the Peeky module when run with python -m peeky.
"""

# Use absolute imports to avoid module path issues
from peeky.main import main

def run_main():
    """Run the main function."""
    main()

if __name__ == "__main__":
    run_main() 