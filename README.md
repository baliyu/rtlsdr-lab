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

`figures/fm_98M_run1_spectrum.png`: three broad peaks about 200 kHz wide, near 97.75, 98.69 and 98.91 MHz (read by eye from the figure). The top one has a shoulder near 98.86 MHz. A thin steady spike near 98.30 MHz, cause unknown. Only the peak near 98.9 MHz was later confirmed as a station, see the section on later captures. One `[R82XX] PLL not locked!` warning appeared during the capture, the stations were present anyway, and I have one capture only.

Peak counter fixed: `plot_spectrum.py` now takes the threshold as an optional sixth argument (default 10 dB) and prints and plots the value used. At 10 dB it lists 4 peaks: 97.743, 98.300, 98.695 and 98.908 MHz (17.1, 16.5, 16.3 and 20.8 dB above the floor). Three are broad, and later captures confirm only the one near 98.9 MHz as a station. The 98.300 MHz one is the thin spike, which I count as a peak but not as a station. The 10 dB value was chosen after seeing the first figure, so it is not a tested threshold.

## Later captures at 98 MHz (same setup, antenna on unless stated)

Run 2 repeated run 1 and the four peaks came back with heights within 1.1 dB of run 1. Some things are established and one is not.

Established:

- 98.9 MHz is a stereo FM broadcast station. Demodulated, it shows audio up to a sharp cutoff at 15 kHz, a 19 kHz pilot tone 29.0 dB above the nearby floor (29.7 dB with the filter centred on 98.900 MHz) and a stereo band around 38 kHz (`figures/fm_98M_run1_pilot.png`, `figures/fm_98M_run1_pilot_grid.png`). I listened to 3 s WAV files for 97.743, 98.695 and 98.908 MHz: one had music and two had nothing audible. I did not record which file had the music. I assumed it was 98.908, which is the loudest (RMS 0.158 against 0.092 and 0.093).
- The 98.30 MHz spike and the two broad peaks disappear with the antenna removed (`figures/fm_98M_noant_spectrum.png`), so they come in through the antenna. The small spike at exactly 98.000 MHz stays, so it is internal to the dongle.
- The 98.9 MHz station, the 98.30 MHz spike and the first broad peak fall by about 12 dB and then about 8 dB when the tuner gain goes from 30 to 20 to 10 dB (levels read by eye from the figures, about 0.5 dB). I expected tuner overload to fall much faster than that, which is from memory and not checked. So overload is ruled out for those three signals. The second broad peak was not read this way.

Not explained:

- The two broad peaks, about 200 kHz wide and about 0.95 MHz apart. In run 1 they sat near 97.74 and 98.70 MHz. In run 2, the gain 20 and gain 10 captures and the battery capture they sat at 97.86 to 97.88 and 98.80 to 98.82 MHz, with the same spacing. The 98.9 MHz station and the 98.30 MHz spike did not move. In the run 1 data their envelope is nearly constant (spread 0.19 and 0.23, against 0.55 for noise) and their frequency spread is about 26 kHz, but demodulating them gives no audible audio and no 19 kHz pilot. I do not know what they are, or why run 1 differs from the later captures. A capture on battery power, with the charger unplugged, did not change them, so the charger is not supported as the source.

The envelope, frequency-spread and WAV checks were one-off inline commands and are not saved in this repo, so those numbers cannot be reproduced from here. `demod_fm.py` is saved:

    /usr/bin/python3 demod_fm.py captures/fm_98M_run1.cfile 98e6 2.048e6 30 figures/fm_98M_run1_pilot.png 97.743e6 98.695e6 98.908e6

Other figures: `figures/fm_98M_run2_spectrum.png`, `figures/fm_98M_g20_spectrum.png`, `figures/fm_98M_g10_spectrum.png`, `figures/fm_98M_battery_spectrum.png`.

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
| 4 peaks at a 10 dB threshold, at 97.75, 98.30, 98.69 and 98.91 MHz | Hit (17.1, 16.5, 16.3 and 20.8 dB above the floor) |
| The 98.86 MHz shoulder is not listed as its own peak | Hit |
| 98.908 MHz has a 19 kHz pilot at least 15 dB above its floor | Hit (29.0 dB) |
| All three stations show a pilot of at least 10 dB | Miss (97.743: 1.0 dB, 98.695: 0.9 dB) |
| 98.908 gives clear speech or music | Hit, assuming it was the music file (see above) |
| 98.908 stereo band is a flat plateau from 23 to 53 kHz | Miss (concentrated at 35 to 41 kHz) |
| The floor on the two quiet bands rises with frequency | Miss (it is flat) |
| Noise-only band has envelope spread near 0.52 | Hit (0.55) |
| 98.908 has envelope spread below 0.25 and is 15 dB above the noise band | Miss (0.31 and 14.9 dB) |
| The two quiet bands have spread below 0.35 and sit 8 to 14 dB above the noise band | Hit (0.19 and 0.23, 11.4 and 10.7 dB) |
| At least one of the two quiet bands has audible audio | Miss (nothing audible in two of the three files) |
| The low to high band power ratio separates the music file from the others | Miss (5.1 dB against 5.9 dB) |
| Frequency spread above 30 kHz for the noise-only band, 15 to 40 kHz for 98.908 | Hit (61.0 and 30.0 kHz) |
| 97.743 shows a mean offset more than 25 kHz from zero | Miss (-1.8 kHz) |
| With the antenna off, 98.908 drops at least 15 dB | Hit (no peak above the new threshold, so at least 18.5 dB) |
| With the antenna off, the two broad peaks and the 98.30 spike stay within 5 dB | Miss (all dropped at least 14 dB) |
| Run 2 shows the same four peaks at the same frequencies, heights within 3 dB | Partly (heights within 1.1 dB, but the two broad peaks moved about 110 kHz) |
| 98.900 MHz pilot at least 25 dB, and one of 97.800 and 98.800 reaches 10 dB | Hit (29.7 dB, and 10.5 dB at 98.800, which I do not trust because the 98.900 station leaks into that filter) |
| 98.90 MHz station stays listed at gain 20 and 10 | Hit (16.7 and 11.0 dB) |
| 98.30 MHz spike stays listed at gain 20 | Hit (10.1 dB, only just) |
| Both broad peaks stay listed at gain 20 | Partly (97.879 listed at 13.0 dB, the other hump was not, because the script keeps one peak per 100 kHz) |
| On battery power, 98.90 and 98.30 stay within 3 dB of run 2 | Partly (spike 2.2 dB lower, station 5.2 dB lower) |
| On battery power, a broad peak moves 30 kHz or changes 5 dB | Miss (moved 14 and 1 kHz, changed 1.0 and 4.2 dB) |

Not yet tested: medium wave (needs direct sampling, which I expect to need a hardware modification), airband AM, ACARS.
