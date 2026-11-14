#!/usr/bin/env python3
# Fit a comb of integer harmonics to a list of peak frequencies (MHz).
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: comb_fit.py PEAKFILE [--drop-worst] [--range LO HI]
#   --drop-worst  refit once after removing the peak with the largest residual (the dropped peak is printed)
#   --range       search range for the spacing in MHz (default 0.90 1.00)
import sys
import numpy as np
args = sys.argv[1:]
drop = "--drop-worst" in args
lo, hi = 0.9000, 1.0000
if "--range" in args:
    i = args.index("--range")
    lo, hi = float(args[i + 1]), float(args[i + 2])
air = np.array([float(l.split()[1]) for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")])
def fit(x, step):
    best = None
    for f0 in np.arange(lo, hi, step):
        rms = np.sqrt(np.mean((x - np.round(x / f0) * f0) ** 2))
        if best is None or rms < best[1]:
            best = (f0, rms)
    return best
def worst(x, f0):
    return int(np.argmax(np.abs(x - np.round(x / f0) * f0)))
def fit_rule(x, step):
    f0, rms = fit(x, step)
    if drop:
        f0, rms = fit(np.delete(x, worst(x, f0)), step)
    return f0, rms
n0 = len(air)
f0, rms = fit(air, 1e-6)
print("peaks: %d  best spacing %.5f MHz  rms residual %.1f kHz" % (len(air), f0, rms * 1e3))
if drop:
    k = worst(air, f0)
    res = (air[k] - round(air[k] / f0) * f0) * 1e3
    print("dropped worst peak %.3f MHz (residual %+.1f kHz)" % (air[k], res))
    air = np.delete(air, k)
    f0, rms = fit(air, 1e-6)
    print("after drop: peaks: %d  best spacing %.5f MHz  rms residual %.1f kHz" % (len(air), f0, rms * 1e3))
print("harmonic numbers:", [int(round(a / f0)) for a in air])
rng = np.random.default_rng(1)
ctl = [fit_rule(rng.uniform(122, 137, n0), 1e-4)[1] * 1e3 for _ in range(20)]
print("random control (20 sets, coarser search%s): median %.0f kHz, min %.0f kHz" % (", same drop rule" if drop else "", np.median(ctl), np.min(ctl)))
checks = [("FM-band hump, later captures", [97.856, 97.879, 97.870]),
          ("FM-band hump, later captures", [98.802, 98.803]),
          ("run 1 hump", [97.743]),
          ("run 1 hump", [98.695])]
for name, vals in checks:
    m = float(np.mean(vals)); n = int(round(m / f0))
    print("%s N=%d predicted %.3f measured %.3f diff %+.0f kHz" % (name, n, n * f0, m, (m - n * f0) * 1e3))
