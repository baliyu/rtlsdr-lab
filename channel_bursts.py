#!/usr/bin/env python3
# Channel power over time from an IQ capture, and burst counting.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: channel_bursts.py INFILE CENTRE_HZ RATE_SPS THRESH_DB CH_MHZ [CH_MHZ ...]
import sys
import numpy as np

infile = sys.argv[1]
fc, fs, thr = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
chans = [float(a) for a in sys.argv[5:]]
nfft, avg, half = 1024, 3, 20
x = np.memmap(infile, dtype=np.complex64, mode="r")
nfr = len(x) // nfft
nfr -= nfr % avg
win = np.hanning(nfft).astype(np.float32)
bw = fs / nfft
idx = {c: (int(round((c * 1e6 - fc) / bw)) + np.arange(-half, half + 1)) % nfft for c in chans}
pw = {c: [] for c in chans}
step = 600
for a in range(0, nfr, step):
    b = min(a + step, nfr)
    fr = np.asarray(x[a * nfft:b * nfft]).reshape(-1, nfft) * win
    p = np.abs(np.fft.fft(fr, axis=1)) ** 2
    for c in chans:
        pw[c].append(p[:, idx[c]].sum(axis=1))
dt = avg * nfft / fs
print("capture %.1f s, block %.2f ms, window +/-%.1f kHz" % (len(x) / fs, dt * 1e3, half * bw / 1e3))
for c in chans:
    db = 10 * np.log10(np.concatenate(pw[c]).reshape(-1, avg).mean(axis=1) + 1e-30)
    med = np.median(db)
    hot = np.flatnonzero(db > med + thr)
    runs = []
    if len(hot):
        s = p0 = hot[0]
        for k in hot[1:]:
            if k - p0 > 5:
                runs.append((s, p0)); s = k
            p0 = k
        runs.append((s, p0))
    runs = [r for r in runs if r[1] - r[0] + 1 >= 10]
    print("%.3f MHz: median %.1f dB, max %.1f dB above median, bursts (>= %.0f dB for >= 100 ms): %d" % (c, med, db.max() - med, thr, len(runs)))
    for s, e in runs[:5]:
        print("   t=%.2f s, %.0f ms, peak %.1f dB above median" % (s * dt, (e - s + 1) * dt * 1e3, db[s:e + 1].max() - med))
