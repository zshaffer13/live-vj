# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:40:08 2025

@author: zshaf
"""

# audio.py
import numpy as np
import pyaudio
import threading

# ---------------------------------------------------------------------
# Module‐level globals: these are what viewer.py will import.
audio_amplitude = 0.0
audio_fft_result = {
    'low':  0.0,
    'mid':  0.0,
    'high': 0.0,
}

def audio_callback(in_data, frame_count, time_info, status):
    global audio_amplitude, audio_fft_result

    # convert bytes → float32 NumPy array
    data = np.frombuffer(in_data, dtype=np.float32)

    # RMS amplitude
    audio_amplitude = float(np.sqrt(np.mean(data**2)))

    # FFT bands
    fft = np.fft.rfft(data)
    power = np.abs(fft)**2
    fs = 44100
    N  = len(data)
    bin_size = fs / N

    # band edges
    low_end  = int(250  / bin_size)
    mid_end  = int(4000 / bin_size)

    # avoid invalid slices
    avg_low  = float(np.mean(power[1:low_end]))   if low_end  > 1 else 0.0
    avg_mid  = float(np.mean(power[low_end:mid_end])) if mid_end  > low_end else 0.0
    avg_high = float(np.mean(power[mid_end:]))    if len(power) > mid_end else 0.0

    # mutate the existing dict in place
    audio_fft_result['low']  = avg_low
    audio_fft_result['mid']  = avg_mid
    audio_fft_result['high'] = avg_high

    return (in_data, pyaudio.paContinue)

def start_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
        stream_callback=audio_callback,
    )
    stream.start_stream()
    # keep alive until the program exits
    while stream.is_active():
        pass

# fire up the thread immediately on import
_thread = threading.Thread(target=start_audio_stream, daemon=True)
_thread.start()
