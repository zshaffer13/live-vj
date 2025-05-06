# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:40:35 2025

@author: zshaf
"""

import moderngl
from pathlib import Path

# Directory where shader files live
SHADER_DIR = Path(__file__).parent / "shaders"


def load_shader_source(path: str) -> str:
    """
    Read a GLSL source file, recursively expanding #include "..." directives.
    """
    file_path = SHADER_DIR / path
    text = file_path.read_text(encoding='utf-8')
    lines = text.splitlines(True)
    output = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#include'):
            # Expect format: #include "filename.glsl"
            include_name = stripped.split('"')[1]
            output.append(load_shader_source(include_name))
        else:
            output.append(line)
    return ''.join(output)


def make_program(ctx: moderngl.Context, frag_path: str) -> moderngl.Program:
    """
    Create and compile a ModernGL Program given a fragment shader path.
    Uses a fixed fullscreen-quad vertex shader and resolves includes.

    Parameters:
      ctx       - ModernGL context
      frag_path - path to the fragment shader file (relative to SHADER_DIR)
    """
    # Fullscreen-quad vertex shader (double-precision enabled)
    vertex_shader = '''#version 430 core
    #extension GL_ARB_gpu_shader_fp64 : enable
    out vec2 fragCoord;
    void main() {
        const vec2 pos[4] = vec2[](vec2(-1.0, -1.0), vec2(1.0, -1.0),
                                    vec2(-1.0,  1.0), vec2(1.0,  1.0));
        fragCoord = (pos[gl_VertexID] + 1.0) * 0.5;
        gl_Position = vec4(pos[gl_VertexID], 0.0, 1.0);
    }'''

    # Load and preprocess fragment shader source
    fragment_shader = load_shader_source(frag_path)

    # Compile program
    try:
        prog = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
    except moderngl.Error as e:
        # Print source for debugging
        print(f"Failed to compile/link shader '{frag_path}':", e)
        print("----- vertex shader -----")
        print(vertex_shader)
        print("----- fragment shader -----")
        print(fragment_shader)
        raise

    return prog

