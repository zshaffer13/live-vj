# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:41:50 2025

@author: zshaf
"""

import moderngl_window as mglw

# pull in audio.py so the background thread and FFT machinery start running
import audio  

# you probably don’t need to import shaders.py explicitly unless it
# registers include-paths or does one-time setup
import shaders  

# GUI lives inside the viewer, so you don’t need to import gui.py here
from viewer import FractalViewer

if __name__ == "__main__":
    mglw.run_window_config(FractalViewer)