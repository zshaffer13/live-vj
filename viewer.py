# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:41:33 2025

@author: zshaf
"""

# viewer.py

import math
import random

import numpy as np
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry

from pyrr import Matrix44, Vector3
import pathlib

from audio import audio_amplitude, audio_fft_result  # your audio.py
from shaders import load_shader_source                 # your shaders.py
from gui import ControlPanel
from config import (
    FRACTAL_SHADERS,
    POPULAR_JULIA_C_VALUES,
    POPULAR_PHOENIX_VALUES,
    COLOR_SCHEMES,
    FRACTAL_LABELS,
    MESH_LABELS,
)

class FractalViewer(mglw.WindowConfig):
    gl_version    = (4, 3)
    title         = "Fractal Viewer"
    window_size   = (1280, 720)
    resizable     = True
    resource_dir  = '.'
    key_input     = True
    mouse_input   = True
    window_type   = 'glfw'
    samples       = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ——— state flags ———
        self.current_shader_key    = 'M'
        self.current_mesh          = 'Y'
        self.zoom                  = 2.5
        self.offset                = np.array([-0.5, 0.0], dtype='f8')
        self.animate               = False
        self.audioAnimate          = False
        self.rotation              = 0.0
        self.pressed_movement_keys = set()
        self.pressed_rotation_keys = set()
        self.color_scheme          = 0
        self.num_schemes           = len(COLOR_SCHEMES)
        self.enable_shadows        = True
        self.render_mode           = 'fractal'

        # 3D shader program
        shaders_dir = pathlib.Path(__file__).parent / 'shaders'
        vs = (shaders_dir / 'standard3d.vert').read_text(encoding='utf-8')
        fs = (shaders_dir / 'standard3d.frag').read_text(encoding='utf-8')
        self.mesh_prog = self.ctx.program(vertex_shader=vs, fragment_shader=fs)

        # projection and camera
        aspect = self.wnd.buffer_width / self.wnd.buffer_height
        self.proj       = Matrix44.perspective_projection(
            45.0, aspect, 0.1, 100.0, dtype='f4'
        )
        self.camera_pos = Vector3([0.0, 0.0, 3.0])

        # create exactly the meshes you'll switch by key
        self.meshes = {
            'Y': geometry.cube(size=(1.0, 1.0, 1.0)),
            'I': geometry.sphere(radius=1.0, sectors=32, rings=16),
        }

        # load initial fractal and mesh
        self._switch_fractal(self.current_shader_key)
        self._switch_mesh(self.current_mesh)

        # create GUI panel
        self.control_panel = ControlPanel(self)

    def _switch_fractal(self, key):
        """Switch to a new 2D fractal shader"""
        self.current_shader_key = key
        src = load_shader_source(FRACTAL_SHADERS[key])
        vs = """
            #version 430 core
            #extension GL_ARB_gpu_shader_fp64 : enable
            out vec2 fragCoord;
            void main() {
                const vec2 pos[4] = vec2[](vec2(-1,-1), vec2(1,-1), vec2(-1,1), vec2(1,1));
                fragCoord = (pos[gl_VertexID] + 1.0) * 0.5;
                gl_Position = vec4(pos[gl_VertexID], 0.0, 1.0);
            }
        """
        self.program = self.ctx.program(vertex_shader=vs, fragment_shader=src)
        self.vao     = self.ctx.vertex_array(self.program, [])
        self._reset_view()
        # randomize constants
        if key == 'J' and 'juliaC' in self.program:
            self.program['juliaC'].value = random.choice(POPULAR_JULIA_C_VALUES)
        if key == 'P' and 'phoenixP' in self.program:
            self.program['phoenixP'].value = random.choice(POPULAR_PHOENIX_VALUES)
        self.render_mode = 'fractal'
        print(f"Switched to fractal {key}")

    def _switch_mesh(self, mesh_key):
        """
        Instantiate the selected mesh as a VAO directly from moderngl_window.geometry
        and flip into mesh‑render mode.
        """
        self.current_mesh = mesh_key

        if mesh_key == 'Y':   # cube
            self.mesh_vao = geometry.cube(size=(1.0, 1.0, 1.0))
        elif mesh_key == 'I': # sphere
            self.mesh_vao = geometry.sphere(radius=1.0, sectors=32, rings=16)
        else:
            # unknown key: bail out
            return

        self.render_mode = 'mesh'
        print(f"Switched to mesh {mesh_key}")
        
    def _reset_view(self):
        self.zoom     = 2.5
        self.offset[:] = (-0.5, 0.0)
        self.rotation = 0.0

    def resize(self, width, height):
        super().resize(width, height)

    def on_render(self, t, frame_time):
        # pump GUI events
        try:
            self.control_panel.root.update()
        except:
            pass

        # clear screen
        self.ctx.clear()

        if self.render_mode == 'fractal':
            # set fractal uniforms
            for name, val in [
                ('zoom', self.zoom),
                ('offset', tuple(self.offset)),
                ('resolution', (self.wnd.buffer_width, self.wnd.buffer_height)),
                ('rotation', self.rotation),
                ('max_iterations', int(200 + 50 * max(math.log(self.zoom, 10), 0))),
                ('color_scheme', self.color_scheme),
                ('enable_shadows', int(self.enable_shadows)),
            ]:
                if name in self.program:
                    self.program[name].value = val
            for name in ['audio_low', 'audio_mid', 'audio_high']:
                if name in self.program:
                    self.program[name].value = (
                        audio_fft_result.get(name.split('_')[1], 0.0)
                        if self.audioAnimate else 0.0
                    )
            # smooth controls
            if self.wnd.keys.W in self.pressed_movement_keys:
                self.zoom *= pow(0.8, frame_time * 2.0)
            if self.wnd.keys.S in self.pressed_movement_keys:
                self.zoom /= pow(0.8, frame_time * 2.0)
            pan_val = 0.5 * self.zoom * frame_time
            dx = (self.wnd.keys.RIGHT in self.pressed_movement_keys) - (self.wnd.keys.LEFT in self.pressed_movement_keys)
            dy = (self.wnd.keys.UP in self.pressed_movement_keys)    - (self.wnd.keys.DOWN in self.pressed_movement_keys)
            cosR, sinR = math.cos(self.rotation), math.sin(self.rotation)
            self.offset[0] += dx * pan_val * cosR - dy * pan_val * sinR
            self.offset[1] += dx * pan_val * sinR + dy * pan_val * cosR
            if self.wnd.keys.Q in self.pressed_rotation_keys:
                self.rotation -= frame_time
            if self.wnd.keys.E in self.pressed_rotation_keys:
                self.rotation += frame_time
            if self.animate:
                self.rotation = t * 0.3 + audio_amplitude * 5.0
            # draw quad
            self.vao.render(mode=self.ctx.TRIANGLE_STRIP, vertices=4)
        else:
            # mesh mode
            self.ctx.enable(moderngl.DEPTH_TEST)
            self.ctx.clear(0.1, 0.1, 0.1, 1.0)

            # build a rotating model matrix
            view  = Matrix44.look_at(self.camera_pos,
                                     Vector3([0.0,0.0,0.0]),
                                     Vector3([0.0,1.0,0.0]),
                                     dtype='f4')
            model = Matrix44.from_y_rotation(self.rotation, dtype='f4')
            mvp   = self.proj * view * model

            # upload uniforms
            self.mesh_prog['u_MVP'].write(mvp.astype('f4').tobytes())
            self.mesh_prog['u_light_dir'].value = (0.5, 0.5, 1.0)
            self.mesh_prog['audio_low'].value   = audio_fft_result['low'] if self.audioAnimate else 0.0

            # render the VAO directly
            self.mesh_vao.render(self.mesh_prog)

            self.ctx.disable(moderngl.DEPTH_TEST)

    def _sync_gui(self):
        cp = self.control_panel
        cp.fractal_var.set(self.current_shader_key)
        cp.color_var.set(COLOR_SCHEMES[self.color_scheme])
        cp.animate_var.set(self.animate)
        cp.audioAnimate_var.set(self.audioAnimate)
        cp.enable_shadows_var.set(self.enable_shadows)
        # when mesh selected, update mesh selector
        if self.render_mode == 'mesh':
            cp.mesh_var.set(self.current_mesh)

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            c = chr(key).upper()
            # fractal keys
            if c in FRACTAL_SHADERS:
                self._switch_fractal(c)
                self._sync_gui()
                return
            # mesh keys
            if c in MESH_LABELS:
                # map 'U' -> 'cube', 'I' -> 'sphere', etc.
                mesh_key = MESH_LABELS[c]
                self._switch_mesh(mesh_key)
                self._sync_gui()
                return
            # toggles
            if c == 'A': self.animate = not self.animate;       self._sync_gui(); return
            if c == 'O': self.audioAnimate = not self.audioAnimate; self._sync_gui(); return
            if c == 'X': self.enable_shadows = not self.enable_shadows; self._sync_gui(); return
            if c == 'R': self._reset_view();                   self._sync_gui(); return
            if c == 'C':
                self.color_scheme = (self.color_scheme + 1) % self.num_schemes
                self._sync_gui(); return
        # movement/rotation keys
        if action == self.wnd.keys.ACTION_PRESS:
            if key in (self.wnd.keys.W, self.wnd.keys.S,
                       self.wnd.keys.UP, self.wnd.keys.DOWN,
                       self.wnd.keys.LEFT, self.wnd.keys.RIGHT):
                self.pressed_movement_keys.add(key)
            if key in (self.wnd.keys.Q, self.wnd.keys.E):
                self.pressed_rotation_keys.add(key)
        else:
            self.pressed_movement_keys.discard(key)
            self.pressed_rotation_keys.discard(key)

if __name__ == '__main__':
    mglw.run_window_config(FractalViewer)
