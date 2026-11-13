#!/usr/bin/env python3
# Spectrum and waterfall of a raw IQ capture (complex float32).
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: plot_spectrum.py INFILE FREQ_HZ RATE_SPS GAIN_DB OUTPNG
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

infile, out = sys.argv[1], sys.argv[5]
fc, fs, gain = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
x = np.fromfile(infile, dtype=np.complex64)
nfft = 4096
f, p = signal.welch(x, fs=fs, nperseg=nfft, return_onesided=False, detrend=False)
f = np.fft.fftshift(f) + fc
p_db = 10 * np.log10(np.fft.fftshift(p) + 1e-20)
floor = np.median(p_db)
step = fs / nfft
mask = np.abs(f - fc) > 10e3
idx, _ = signal.find_peaks(np.where(mask, p_db, floor), height=floor + 20, distance=int(100e3 / step))
print("samples:", len(x), "seconds:", round(len(x) / fs, 2))
print("median floor (dB):", round(floor, 1), "centre bin (dB):", round(p_db[nfft // 2], 1))
print("peaks 20 dB or more above floor, excluding centre +/-10 kHz:", len(idx))
for i in idx:
    print("  %.3f MHz  %.1f dB above floor" % (f[i] / 1e6, p_db[i] - floor))

fig, ax = plt.subplots(2, 1, figsize=(10, 8))
ax[0].plot(f / 1e6, p_db, lw=0.6)
ax[0].axhline(floor + 20, color="r", ls="--", lw=0.8, label="floor + 20 dB")
ax[0].set_xlabel("Frequency (MHz)")
ax[0].set_ylabel("Power (dB, uncalibrated)")
ax[0].legend()
ax[0].set_title("%.3f MHz, %.3f MS/s, tuner gain %.1f dB, %.1f s" % (fc / 1e6, fs / 1e6, gain, len(x) / fs))
fw, tw, S = signal.spectrogram(x, fs=fs, nperseg=nfft, noverlap=0, return_onesided=False, detrend=False)
S = 10 * np.log10(np.fft.fftshift(S, axes=0) + 1e-20)
ax[1].imshow(S.T, aspect="auto", origin="lower", extent=[(fc - fs / 2) / 1e6, (fc + fs / 2) / 1e6, 0, len(x) / fs])
ax[1].set_xlabel("Frequency (MHz)")
ax[1].set_ylabel("Time (s)")
fig.tight_layout()
fig.savefig(out, dpi=150)
print("saved", out)
