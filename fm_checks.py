#!/usr/bin/env python3
# Envelope spread, power and frequency spread of FM-band stations in an IQ capture.
# Reproduces the one-off inline checks described in the README.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: fm_checks.py INFILE CENTRE_HZ RATE_SPS REF_HZ STATION_HZ [STATION_HZ ...]
import sys
import numpy as np
from scipy import signal

infile = sys.argv[1]
fc, fs, ref = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
stations = [float(a) for a in sys.argv[5:]]
x = np.fromfile(infile, dtype=np.complex64)
n = np.arange(len(x))
taps = signal.firwin(129, 100e3, fs=fs)
fsd = fs / 8
rows = []
for f0 in [ref] + stations:
    y = signal.lfilter(taps, 1.0, x * np.exp(-2j * np.pi * (f0 - fc) * n / fs))[::8][200:]
    a = np.abs(y)
    d = np.angle(y[1:] * np.conj(y[:-1])) * fsd / (2 * np.pi)
    rows.append((f0, a.std() / a.mean(), 10 * np.log10(np.mean(a ** 2)), d.mean() / 1e3, d.std() / 1e3))
ref_db = rows[0][2]
for f0, sp, pw, off, sd in rows:
    print("%.3f MHz  envelope spread %.2f  power %+.1f dB vs reference  frequency offset %+.1f kHz  frequency std %.1f kHz" % (f0 / 1e6, sp, pw - ref_db, off, sd))
