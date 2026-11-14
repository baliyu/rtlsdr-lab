#!/usr/bin/env python3
# Demodulate FM stations from an IQ capture and write one mono WAV per station on one shared volume scale.
# Reproduces the one-off inline WAV step described in the README.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: fm_wav.py INFILE CENTRE_HZ RATE_SPS OUTPREFIX STATION_HZ [STATION_HZ ...]
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

infile, prefix = sys.argv[1], sys.argv[4]
fc, fs = float(sys.argv[2]), float(sys.argv[3])
stations = [float(a) for a in sys.argv[5:]]
x = np.fromfile(infile, dtype=np.complex64)
n = np.arange(len(x))
taps = signal.firwin(129, 100e3, fs=fs)
lp = signal.firwin(129, 15e3, fs=fs / 8)
out = {}
for f0 in stations:
    y = signal.lfilter(taps, 1.0, x * np.exp(-2j * np.pi * (f0 - fc) * n / fs))[::8]
    m = np.angle(y[1:] * np.conj(y[:-1]))
    m = signal.lfilter(lp, 1.0, m)[::8]
    out[f0] = m - m.mean()
scale = 0.5 / max(np.abs(v).max() for v in out.values())
for f0, m in out.items():
    name = '%s_%.3f.wav' % (prefix, f0 / 1e6)
    wavfile.write(name, int(round(fs / 64)), (m * scale * 32767).astype(np.int16))
    print(name, 'rms %.4f' % np.sqrt(np.mean((m * scale) ** 2)))
