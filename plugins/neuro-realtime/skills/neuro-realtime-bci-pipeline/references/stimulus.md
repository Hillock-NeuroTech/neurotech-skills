# Stimulus presentation and event markers: PsychoPy and Psychtoolbox

Not executed while writing this file (no display here); written from the
PsychoPy and Psychtoolbox documentation. Check function names against your
installed version. Validate any timing claim with a photodiode
(`neuro-stimulus-timing-audit`).

## Principles

- A stimulus appears on the **frame** after the flip that draws it. Its
  true onset is the flip time plus the display's own delay (input lag,
  pixel response), which software cannot see.
- Send the event marker **at the flip** that shows the stimulus, from the
  same process, and log the flip timestamp next to it.
- Time durations in **frames**, not seconds, for visual stimuli: at 60 Hz
  a 100 ms stimulus is 6 frames; 110 ms cannot be shown.
- Hardware triggers (TTL into the amplifier) beat network markers for
  time-locked analyses; network markers are fine as labels.

## PsychoPy

```python
from psychopy import visual, core, event
import pylsl

win = visual.Window(fullscr=True, screen=0, units="height", waitBlanking=True)
rate = win.getActualFrameRate()                 # measure, do not assume 60
outlet = pylsl.StreamOutlet(pylsl.StreamInfo("Markers", "Markers", 1, 0, pylsl.cf_string, "psychopy-markers"))
stim = visual.GratingStim(win, sf=5, size=0.3)

for trial in trials:
    stim.draw()
    win.callOnFlip(outlet.push_sample, [f"stim/{trial}"])   # marker sent at the flip
    onset = win.flip()                          # returns the flip time
    for _ in range(n_frames - 1):               # hold for n frames
        stim.draw(); win.flip()
    win.flip()                                  # blank
```

- Builder experiments: set component durations in frames; add a code
  component that pushes LSL markers with `win.callOnFlip`, or use the
  parallel or serial port component for TTL triggers.
- `win.recordFrameIntervals = True` then inspect `win.frameIntervals`
  for dropped frames after the run.
- Audio: use the PTB audio backend (`prefs.hardware['audioLib'] = ['PTB']`)
  with low-latency mode for precise sound onsets.
- Run fullscreen on the primary display, with other programs closed and
  power saving off.

## Psychtoolbox (MATLAB / Octave)

```matlab
PsychDefaultSetup(2);
[win, rect] = PsychImaging('OpenWindow', max(Screen('Screens')), 0);
ifi = Screen('GetFlipInterval', win);           % measured frame interval
Priority(MaxPriority(win));
vbl = Screen('Flip', win);
for t = 1:nTrials
    Screen('DrawTexture', win, tex);
    vbl = Screen('Flip', win, vbl + (waitFrames - 0.5) * ifi);   % schedule by frames
    % send the trigger right here: lsl outlet push, or a TTL write
    stimOnset(t) = vbl;
end
Priority(0); sca;
```

`Screen('Flip')` returns the time of the vertical blank at which the
image swapped. Psychtoolbox prints synchronisation warnings at start-up:
read them; a failed sync test means timing is not trustworthy on that
setup. Sound: `PsychPortAudio` with `reqlatencyclass` 2 or higher and
scheduled start times.

## Triggers

| Route | Typical use | Notes |
|---|---|---|
| Parallel port (`psychopy.parallel`, `io64`/`ioObj` in MATLAB) | older amplifiers | sub-millisecond; ports are rare on new PCs |
| USB-TTL boxes (Brain Products TriggerBox, Cedrus StimTracker, LabJack, Arduino/Teensy) | most current setups | check their latency once with a photodiode |
| Serial (`serial` / pyserial) | some amplifiers and boxes | a few ms; depends on the driver |
| LSL markers | multi-device recordings | software timing; validate offset |
| Photodiode on the screen into an aux channel | ground truth for visual onsets | the reference every other route is checked against |

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Marker sent before `flip()` | marker early by up to one frame plus scheduling delay | `callOnFlip`, or send right after `Flip` returns |
| Durations in seconds with `core.wait` | stimulus lengths vary by a frame | count frames |
| Windowed mode or a second monitor mirrored | tearing, missed flips | fullscreen on one display |
| Assuming 60 Hz | wrong durations on 59.94, 75, 120, 144 Hz displays | measure the frame rate |
| Laptop on battery or with variable refresh | irregular frames | mains power, fixed refresh |
| Never checking dropped frames | silently wrong durations | log frame intervals; report the drop count |
