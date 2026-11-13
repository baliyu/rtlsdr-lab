#!/usr/bin/env python3
# Fit a comb of integer harmonics to a list of peak frequencies (MHz).
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: comb_fit.py PEAKFILE
import sys
import numpy as np
air = np.array([float(l.split()[1]) for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")])
def fit(x, step):
    best = None
    for f0 in np.arange(0.9000, 1.0000, step):
        rms = np.sqrt(np.mean((x - np.round(x / f0) * f0) ** 2))
        if best is None or rms < best[1]:
            best = (f0, rms)
    return best
f0, rms = fit(air, 1e-6)
print("peaks: %d  best spacing %.5f MHz  rms residual %.1f kHz" % (len(air), f0, rms * 1e3))
print("harmonic numbers:", [int(round(a / f0)) for a in air])
rng = np.random.default_rng(1)
ctl = [fit(rng.uniform(122, 137, len(air)), 1e-4)[1] * 1e3 for _ in range(20)]
print("random control (20 sets, coarser search): median %.0f kHz, min %.0f kHz" % (np.median(ctl), np.min(ctl)))
checks = [("FM-band hump, later captures", [97.856, 97.879, 97.870]),
          ("FM-band hump, later captures", [98.802, 98.803]),
          ("run 1 hump", [97.743]),
          ("run 1 hump", [98.695])]
for name, vals in checks:
    m = float(np.mean(vals)); n = int(round(m / f0))
    print("%s N=%d predicted %.3f measured %.3f diff %+.0f kHz" % (name, n, n * f0, m, (m - n * f0) * 1e3))
