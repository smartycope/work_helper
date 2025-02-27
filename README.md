# Work Helper
###### Dumb name, I know

This is a TUI (*Terminal User Interface*) I made while working for Acer in order to optimize my own workflow, since my memory is absolutely garbage. It's currently under active and constant development.

There's 3 seperate entrypoints:
1. `main.py`
    * The main large program that has all the features
2. `serial_parser.py`
    * A smaller program that just parses the serial numbers, and reuses some of the functionality of the main program
3. `run_hotkeys.py`
    * A tiny script that adds some hotkey functionality for my personal setup. **Do not use**

As for running, I'm trying to get web versions up and running (using the astonishingly simple `textual-web` library) [here](https://textual-web.io/smartycope/work-helper) and [here](https://textual-web.io/smartycope/serial-parser). Currently, only SerialParser is currently functioning.

Or you can run locally. `requirements.txt` *should* be up to date, install with `python -m pip install -r requirements.txt`, then simply run `python main.py` (or whichever entrypoint). Use the `-d` flag for debug mode.

Basically, if you don't know what this is already, don't use it, you're in the wrong place.
