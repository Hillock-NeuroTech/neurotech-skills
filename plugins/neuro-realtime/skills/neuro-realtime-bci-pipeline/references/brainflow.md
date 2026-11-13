# BrainFlow: device-agnostic acquisition

Checked against BrainFlow 5.24 by running the code below with the
synthetic board (November 2026). BrainFlow talks to about 70 boards
(OpenBCI Cyton, Ganglion, Daisy; Muse 2, Muse S; g.tec Unicorn; ANT
Neuro eego; BrainBit; Neurosity; Mentalab Explore; EmotiBit; Shimmer;
and others) through one API in Python, C++, Java, C#, Julia, Rust and
MATLAB.

## Recipe

```python
import time
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

board_id = BoardIds.SYNTHETIC_BOARD.value         # develop without hardware; then e.g. BoardIds.CYTON_BOARD.value
params = BrainFlowInputParams()
# params.serial_port = "/dev/cu.usbserial-XXXX"   # Cyton/Ganglion dongle; Bluetooth boards use mac_address or serial_number
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream(45000)                          # ring buffer size in samples
# board.start_stream(45000, "streaming_board://225.1.1.1:6677")  # also publish for other programs
time.sleep(5)
board.insert_marker(1.0)                           # marker written into the data, at the next sample
window = board.get_current_board_data(250)         # latest 250 samples, buffer kept
data = board.get_board_data()                      # everything since the last call, buffer emptied
board.stop_stream(); board.release_session()

fs = BoardShim.get_sampling_rate(board_id)
eeg = BoardShim.get_eeg_channels(board_id)         # row indices into `data`
ts = data[BoardShim.get_timestamp_channel(board_id)]   # Unix time in seconds
markers = data[BoardShim.get_marker_channel(board_id)]
```

`data` is a 2-D array: rows are channels as described by
`BoardShim.get_board_descr(board_id)` (EEG, accelerometer, package
number, timestamp, marker...), columns are samples. Units for EEG rows
are microvolts on the supported boards; confirm in the board description.

## Filtering online

`DataFilter.perform_bandpass(x, fs, low, high, order, FilterTypes.BUTTERWORTH.value, 0)`
works in place on a contiguous 1-D float64 array. The plain types
(`BUTTERWORTH`, `CHEBYSHEV_TYPE_1`, `BESSEL`) are causal: an impulse at
sample 1000 produced no output before sample 1000 when checked. The
`*_ZERO_PHASE` variants filter forwards and backwards: offline only.

Filtering each pulled window separately restarts the filter every time
(edge transients at each window start). For true online filtering keep
filter state across chunks with `scipy.signal.sosfilt(sos, x, zi=state)`,
or filter a longer buffer and keep only its end.

Other helpers: `DataFilter.detrend`, `perform_bandstop` and
`remove_environmental_noise` (50/60 Hz), `get_psd_welch`,
`get_band_power`, `get_avg_band_powers`, `write_file` / `read_file`
(CSV). The `PLAYBACK_FILE_BOARD` replays a recorded file as if it were a
board; `STREAMING_BOARD` receives a stream another BrainFlow process
publishes.

## Checks

1. **Real rate**: compute it from the timestamp row over a few minutes;
   the synthetic board gave 249.9 Hz for a nominal 250. Bluetooth boards
   deviate more and drop packets.
2. **Lost packets**: the package-number row (`get_package_num_channel`)
   counts packets; gaps mean lost data. Cyton counts 0-255 and wraps.
3. **Cyton + Daisy**: 16 channels at 125 Hz (each board's samples
   alternate); check the board description before assuming 250 Hz.
4. **Markers** from `insert_marker` land at the next acquired sample on
   the acquisition thread; they carry the software timing of the call,
   not the stimulus onset.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Zero-phase filter type used online | output uses future samples; offline accuracy that cannot be reproduced live | causal types online |
| Filtering each window independently | transients at every window start | carry filter state across chunks |
| `get_board_data()` in a loop when the full record is wanted later | data already removed from the buffer | keep your own copy, or use `get_current_board_data` |
| Bluetooth board near Wi-Fi or on a busy USB hub | packet loss, irregular timing | dongle on a short USB extension, away from other radios; watch package numbers |
| Nominal rate used for epoch timing on wireless boards | events drift | use the timestamp row |
| Forgetting `release_session()` after an error | port stays busy | wrap in `try/finally` |
