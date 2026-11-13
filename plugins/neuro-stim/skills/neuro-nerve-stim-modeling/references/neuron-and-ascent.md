# NEURON, ASCENT and field-coupled axon models

NEURON code checked by running it with NEURON 9.0.2 (November 2026).
ASCENT and the MRG model from their repositories; not run here (ASCENT
needs COMSOL).

## Applying an extracellular field to an axon in NEURON

The pattern every field-coupled model uses: compute the extracellular
potential at each segment (analytically or from a finite-element
solution), then play it into `e_extracellular` with the stimulus
waveform.

```python
import numpy as np
from neuron import h
h.load_file("stdrun.hoc")

ax = h.Section(name="axon"); ax.L, ax.diam, ax.nseg = 10000, 10.0, 201   # um
ax.Ra, ax.cm = 100, 1
ax.insert("hh"); ax.insert("extracellular")

def fire(amp_ma, pw_ms, dist_um=1000.0, sigma=0.3):
    xs = np.array([seg.x * ax.L for seg in ax])
    r_m = np.sqrt((xs - ax.L / 2) ** 2 + dist_um ** 2) * 1e-6
    ve_mv_per_ma = 1e-3 / (4 * np.pi * sigma * r_m) * 1e3     # point source in a homogeneous medium
    t = h.Vector([0, 1, 1, 1 + pw_ms, 1 + pw_ms, 10]); keep = []
    for seg, k in zip(ax, ve_mv_per_ma):
        v = h.Vector([0, 0, amp_ma * k, amp_ma * k, 0, 0])
        v.play(seg._ref_e_extracellular, t, True); keep.append(v)
    vend = h.Vector().record(ax(0.98)._ref_v)
    h.finitialize(-65); h.dt = 0.005; h.continuerun(10)
    return max(vend) > 0           # did a spike reach the far end?
```

Find the threshold by bisection on `amp_ma` per pulse width.

### What this toy model showed when run

| Check | Result |
|---|---|
| Threshold vs pulse width (cathodic, 1 mm away) | 5.26 mA at 0.05 ms, 2.64 at 0.1, 1.33 at 0.2, 0.55 at 0.5, 0.30 at 1.0 |
| Anodic vs cathodic at 0.2 ms | 5.06 vs 1.33 mA: anodic needs 3.8 times more |
| 2 ms cathodic pulse | no propagated spike up to 50 mA (block near the electrode) |
| Fitted chronaxie | 7-9 ms: unrealistic for mammalian nerve |

The long chronaxie is a property of the model, not of nerves: NEURON's
built-in `hh` is the 1952 squid axon at `h.celsius = 6.3` by default.
Use mammalian fibre models (MRG for myelinated fibres, a dedicated
C-fibre model for unmyelinated ones) at the temperature they were
published for, and exclude pulse widths that produce block from
strength-duration fits.

## MRG model

McIntyre, Richardson and Grill (2002): double-cable myelinated axon with
nodes, paranodes (MYSA, FLUT) and internodes (STIN); geometry
parameters per fibre diameter are tabulated in the paper and its
ModelDB entry. Interpolate geometry for diameters between tabulated
values only with a published interpolation, and state it.

## ASCENT (wmglab-duke/ascent)

An open pipeline (Musselman et al. 2021) that:

1. builds nerve geometry from segmented histology (or idealised
   shapes) and a cuff electrode from a library of cuff designs;
2. solves the extracellular potential in COMSOL (licence required);
3. places fibres in fascicles and runs MRG or other fibre models in
   NEURON with those potentials;
4. returns thresholds per fibre, recruitment curves and selectivity.

Configuration is in JSON files (sample, model, simulation); keep them with
the results as the record of the run.

## Alternatives

| Tool | Use |
|---|---|
| Sim4Life (commercial) | integrated EM fields and neuron models (including MRG) in anatomical models |
| COMSOL + NEURON by hand | full control, more work |
| PyPNS | Python peripheral nerve simulator, simpler geometries |
| NetPyNE | multi-cell networks on NEURON when stimulation targets circuits |

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Built-in `hh` at 6.3 °C used for mammalian nerve | thresholds and chronaxie far off | MRG or C-fibre models at their published temperature |
| `nseg` too small for the field gradient | wrong thresholds | refine until thresholds converge (odd `nseg`, about 10 per length constant or finer near the electrode) |
| Isotropic conductivity for endoneurium | wrong spread across fascicles | anisotropic endoneurium; perineurium as a thin resistive layer |
| Pulse widths that cause block included in fits | strength-duration fit fails | check each threshold actually propagates; drop blocked points |
| Not checking propagation | local depolarisation counted as activation | record at a distant node, as above |
| Model never compared with measured recruitment | untested predictions | validate against CAPs or EMG before design decisions |
