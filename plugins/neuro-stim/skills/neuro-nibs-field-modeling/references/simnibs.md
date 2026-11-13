# SimNIBS and ROAST: field-modelling recipes

SimNIBS details checked against the SimNIBS 4.6.0 source and its own
example scripts (release of March 2026); ROAST against its README
(November 2026). Neither was run here: both need an installed package
and an MRI. SimNIBS installs with its own installer (not plain pip) and
provides `simnibs_python` and command-line tools.

## SimNIBS workflow

1. **Head model**: `charm sub01 T1.nii.gz T2.nii.gz` creates the folder
   `m2m_sub01`. A T2 (or T2-FLAIR) improves skull and CSF. Open
   `m2m_sub01/charm_report.html` and check the segmentation overlay;
   errors in skull thickness change the field.
2. **No MRI**: use the example head `ernie` (`m2m_ernie`) or an MNI
   template and say so; conclusions then apply to an average head only.
3. **Simulate** (Python, run with `simnibs_python script.py`):

```python
import os
from simnibs import sim_struct, run_simnibs

S = sim_struct.SESSION()
S.subpath = "m2m_sub01"
S.pathfem = "tms_sim"
S.map_to_surf = True          # field on the middle grey-matter surface
S.map_to_fsavg = True         # and on fsaverage, for group analysis

tms = S.add_tmslist()
tms.fnamecoil = os.path.join("legacy_and_other", "Magstim_70mm_Fig8.ccd")   # coil files live in SimNIBS's coil folder
pos = tms.add_position()
pos.centre = "C3"             # EEG 10-10 label or MNI/subject coordinates
pos.pos_ydir = "CP3"          # direction of the coil handle
pos.distance = 4              # mm, coil to scalp
pos.didt = 1.0e6 * 1.4        # A/s; default 1e6 = 1 A/us. Set from the stimulator output
run_simnibs(S)
```

```python
tdcs = S.add_tdcslist()
tdcs.currents = [0.002, -0.002]          # amperes per channel, must sum to zero
el = tdcs.add_electrode(); el.channelnr = 1; el.centre = "C3"
el.shape = "rect"; el.dimensions = [50, 50]; el.thickness = 4      # mm
el = tdcs.add_electrode(); el.channelnr = 2; el.centre = "AF4"
el.shape = "rect"; el.dimensions = [50, 70]; el.thickness = 4
```

Temporal interference: two tDCS lists (one per pair), then
`simnibs.utils.TI_utils` to compute the envelope amplitude
(`examples/simulations/TI.py`).

4. **Optimise** (`simnibs.opt_struct`): `TMSoptimize` (coil position and
   orientation), `TmsFlexOptimization`, `TDCSoptimize` and
   `TDCSDistributedOptimize` (multi-electrode montages from a lead
   field), `TesFlexOptimization` (electrode positions and currents for
   focality or intensity goals). State the target, the constraint (total
   current, electrode count) and the objective.
5. **Neuronavigation**: `simnibs.localite`, `brainsight`, `softaxic` and
   `ant` read and write coil positions for those systems.

Outputs: `.msh` meshes with fields `E` (vector), `magnE`, `J`, `magnJ`
in V/m and A/m²; open them in the Gmsh viewer bundled with SimNIBS (results open there automatically when `S.open_in_gmsh` is true) or read them with
`simnibs.mesh_io.read_msh`. Surface and fsaverage maps are written as
GIfTI/FreeSurfer files.

## Reading the field

Report in the target region: a high percentile of `magnE` (99th or
99.9th, not the single maximum element, which is a meshing artefact),
the component normal to the cortex, and focality (volume or area above
half of that percentile). Use the same region definition for every
participant.

## ROAST (MATLAB)

```matlab
roast('example/MNI152_T1_1mm.nii', {'Fp1', 1, 'P4', -1}, ...
      'elecType', 'pad', 'elecSize', [50 50 3], 'capType', '1010');
roast_target(...)       % optimise after a 'leadField' recipe
reviewRes(...)          % reopen results
```

Currents in a ROAST recipe are in **milliamperes**; SimNIBS uses
**amperes**. Electrodes come from the 10/20, 10/10, 10/05, BioSemi-256 or
EGI-256 layouts. ROAST segments the MRI with SPM and meshes with
iso2mesh; check the segmentation figures it produces.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Currents entered in mA in SimNIBS or A in ROAST | field off by a factor of 1000 | SimNIBS amperes, ROAST milliamperes |
| `didt` left at the default 1 A/us | TMS field not tied to the intensity used | derive dI/dt from the stimulator output and coil (manufacturer data or measurement) |
| Coil file that does not match the coil model or version | wrong field shape and strength | use the exact coil model; check the coil folder |
| Reporting the maximum element of `magnE` | inflated, mesh-dependent value | report a high percentile |
| Template head for single-person claims | dose error from anatomy | individual MRI for individual targeting |
| Skipping the segmentation check | thin or missing skull, CSF errors | inspect `charm_report.html` and fix or re-run with T2 |
| Comparing fields between versions without noting it | default conductivities and meshing change between releases | report the version and conductivities |
