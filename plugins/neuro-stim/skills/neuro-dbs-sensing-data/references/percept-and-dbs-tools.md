# Percept exports, Lead-DBS and OSS-DBS

Percept section and field names checked against the perceive toolbox
source (`neuromodulation/perceive`, November 2026). Lead-DBS and OSS-DBS
from their repositories; not run here (MATLAB and imaging data needed).
Research tools; none is for clinical decisions.

## Medtronic Percept session JSON

One export per programming session (`Report_Json_Session_Report_*.json`).
Sections that hold signals:

| Section | Holds | Typical use |
|---|---|---|
| `BrainSenseTimeDomain` | streamed LFP during a BrainSense session, per channel | time-domain analysis, beta bursts, aDBS work |
| `BrainSenseLfp` | power in the selected band and stimulation amplitude, streamed alongside | relating beta power to stimulation |
| `IndefiniteStreaming` | streaming from several contacts without stimulation | off-stimulation recordings |
| `LfpMontageTimeDomain` (with `BrainSenseSurvey`/`BrainSenseSurveysTimeDomain`) | short survey recordings across contact pairs | choosing the sensing pair |
| `DiagnosticData` > `LFPTrendLogs` | chronic band power every few minutes over days | circadian and long-term analyses |
| `DiagnosticData` > `LfpFrequencySnapshotEvents` | spectra captured when the patient marks an event | symptom-linked spectra |
| `Groups`, `GroupHistory`, `Stimulation`, `LeadConfiguration`, `Impedance`, `DeviceInformation`, `BatteryInformation`, `PatientEvents`, `EventSummary` | settings, contacts and device state | context for every analysis |

Each time-domain entry has `Channel`, `SampleRateInHz`,
`FirstPacketDateTime`, `TimeDomainData`, and per-packet
`GlobalSequences`, `GlobalPacketSizes` and `TicksInMses` (stored as
comma-separated strings). Packets arrive every 250 ms; a step larger
than 250 ms between consecutive `TicksInMses` values means lost packets.

`scripts/percept_timedomain.py` rebuilds each stream with lost packets as
NaN gaps. On a synthetic export with three packets removed it reported 3
missing packets in two gaps at 2.5 s and 6.25 s and placed the data after
each gap at the correct time.

**perceive** (MATLAB): `perceive(files, sub, session, extended)` converts
exports to FieldTrip-format files with BIDS-like names and plots, and
includes ECG cleaning and missing-data correction. Use it as the reference
when results from another reader differ.

## Percept traps

| Trap | Effect | Fix |
|---|---|---|
| Concatenating `TimeDomainData` ignoring ticks | events after a gap misplaced in time | rebuild with gaps (script above or perceive) |
| Comparing band power across firmware versions without checking | export fields and filters differ between versions | record firmware version from `DeviceInformation` |
| ECG in single-sided or low-amplitude recordings | broadband peaks, false beta changes | detect QRS and subtract templates; compare spectra before and after |
| Stimulation artefact and its aliases at 250 Hz sampling | spurious peaks | compute where stimulation frequency aliases and avoid those bins |
| Using `FirstPacketDateTime` as exact sample time | clock offsets of seconds against external systems | align on shared events (stimulation onset, tapping) with `neuro-sync-forensics` |

## Lead-DBS (MATLAB)

Localises DBS electrodes from pre- and post-operative imaging and models
stimulation:

1. Import DICOM or NIfTI (pre-op MRI, post-op CT or MRI) into a patient
   folder.
2. Co-register post-op to pre-op, normalise to MNI space (several
   methods; check each step's figures), correct brain shift if needed.
3. Reconstruct electrode trajectories and contacts; pick the electrode
   model actually implanted.
4. Visualise with atlases (subthalamic nucleus, GPi, thalamic nuclei).
5. Volume of tissue activated or pathway activation for the programmed
   settings; group analyses (sweet spots, connectomics).

Report the Lead-DBS version, registration and normalisation methods,
atlas and version, electrode model and the VTA method.

## OSS-DBS

Open-source finite-element simulation of DBS fields and axon activation
(SFB-ELAINE/OSS-DBSv2 is the current version), callable from Lead-DBS.
Use it when the VTA approximation is not enough: it computes potentials
in a patient-specific volume conductor and the activation of modelled
axons or pathways.

## Other implants

- **Summit RC+S**: several JSON files per session; use the investigators'
  open processing pipeline and read Sellers et al. 2021 on its timing
  issues.
- **NeuroPace RNS**: data come through NeuroPace's data exports (ECoG
  snippets triggered by detections or scheduled); sampling and storage
  are event-driven, so time series are not continuous.
