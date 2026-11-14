#!/bin/bash
# Airband survey: 13 captures of 1 s, centred every 1.5 MHz from 118.5 to 136.5 MHz, at 2.048 MS/s.
# Prints one line per peak: capture centre MHz, peak MHz, dB above the floor (the columns of data/air_survey_2026-11-13.txt).
# AI-assisted: drafted with Claude, run and checked by the author.
# Usage: survey_air.sh [GAIN_DB] [THRESHOLD_DB]   (defaults 40 and 10), needs the dongle attached to WSL
gain=${1:-40}
thr=${2:-10}
mkdir -p captures
echo "# Airband survey, $(date -u +%Y-%m-%d), tuner gain $gain dB, 2.048 MS/s, 1 s per capture, peaks $thr dB or more above the median floor (centre +/-10 kHz excluded)."
echo "# Columns: capture centre MHz, peak MHz, dB above floor. Written by survey_air.sh."
for c in 118.5 120.0 121.5 123.0 124.5 126.0 127.5 129.0 130.5 132.0 133.5 135.0 136.5; do
  /usr/bin/python3 capture.py ${c}e6 2.048e6 $gain 1 captures/air_$c.cfile > /tmp/survey_cap.log 2>&1
  if [ ! -s captures/air_$c.cfile ]; then echo "capture at $c MHz FAILED:" >&2; tail -2 /tmp/survey_cap.log >&2; exit 1; fi
  /usr/bin/python3 plot_spectrum.py captures/air_$c.cfile ${c}e6 2.048e6 $gain /tmp/air_$c.png $thr | grep -E "MHz .* dB above floor" | sed -E "s/^ +([0-9.]+) MHz +([0-9.]+) dB above floor/$c \1 \2/"
done
