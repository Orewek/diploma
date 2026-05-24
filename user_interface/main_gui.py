# -*- coding: utf-8 -*-
"""Main module for the app."""
import os
import sys

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import src.logger_config

from main_window import BooleanAnfApp


if __name__ == '__main__':
    app = BooleanAnfApp()
    app.mainloop()
