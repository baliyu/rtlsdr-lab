#!/usr/bin/env python3
# Distance of each airband peak from a fitted harmonic comb, 13 and 14 Nov surveys.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: comb_plot.py OUT.png   (run from the repo root; spacing searched over 0.94 to 0.96 MHz)
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(p):
    return np.array([float(l.split()[1]) for l in open(p) if l.strip() and not l.startswith("#")])

def fit(x, step=1e-6, lo=0.94, hi=0.96):
    best = None
    for f0 in np.arange(lo, hi, step):
        rms = np.sqrt(np.mean((x - np.round(x / f0) * f0) ** 2))
        if best is None or rms < best[1]:
            best = (f0, rms)
    return best

def resid(x, f0):
    return (x - np.round(x / f0) * f0) * 1e3

sets = [("13 Nov", "data/air_survey_2026-11-13.txt", "o", "tab:blue", False),
        ("14 Nov", "data/air_survey_2026-11-14.txt", "s", "tab:orange", True)]
fig, ax = plt.subplots(figsize=(8, 4.5))
for label, path, mk, col, drop in sets:
    x = load(path)
    f0, rms = fit(x)
    k = None
    if drop:
        k = int(np.argmax(np.abs(resid(x, f0))))
        f0, rms = fit(np.delete(x, k))
    r = resid(x, f0)
    keep = np.ones(len(x), bool)
    if k is not None:
        keep[k] = False
    ax.scatter(x[keep], r[keep], marker=mk, color=col,
               label="%s: %d peaks, spacing %.5f MHz, rms %.1f kHz" % (label, keep.sum(), f0, rms * 1e3))
    print("%s: kept %d of %d, spacing %.5f MHz, rms %.1f kHz" % (label, keep.sum(), len(x), f0, rms * 1e3))
    if k is not None:
        ax.scatter(x[k], r[k], marker="x", color="red", s=80, label="dropped: %.3f MHz, %+.1f kHz" % (x[k], r[k]))
        print("dropped %.3f MHz, residual %+.1f kHz (against the refit spacing)" % (x[k], r[k]))
ax.axhline(0, color="grey", lw=0.8)
ax.set_xlabel("Peak frequency (MHz)")
ax.set_ylabel("Distance from nearest comb line (kHz)")
ax.set_title("Airband peaks against a fitted comb of harmonics")
ax.legend(fontsize=8, loc="center right")
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=150)
print("saved", sys.argv[1])
