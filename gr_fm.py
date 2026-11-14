#!/usr/bin/env python3
# FM demodulation of one station from an IQ capture with a GNU Radio flowgraph (file source, no dongle).
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: gr_fm.py INFILE CENTRE_HZ RATE_SPS STATION_HZ OUTFILE
import sys
import numpy as np
from gnuradio import gr, blocks, analog, filter
from gnuradio.filter import firdes
from scipy import signal

infile, out = sys.argv[1], sys.argv[5]
fc, fs, f0 = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
dec = 8
taps = firdes.low_pass(1.0, fs, 100e3, 20e3)
tb = gr.top_block()
src = blocks.file_source(gr.sizeof_gr_complex, infile, False)
xlate = filter.freq_xlating_fir_filter_ccc(dec, taps, f0 - fc, fs)
demod = analog.quadrature_demod_cf(1.0)
sink = blocks.file_sink(gr.sizeof_float, out, False)
tb.connect(src, xlate, demod, sink)
tb.run()
m = np.fromfile(out, dtype=np.float32)[200:]
f, p = signal.welch(m, fs=fs / dec, nperseg=16384)
pdb = 10 * np.log10(p + 1e-30)
pilot = pdb[(f > 18.9e3) & (f < 19.1e3)].max()
ref = np.median(pdb[((f > 16e3) & (f < 18e3)) | ((f > 20e3) & (f < 22e3))])
print("taps %d  samples out %d  %.3f MHz: 19 kHz pilot %.1f dB above nearby floor" % (len(taps), len(m), f0 / 1e6, pilot - ref))
