# rtlsdr-lab

RTL-SDR and GNU Radio experiments: FM first, then airband AM, then ACARS. Predictions are written before each run and scored afterwards, misses included.

AI-assisted: scripts and this README were drafted with Claude. I ran every command and checked the output.

## Setup used

- Dongle: Realtek RTL2832U, tuner Rafael Micro R820T (found by `SoapySDRUtil --find`). Probe range 24 to 1764 MHz, sample rates up to 3.2 MS/s.
- Windows 11 with WSL2 (Ubuntu), GNU Radio 3.10.12, SoapySDR RTL-SDR module. No `gr-osmosdr`, the Soapy source block is used instead.
- The dongle is passed into WSL with usbipd-win 5.3.0. Admin PowerShell, once: `usbipd bind --busid 1-1`. Normal PowerShell, each time: `usbipd attach --wsl --busid 1-1`. Check the bus ID with `usbipd list` first, other devices on the machine must stay unbound.
- Scripts run with `/usr/bin/python3` (the system one GNU Radio uses), not a venv.

## Commands

Capture 3 s of raw IQ at 98 MHz, 2.048 MS/s, tuner gain 30 dB:

    /usr/bin/python3 capture.py 98e6 2.048e6 30 3 captures/fm_98M_run1.cfile

Plot spectrum and waterfall:

    /usr/bin/python3 plot_spectrum.py captures/fm_98M_run1.cfile 98e6 2.048e6 30 figures/fm_98M_run1_spectrum.png

`captures/` is git-ignored (49 MB per 3 s capture).

## Result so far

`figures/fm_98M_run1_spectrum.png`: three broad peaks about 200 kHz wide, near 97.75, 98.69 and 98.91 MHz (read by eye from the figure). The top one has a shoulder near 98.86 MHz. A thin steady spike near 98.30 MHz, cause unknown. I have not identified any station. One `[R82XX] PLL not locked!` warning appeared during the capture, the stations were present anyway, and I have one capture only.

Known flaw: the peak counter in `plot_spectrum.py` uses a 20 dB threshold and counted only 1 peak. By eye two other stations sit about 16 to 17 dB above the floor, so the printed count is wrong. To be fixed.

## Prediction scorecard

| Prediction | Result |
| --- | --- |
| Dongle shows status OK after plug-in | Miss (it was unplugged, status Unknown) |
| Driver on interface 0 is WinUSB | Hit (Zadig had already set it) |
| `rtl_test` not on the Windows PATH | Hit |
| GNU Radio not installed | Miss (it is in WSL) |
| `osmosdr` Python module missing | Hit |
| `librtlsdr` not installed in WSL | Miss (`librtlsdr2` is installed) |
| `usbipd bind` works on a WinUSB device | Hit |
| Soapy probe fails on USB permissions | Miss (it opened fine) |
| Probe range about 24 MHz to 1.7 GHz | Hit (24 to 1764 MHz) |
| Capture file is 49,152,000 bytes | Hit |
| No overflows in the capture | Hit |
| At least 5 FM peaks at 2.048 MS/s | Miss (span is too narrow) |
| At least 2 peaks 20 dB above floor | Miss (script threshold, see above) |
| Strong spike at the centre frequency | Miss (about 3 dB) |
| Flat noise only (25% chance) | Did not happen |

Not yet tested: medium wave (needs direct sampling, which I expect to need a hardware modification), airband AM, ACARS.
