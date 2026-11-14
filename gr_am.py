#!/usr/bin/env python3
# AM demodulation check: synthetic AM IQ file, GNU Radio envelope detector, measure depth, tone and harmonic.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: gr_am.py DEPTH TONE_HZ OFFSET_HZ
import sys
import numpy as np
from gnuradio import gr, blocks, filter
from gnuradio.filter import firdes
from scipy import signal

m_in, tone, off = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
fs, secs, dec = 0.3e6, 3, 10
rng = np.random.default_rng(1)
n = np.arange(int(fs * secs))
a = 0.5 * (1 + m_in * np.cos(2 * np.pi * tone * n / fs))
noise = 0.005 * (rng.standard_normal(len(n)) + 1j * rng.standard_normal(len(n))) / np.sqrt(2)
x = (a * np.exp(2j * np.pi * off * n / fs) + noise).astype(np.complex64)
fin, fout = "captures/am_synth.cfile", "captures/am_synth_demod.f32"
x.tofile(fin)
taps = firdes.low_pass(1.0, fs, 5e3, 2e3)
tb = gr.top_block()
src = blocks.file_source(gr.sizeof_gr_complex, fin, False)
xlate = filter.freq_xlating_fir_filter_ccc(dec, taps, off, fs)
mag = blocks.complex_to_mag(1)
sink = blocks.file_sink(gr.sizeof_float, fout, False)
tb.connect(src, xlate, mag, sink)
tb.run()
y = np.fromfile(fout, dtype=np.float32)[500:]
fsd = fs / dec
t = np.arange(len(y)) / fsd
dc = y.mean()
def amp(f):
    return 2 * abs(np.mean((y - dc) * np.exp(-2j * np.pi * f * t)))
h1, h2 = amp(tone), amp(2 * tone)
f, p = signal.welch(y - dc, fs=fsd, nperseg=32768)
print("input depth %.2f  recovered depth %.3f  tone peak %.1f Hz  2nd harmonic %.1f dB below the tone  samples %d" % (m_in, h1 / dc, f[np.argmax(p)], 20 * np.log10(h1 / (h2 + 1e-12)), len(y)))
