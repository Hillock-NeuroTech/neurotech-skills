# Lab Streaming Layer: streams, clocks, recording

Checked against pylsl 1.18.6 (bundled liblsl 1.18) and MNE-LSL 1.15 by running
the code below on one machine (November 2026). LSL moves time-stamped
samples between programs on a network and keeps a shared clock. It does
not make a device's timing accurate: it records what each program saw.

## Concepts that decide whether timing is right

- **Every sample has a timestamp in the sender's `local_clock()`**
  (seconds, monotonic). When a sender pushes a chunk without
  timestamps, LSL stamps the last sample "now" and back-fills earlier
  samples at the nominal rate, so timestamps carry a few milliseconds of
  jitter.
- **Clock offset**: `inlet.time_correction()` estimates the offset
  between sender and receiver clocks; add it to sender timestamps to
  convert them to the receiver's clock. LabRecorder stores these
  measurements in the XDF file, and pyxdf applies them.
- **Nominal rate is a promise, not a measurement.** Devices drift by tens
  to thousands of parts per million. Use timestamps, not sample counts,
  to find when something happened.
- **Markers** are a separate, irregular-rate stream (`nominal_srate=0`,
  `cf_string` or `cf_int32`), stamped when the marker is pushed: the time
  the software decided, not the time the stimulus reached the eye or ear.

## Sending

```python
import pylsl

info = pylsl.StreamInfo("MyAmp", "EEG", n_channels, 250.0, pylsl.cf_float32, source_id="amp-sn-1234")
chans = info.desc().append_child("channels")
for name in ch_names:
    ch = chans.append_child("channel")
    ch.append_child_value("label", name); ch.append_child_value("unit", "microvolts"); ch.append_child_value("type", "EEG")
outlet = pylsl.StreamOutlet(info, chunk_size=10)
outlet.push_chunk(samples)                       # list of rows; or push_sample(row, timestamp)

markers = pylsl.StreamOutlet(pylsl.StreamInfo("Markers", "Markers", 1, pylsl.IRREGULAR_RATE, pylsl.cf_string, "task-markers"))
markers.push_sample(["stim/left"])               # push at the moment of the event, e.g. right after win.flip()
```

Set a stable `source_id` (device serial number): it lets inlets
reconnect automatically after a dropout and lets LabRecorder find the
same stream again.

## Receiving

```python
streams = pylsl.resolve_byprop("type", "EEG", timeout=10.0)    # or resolve_streams(), resolve_bypred()
inlet = pylsl.StreamInlet(streams[0], max_buflen=60, processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)
while running:
    data, stamps = inlet.pull_chunk(timeout=0.0, max_samples=1024)   # non-blocking, all pending samples
    ...
```

`proc_clocksync` converts timestamps to the local clock; `proc_dejitter`
smooths chunk jitter assuming a regular rate (do not use it on irregular
streams). Pull in chunks; per-sample pulls waste CPU and fall behind.

Check a live stream with `scripts/lsl_stream_check.py`: it reports the
true sampling rate, gaps, lost samples (with a counter channel), clock
offset and how old samples are when they arrive. On a simulated stream
declared at 250 Hz it measured 250.004 Hz; with the stream running 1%
fast it measured 252.497 Hz and warned; with 25 samples dropped it found
one 105 ms gap and 25 lost samples.

## Recording

- **LabRecorder** records any set of streams into one XDF file, including
  clock-offset measurements. Start it before the experiment; check that
  every expected stream is ticked and green.
- Load with `pyxdf.load_xdf(path, synchronize_clocks=True,
  dejitter_timestamps=True)`; each stream comes back with its own
  `time_stamps` and `time_series`. Build an `mne.io.RawArray` per signal
  stream, and turn marker timestamps into annotations relative to the
  first EEG timestamp.
- Vendor LSL apps exist for most amplifiers (Brain Products, g.tec,
  ANT, BioSemi, Cognionics, OpenBCI via BrainFlow), eye trackers and
  input devices. Prefer the vendor's app for the amplifier; check its rate
  with the stream check above.

## Development without hardware: MNE-LSL replay

```python
from mne_lsl.player import PlayerLSL
from mne_lsl.stream import StreamLSL

player = PlayerLSL("recording.fif", chunk_size=10, name="replay"); player.start()   # any MNE Raw or file
stream = StreamLSL(bufsize=5, name="replay").connect(acquisition_delay=0.001)
stream.filter(1.0, 40.0)                       # causal filter applied as data arrive
data, times = stream.get_data(winsize=2)       # latest 2 s
```

Replaying a real recording through the whole online pipeline is the
best rehearsal before a session: the decoder sees data at the real rate
and chunk size. `PlayerLSL` also streams annotations as markers.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Using sample index / nominal rate as time | events drift by tens of ms over an hour | use timestamps (after clock sync) |
| Marker pushed before `flip()` returns, or from a different thread | markers early by up to a frame or more | push immediately after the flip that shows the stimulus; validate with a photodiode |
| Several streams with the same name | inlet connects to the wrong one | resolve by `source_id`, or name streams uniquely |
| Loading XDF without `synchronize_clocks` | streams offset by the clock difference between machines | `synchronize_clocks=True` |
| `proc_dejitter` on a marker stream | marker times smeared | dejitter only regular-rate streams |
| Firewall or VPN blocks multicast | streams not found on other machines | allow LSL ports or configure `lsl_api.cfg` with known peers |
| Wi-Fi between devices | bursts and delays of tens to hundreds of ms | wired Ethernet for acquisition |
| `max_buflen` too small during a pause in pulling | samples silently dropped | size the buffer for the longest pause; check counters |
