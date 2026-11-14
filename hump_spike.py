#!/usr/bin/env python3
# Height of a broad hump and a thin spike in a narrow IQ capture centred at 129.525 MHz, from a Welch spectrum.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: hump_spike.py INFILE CENTRE_HZ RATE_SPS
import sys
import numpy as np
from scipy import signal

x = np.fromfile(sys.argv[1], dtype=np.complex64)
fc, fs = float(sys.argv[2]), float(sys.argv[3])
f, p = signal.welch(x, fs=fs, nperseg=4096, return_onesided=False, detrend=False)
f = (np.fft.fftshift(f) + fc) / 1e6
db = 10 * np.log10(np.fft.fftshift(p) + 1e-20)
def med(lo, hi):
    return np.median(db[(f >= lo) & (f <= hi)])
ref = (med(129.385, 129.415) + med(129.645, 129.670)) / 2
hump = med(129.565, 129.615) - ref
loc = np.median(np.concatenate([db[(f >= 129.590) & (f < 129.5990)], db[(f > 129.6010) & (f <= 129.610)]]))
spike = db[(f >= 129.5995) & (f <= 129.6005)].max() - loc
print("%s  hump %.1f dB above the span edges  spike %.1f dB above its neighbours  edge level %.1f dB" % (sys.argv[1].split('/')[-1], hump, spike, ref))
