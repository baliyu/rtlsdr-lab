#!/usr/bin/env python3
# Capture raw IQ (complex float32) from an RTL-SDR with GNU Radio's Soapy source.
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: capture.py FREQ_HZ RATE_SPS GAIN_DB SECONDS OUTFILE
import sys
from gnuradio import gr, blocks, soapy

def main():
    freq, rate, gain, secs = (float(x) for x in sys.argv[1:5])
    out = sys.argv[5]
    tb = gr.top_block()
    src = soapy.source("driver=rtlsdr", "fc32", 1, "", "", [""], [""])
    src.set_sample_rate(0, rate)
    src.set_frequency(0, freq)
    src.set_gain_mode(0, False)
    src.set_gain(0, "TUNER", gain)
    head = blocks.head(gr.sizeof_gr_complex, int(rate * secs))
    sink = blocks.file_sink(gr.sizeof_gr_complex, out, False)
    tb.connect(src, head, sink)
    tb.run()

main()
