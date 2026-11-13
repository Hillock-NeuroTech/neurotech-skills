# Front-end chips, design tools and layout

Chip figures taken from the manufacturers' datasheets downloaded on 13
November 2026 (TI ADS1299 datasheet; Intan RHD2000 series datasheet).
Use the datasheet revision you build with: values and test conditions
change between revisions.

## Reference chips

| | TI ADS1299 (-4, -6, 8-channel) | Intan RHD2000 series (RHD2132, RHD2164, RHD2216) |
|---|---|---|
| Class | EEG, ECG, EMG biopotentials | extracellular spikes and LFP |
| Resolution | 24-bit delta-sigma, simultaneous sampling | 16-bit SAR, multiplexed |
| Data rate | 250 SPS to 16 kSPS | up to 1.05 MS/s aggregate (32 channels at 30 kS/s) |
| Input-referred noise | 1 µVpp in a 70 Hz band (input shorted; datasheet note: not production tested) | 2.4 µVrms typical (varies < 15% with bandwidth) |
| Gain / bandwidth | PGA 1, 2, 4, 6, 8, 12 or 24; input range ±VREF/gain | fixed-gain amplifiers; upper cutoff 100 Hz-20 kHz and lower cutoff 0.1-500 Hz set by registers; DSP high-pass 0.02 Hz-1 kHz for offset removal |
| Input impedance / bias | 1000 MΩ DC (500 MΩ with 6 nA current-source lead-off); bias current ±300 pA | see datasheet; AC-coupled amplifier inputs |
| CMRR | -110 dB | see datasheet |
| Power | 39 mW typical, 42 max for 8 channels at 5 V analog (about 5 mW per channel) | see datasheet for your sampling rate |
| Built in | bias (right-leg) drive amplifier, lead-off detection, test signals | in situ electrode impedance measurement |
| Seen in | OpenBCI Cyton (8 ch, gain 24 by default), many research EEG boards | Intan and Open Ephys acquisition boards, many headstages |

Stimulation-capable variant: Intan RHS2000 (recording plus constant-current
stimulation per channel, with amplifier fast settle after pulses).

## Configuring an ADS1299 (orientation)

Configuration is by SPI registers: `CONFIG1` (data rate), `CONFIG2`
(test signals), `CONFIG3` (reference buffer and bias), `CHnSET` per channel
(power-down, gain, input mux), `BIAS_SENSP`/`BIAS_SENSN` (which channels
feed the bias drive), `LOFF*` (lead-off). Read every register back after
writing. Typical EEG: 250-500 SPS, gain 24, SRB1 common reference, bias
drive enabled from all EEG channels. Check the noise floor with inputs
shorted (`CHnSET` mux to input-short) before any electrode is attached.

## Design and simulation tools

| Tool | Use |
|---|---|
| KiCad (with ngspice) | schematic, PCB layout, SPICE simulation; free |
| Altium Designer | commercial PCB design |
| LTspice | free SPICE from Analog Devices; fast for amplifier, filter and noise simulation |
| TINA-TI, PSpice for TI | TI's simulators with vendor models |
| Python (`scripts/noise_budget.py`) | input-referred noise budget by source |

Simulate: input network (protection resistors, RC anti-alias, DC
blocking) with electrode impedance; noise (`.noise` analysis in SPICE);
common-mode rejection with mismatched electrode impedances; settling after
saturation or stimulation.

## Layout rules for microvolt signals

- Short, symmetric differential input traces; keep inputs away from
  switching regulators, clocks and SPI lines.
- Solid ground plane under the analog section; one connection point
  between analog and digital grounds (or one plane with careful
  partitioning).
- Battery or isolated supply for anything touching a person (IEC
  60601-1 patient leakage limits); USB-powered boards need isolation.
- Guard rings around high-impedance inputs; shielded electrode leads for
  long cables, with the shield driven or tied to a defined potential.
- Series resistors on inputs both protect (defibrillation, ESD) and add
  thermal noise: include them in the noise budget.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Comparing noise in µVpp and µVrms | factor of about 6.6 confusion | state the unit and bandwidth |
| Noise measured with inputs shorted only | real electrodes add thermal and interface noise | measure also with a dummy electrode impedance and with real electrodes |
| Gain 24 with large electrode offsets on a DC-coupled input | channel saturates | lower gain, AC coupling or offset removal |
| Ignoring datasheet test conditions (bandwidth, interval, temperature) | optimistic comparison | compare at the same bandwidth and conditions |
| Bias drive left open or overloaded | poor common-mode rejection, mains hum | connect and check the bias electrode impedance |
