#!/usr/bin/env python3
# FM demodulate stations from an IQ capture and look for the 19 kHz stereo pilot.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: demod_fm.py INFILE CENTRE_HZ RATE_SPS GAIN_DB OUTPNG STATION_HZ [STATION_HZ ...]
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

infile, out = sys.argv[1], sys.argv[5]
fc, fs, gain = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
stations = [float(a) for a in sys.argv[6:]]
x = np.fromfile(infile, dtype=np.complex64)
n = np.arange(len(x))
dec = 8
fsd = fs / dec
taps = signal.firwin(129, 100e3, fs=fs)
fig, axs = plt.subplots(len(stations), 1, figsize=(10, 3.2 * len(stations)), squeeze=False)
for ax, f0 in zip(axs[:, 0], stations):
    y = (x * np.exp(-2j * np.pi * (f0 - fc) * n / fs)).astype(np.complex64)
    y = signal.lfilter(taps, 1.0, y)[::dec]
    mpx = np.angle(y[1:] * np.conj(y[:-1]))
    f, p = signal.welch(mpx, fs=fsd, nperseg=16384)
    pdb = 10 * np.log10(p + 1e-30)
    pilot = pdb[(f > 18.9e3) & (f < 19.1e3)].max()
    ref = np.median(pdb[((f > 16e3) & (f < 18e3)) | ((f > 20e3) & (f < 22e3))])
    print("%.3f MHz: 19 kHz pilot %.1f dB above nearby floor" % (f0 / 1e6, pilot - ref))
    m = f < 60e3
    ax.plot(f[m] / 1e3, pdb[m], lw=0.7)
    ax.axvline(19, color="r", ls="--", lw=0.8, label="19 kHz")
    ax.set_title("%.3f MHz, demodulated, pilot %.1f dB above floor" % (f0 / 1e6, pilot - ref), fontsize=10)
    ax.set_xlabel("Frequency (kHz)")
    ax.set_ylabel("Power (dB, uncalibrated)")
    ax.legend()
fig.suptitle("Capture: %.3f MHz, %.3f MS/s, tuner gain %.1f dB" % (fc / 1e6, fs / 1e6, gain), fontsize=10)
fig.tight_layout()
fig.savefig(out, dpi=150)
print("saved", out)
