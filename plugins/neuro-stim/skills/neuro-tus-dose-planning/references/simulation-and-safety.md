# TUS simulation tools and safety levels

k-wave-python API checked against version 0.6.2 (November 2026);
BabelBrain and Kranion from their repositories; ITRUSST levels from
Aubry et al. 2025, *Brain Stimulation* 18(6):1896-1905,
doi:10.1016/j.brs.2025.10.007. No acoustic simulation was run here.

## ITRUSST levels for non-significant risk

These are consensus levels, not safety limits; they assume participants
without contraindications, compromised thermoregulation, vascular
vulnerability or ultrasound contrast agents.

| Effect | Non-significant risk if |
|---|---|
| Mechanical | MI (or the transcranial MItc) does not exceed 1.9 |
| Thermal (any one of) | peak temperature rise at most 2 °C (or peak at most 39 °C from 37 °C); thermal dose at most 2 CEM43 in brain, 16 CEM43 in bone, 21 CEM43 in skin; or thermal index within the values tabulated for the exposure time |

The FDA diagnostic-imaging reference (Ispta.3 up to 720 mW/cm², MI up to
1.9) is often quoted alongside; it was set for imaging, not for TUS.

`scripts/tus_indices.py` computes MI, Isppa, Ispta (with both pulse and
train duty cycles) and CEM43 from a temperature trace, and compares them
with these levels. Its tests reproduce reference values: MI 1.414 for
1 MPa at 0.5 MHz; Isppa 33.3 W/cm² for 1 MPa in water; 1 CEM43 for one
minute at 43 °C. Feed it in situ values from simulation, not free-field
values.

Ispta depends on the averaging window: in the script's example the same
protocol gives 640 mW/cm² over the session and 6,400 mW/cm² within a
pulse train. Always say which.

## k-Wave (MATLAB) and k-wave-python

Pseudospectral time-domain acoustic simulation; the standard engine
behind many TUS planning tools.

```python
from kwave.kgrid import kWaveGrid
from kwave.kmedium import kWaveMedium
from kwave.ksource import kSource
from kwave.ksensor import kSensor
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
from kwave.options.simulation_options import SimulationOptions
from kwave.options.simulation_execution_options import SimulationExecutionOptions
from kwave.utils.mapgen import make_bowl          # focused bowl transducer

kgrid = kWaveGrid([Nx, Ny, Nz], [dx, dx, dx])     # metres
medium = kWaveMedium(sound_speed=c_map, density=rho_map, alpha_coeff=alpha_map, alpha_power=y)   # y: power-law exponent, one value for the grid
kgrid.makeTime(medium.sound_speed)                 # time step from the CFL condition
...
out = kspaceFirstOrder3D(kgrid, source, sensor, medium,
                         SimulationOptions(pml_inside=False, data_cast="single", save_to_disk=True),
                         SimulationExecutionOptions(is_gpu_simulation=True))
```

- Grid spacing: at least 6-10 points per wavelength in the softest
  medium; skull needs fine sampling.
- Skull acoustic properties from CT Hounsfield units (or pseudo-CT);
  the conversion used must be reported.
- k-wave-python calls compiled C++/CUDA binaries; a GPU makes 3-D head
  simulations practical.
- Thermal: k-Wave's `kWaveDiffusion` (MATLAB) or the planning tools'
  thermal modules, using the full pulsing sequence.

## Planning tools

| Tool | What it does |
|---|---|
| k-Plan (commercial) | treatment planning on k-Wave for common TUS transducers; acoustic and thermal |
| BabelBrain (open, ProteusMRIgHIFU/BabelBrain) | GUI planning from MRI/CT with neuronavigation, acoustic and thermal simulation, supports common transducers |
| Kranion (open, jws2f/Kranion) | transcranial focused-ultrasound visualisation and planning |
| PRESTUS and similar pipelines | scripted k-Wave planning for research groups |

Validate the planning tool against hydrophone measurements of your
transducer in free field before trusting in situ predictions.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Using free-field values as in situ dose | dose overstated or understated by the skull | simulate per person, or derate and say how |
| MI from peak positive pressure | MI wrong | MI uses peak negative pressure and centre frequency in MHz |
| One duty cycle quoted without saying which | Ispta ambiguous by up to orders of magnitude | report pulse and train duty cycles and the averaging window |
| Coarse grid in skull | focus position and pressure errors | refine until results stop changing |
| Thermal estimate from a single pulse | heating underestimated | simulate the whole sequence, including repeated trains |
| No sham controlling sound | auditory confound read as neuromodulation | matched sham and masking (`neuro-sham-and-blinding-design`) |
