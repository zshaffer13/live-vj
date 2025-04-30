import moderngl
import moderngl_window as mglw

import numpy as np
import pyaudio
import threading
import random
import math
import tkinter as tk
from tkinter import ttk

# Global audio data
audio_amplitude = 0.0
audio_fft_result = {'low': 0.0, 'mid': 0.0, 'high': 0.0}

# Audio callback: fill amplitude and FFT bands
def audio_callback(in_data, frame_count, time_info, status):
    global audio_amplitude, audio_fft_result
    data = np.frombuffer(in_data, dtype=np.float32)
    audio_amplitude = np.sqrt(np.mean(data**2))
    fft = np.fft.rfft(data)
    power = np.abs(fft)**2
    fs = 44100
    N = len(data)
    bin_size = fs / N
    low_end = int(250 / bin_size)
    mid_end = int(4000 / bin_size)
    avg_low = np.mean(power[1:low_end]) if low_end > 1 else 0.0
    avg_mid = np.mean(power[low_end:mid_end]) if mid_end > low_end else 0.0
    avg_high = np.mean(power[mid_end:]) if len(power) > mid_end else 0.0
    audio_fft_result = {'low': avg_low, 'mid': avg_mid, 'high': avg_high}
    return in_data, pyaudio.paContinue

# Start audio stream in background thread
def start_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024,
                    stream_callback=audio_callback)
    stream.start_stream()
    while stream.is_active():
        pass

audio_thread = threading.Thread(target=start_audio_stream, daemon=True)
audio_thread.start()

# Popular constant values
POPULAR_JULIA_C_VALUES = [
    (-0.8, 0.156), (0.285, 0.01), (-0.70176, -0.3842),
    (-0.8, 0.2), (-0.7269, 0.1889)
]
POPULAR_PHOENIX_VALUES = [-0.5, -0.7, -0.8, -0.4, -0.6]

# Map keys to fractal shaders
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
}

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
}

class ControlPanel:
    def __init__(self, viewer):
        self.viewer = viewer
        self.root = tk.Tk()
        self.root.title("Fractal Controls")
        # Fractal type selector
        ttk.Label(self.root, text="Fractal Type:").pack(anchor='w', padx=10, pady=(10,0))
        self.fractal_var = tk.StringVar(value=viewer.current_shader_key)
        for key, label in FRACTAL_LABELS.items():
            ttk.Radiobutton(
                self.root, text=label,
                variable=self.fractal_var, value=key,
                command=self.on_fractal_change
            ).pack(anchor='w', padx=20)
        # Color scheme combobox
        ttk.Label(self.root, text="Color Scheme:").pack(anchor='w', padx=10, pady=(10,0))
        self.color_names = ["HSV","Grayscale","Pastel","Thermal",
                            "Neon Pulse","Rainbow Bands","Gold","Duotone"]
        self.color_var = tk.StringVar(value=self.color_names[viewer.color_scheme])
        combo = ttk.Combobox(self.root, values=self.color_names,
                             textvariable=self.color_var, state='readonly')
        combo.pack(fill='x', padx=20)
        combo.bind('<<ComboboxSelected>>', self.on_color_change)
        # Toggles
        self.animate_var = tk.BooleanVar(value=viewer.animate)
        ttk.Checkbutton(
            self.root, text="Animate (A)", variable=self.animate_var,
            command=lambda: setattr(viewer, 'animate', self.animate_var.get())
        ).pack(anchor='w', padx=10, pady=(10,0))
        self.audio_var = tk.BooleanVar(value=viewer.audioAnimate)
        ttk.Checkbutton(
            self.root, text="Audio Anim (O)", variable=self.audio_var,
            command=lambda: setattr(viewer, 'audioAnimate', self.audio_var.get())
        ).pack(anchor='w', padx=10)
        self.shadows_var = tk.BooleanVar(value=viewer.enable_shadows)
        ttk.Checkbutton(
            self.root, text="Shadows (X)", variable=self.shadows_var,
            command=lambda: setattr(viewer, 'enable_shadows', self.shadows_var.get())
        ).pack(anchor='w', padx=10)
        # Reset & screenshot
        ttk.Button(self.root, text="Reset View (R)",
                   command=viewer._reset_view).pack(fill='x', padx=10, pady=(20,5))

    def on_fractal_change(self):
        key = self.fractal_var.get()
        self.viewer._switch_fractal(key)
        self.viewer._sync_gui()

    def on_color_change(self, event):
        idx = self.color_names.index(self.color_var.get())
        self.viewer.color_scheme = idx
        self.viewer._sync_gui()

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
        # — state flags —
        self.current_shader_key   = 'M'
        self.zoom                 = 2.5
        self.offset               = np.array([-0.5, 0.0], dtype='f8')
        self.animate              = False
        self.audioAnimate         = False
        self.rotation             = 0.0
        self.pressed_movement_keys= set()
        self.pressed_rotation_keys= set()
        self.color_scheme         = 0
        self.num_schemes          = 8
        self.enable_shadows       = True

        # load initial fractal + VAO
        self._switch_fractal(self.current_shader_key)
        # create TK control panel
        self.control_panel = ControlPanel(self)
        
    def _switch_fractal(self, key):
        self.current_shader_key = key
        frag_file = FRACTAL_SHADERS[key]
        self.load_shader(frag_file)
        self.vao = self.ctx.vertex_array(self.program, [])
        self._reset_view()
        if key == 'J' and 'juliaC' in self.program:
            c = random.choice(POPULAR_JULIA_C_VALUES)
            self.program['juliaC'].value = c
        if key == 'P' and 'phoenixP' in self.program:
            p = random.choice(POPULAR_PHOENIX_VALUES)
            self.program['phoenixP'].value = p
        print(f"Switched to {key}")

    def resize(self, width, height):
        # called by moderngl_window on window resize
        super().resize(width, height)
        self._alloc_feedback_buffers(width, height)

    def _reset_view(self):
        self.zoom     = 2.5
        self.offset   = np.array([-0.5, 0.0], dtype='f8')
        self.rotation = 0.0

    def load_shader(self, shader_filename):
        src = self.load_shader_source(shader_filename)
        vs = """
            #version 430 core
            #extension GL_ARB_gpu_shader_fp64 : enable
            out vec2 fragCoord;
            void main() {
                const vec2 pos[4] = vec2[](vec2(-1,-1),vec2(1,-1),vec2(-1,1),vec2(1,1));
                fragCoord = (pos[gl_VertexID] + 1.0) * 0.5;
                gl_Position = vec4(pos[gl_VertexID],0.0,1.0);
            }
        """
        try:
            self.program = self.ctx.program(vertex_shader=vs, fragment_shader=src)
        except moderngl.Error as e:
            print(f"Shader compilation failed for {shader_filename}: {e}")
            raise

    def load_shader_source(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        out = []
        for line in lines:
            if line.strip().startswith('#include'):
                inc = line.split('"')[1]
                out += open(inc, 'r', encoding='utf-8').read().splitlines(True)
            else:
                out.append(line)
        return ''.join(out)

    def _sync_gui(self):
        cp = self.control_panel
        cp.fractal_var.set(self.current_shader_key)
        cp.animate_var.set(self.animate)
        cp.audio_var.set(self.audioAnimate)
        cp.shadows_var.set(self.enable_shadows)
        cp.color_var.set(cp.color_names[self.color_scheme])

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            c = chr(key).upper()
            if c in FRACTAL_SHADERS:
                self._switch_fractal(c)
                self._sync_gui()
                return
            if c == 'A':
                self.animate = not self.animate
                self._sync_gui()
                return
            if c == 'O':
                self.audioAnimate = not self.audioAnimate
                self._sync_gui()
                return
            if c == 'X':
                self.enable_shadows = not self.enable_shadows
                self._sync_gui()
                return
            if c == 'R':
                self._reset_view()
                self._sync_gui()
                return
            if c == 'C':
                self.color_scheme = (self.color_scheme + 1) % self.num_schemes
                self._sync_gui()
                print(f"Color scheme → {self.color_scheme}")
                return

        # movement & rotation key‐state handling (unchanged)…
        move_keys = {self.wnd.keys.W,self.wnd.keys.S,
                     self.wnd.keys.UP,self.wnd.keys.DOWN,
                     self.wnd.keys.LEFT,self.wnd.keys.RIGHT}
        if action == self.wnd.keys.ACTION_PRESS and key in move_keys:
            self.pressed_movement_keys.add(key)
        elif action == self.wnd.keys.ACTION_RELEASE and key in move_keys:
            self.pressed_movement_keys.discard(key)
        rot_keys = {self.wnd.keys.Q, self.wnd.keys.E}
        if action == self.wnd.keys.ACTION_PRESS and key in rot_keys:
            self.pressed_rotation_keys.add(key)
        elif action == self.wnd.keys.ACTION_RELEASE and key in rot_keys:
            self.pressed_rotation_keys.discard(key)

    def on_render(self, t, frame_time):
        # — 1) Pump TK events —
        try:
            self.control_panel.root.update()
        except tk.TclError:
            pass

        # — 3) Clear and upload all uniforms —
        self.ctx.clear()
        if 'zoom' in self.program:
            self.program['zoom'].value = self.zoom
        if 'offset' in self.program:
            self.program['offset'].value = tuple(self.offset)
        if 'resolution' in self.program:
            self.program['resolution'].value = (
                self.wnd.buffer_width,
                self.wnd.buffer_height
            )
        if 'rotation' in self.program:
            self.program['rotation'].value = self.rotation
        if 'max_iterations' in self.program:
            extra = 50 * max(math.log(self.zoom, 10), 0)
            self.program['max_iterations'].value = int(200 + extra)
        if 'color_scheme' in self.program:
            self.program['color_scheme'].value = self.color_scheme
        if 'enable_shadows' in self.program:
            self.program['enable_shadows'].value = int(self.enable_shadows)
        if 'audio_low' in self.program:
            self.program['audio_low'].value = (
                audio_fft_result['low'] if self.audioAnimate else 0.0
            )
        if 'audio_mid' in self.program:
            self.program['audio_mid'].value = (
                audio_fft_result['mid'] if self.audioAnimate else 0.0
            )
        if 'audio_high' in self.program:
            self.program['audio_high'].value = (
                audio_fft_result['high'] if self.audioAnimate else 0.0
            )

        # — 4) Update pan/zoom/rotation keys (unchanged) —
        move_speed, pan_speed = 2.0, 0.5
        if self.wnd.keys.W in self.pressed_movement_keys:
            self.zoom *= pow(0.8, frame_time * move_speed)
        if self.wnd.keys.S in self.pressed_movement_keys:
            self.zoom /= pow(0.8, frame_time * move_speed)
        pan_val = pan_speed * self.zoom * frame_time
        dx = ((self.wnd.keys.RIGHT in self.pressed_movement_keys) -
              (self.wnd.keys.LEFT  in self.pressed_movement_keys)) * pan_val
        dy = ((self.wnd.keys.UP    in self.pressed_movement_keys) -
              (self.wnd.keys.DOWN  in self.pressed_movement_keys)) * pan_val
        cosR, sinR = math.cos(self.rotation), math.sin(self.rotation)
        self.offset[0] += dx * cosR - dy * sinR
        self.offset[1] += dx * sinR + dy * cosR
        rot_speed = 1.0
        if self.wnd.keys.Q in self.pressed_rotation_keys:
            self.rotation -= rot_speed * frame_time
        if self.wnd.keys.E in self.pressed_rotation_keys:
            self.rotation += rot_speed * frame_time
        if self.animate:
            self.rotation = t * 0.3 + audio_amplitude * 5.0

        # — 5) Draw the fractal into whatever target we bound above —
        self.vao.render(mode=self.ctx.TRIANGLE_STRIP, vertices=4)



if __name__ == '__main__':
    mglw.run_window_config(FractalViewer)
