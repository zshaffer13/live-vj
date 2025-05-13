# -*- coding: utf-8 -*-
"""
Created on Thu May  1 11:29:36 2025

@author: zshaf
"""

# config.py

# Popular constants
POPULAR_JULIA_C_VALUES = [
    (-0.8, 0.156),
    (0.285, 0.01),
    (-0.70176, -0.3842),
    (-0.8, 0.2),
    (-0.7269, 0.1889),
]

POPULAR_PHOENIX_VALUES = [-0.5, -0.7, -0.8, -0.4, -0.6]

# Fractal → shader-path mappings
FRACTAL_SHADERS = {
    'M': 'mandelbrot_clean.frag',
    'J': 'julia.frag',
    'B': 'burning_ship.frag',
    'P': 'phoenix.frag',
    'D': 'buddhabrot.frag',
    'T': 'tunnel.frag',
    'U': 'mandelbulb.frag',
    'S': 'sphere_grid.frag',
    'K': 'kaleido.frag',
    #'V': 'volumetric_raymarch.frag',
}

# For your Tk radio buttons
FRACTAL_LABELS = {
    'M': 'Mandelbrot (M)',
    'J': 'Julia (J)',
    'B': 'Burning Ship (B)',
    'P': 'Phoenix (P)',
    'D': 'Buddhabrot (D)',
    'T': '3D Tunnel (T)',
    'U': 'Mandelbulb 3D (U)',
    'S': 'Sphere Grid (S)',
    'K': 'Kaleido Tunnel (K)',
    #'V': 'Volumetric SDF (V)',
}

#For Tk radio buttons
MESH_LABELS = {
    'Y': 'Cube (Y)',
    'I': 'Sphere (I)',
}

# Your color-scheme list
COLOR_SCHEMES = [
    "HSV",
    "Grayscale",
    "Pastel",
    "Thermal",
    "Neon Pulse",
    "Rainbow Bands",
    "Gold",
    "Duotone",
]
