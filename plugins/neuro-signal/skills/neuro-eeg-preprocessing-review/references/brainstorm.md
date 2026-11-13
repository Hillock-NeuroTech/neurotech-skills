# Brainstorm: workflow and traps

Brainstorm runs from MATLAB or as a standalone (compiled) application.
Not executed while writing this file. Process names change between
releases: generate the exact script from your own pipeline (see below)
rather than typing process names from memory.

Data live in a protocol database (`brainstorm_db`) organised as Protocol
> Subject > Condition/Run. Raw recordings are linked, not copied. Units in
the database are volts.

## Workflow (GUI)

1. **Create a protocol**; choose "No, use individual anatomy" only if MRIs
   exist, otherwise use the default anatomy (ICBM152).
2. **Review raw file** (link, do not import): pick the right file type in
   the dialog (Brainstorm cannot always tell `.cnt` vendors apart).
3. **Channel file**: add or edit electrode positions; project to the head
   surface if positions are generic.
4. **Event markers**: check event names and counts in the viewer's Events
   menu; detect blinks and heartbeats (Events > Detect eye blinks /
   heartbeats) if EOG/ECG exist.
5. **Frequency**: Power spectrum (Welch) on the raw link to find bad
   channels and line noise.
6. **Filters**: Pre-process > Notch filter and Band-pass filter on the
   continuous file (creates a new filtered raw file).
7. **Artefacts**: SSP (Artifacts > SSP: eye blinks / heartbeats) or ICA
   (Artifacts > ICA components). Review components in the viewer before
   removal.
8. **Import in database**: epochs around events, with baseline removal
   set here or later.
9. **Average** per condition and subject; then group statistics in the
   Process2 tab or source estimation (Head model > Noise covariance >
   Sources).

## Scripting

Every pipeline built in the Process1 or Process2 tab can be exported:
pipeline editor menu > **Generate .m script**. The generated code calls
`bst_process('CallProcess', 'process_<name>', sFiles, [], 'option', value,
...)` with the exact process names and options of your installed
version. Edit that script rather than writing calls by hand. Common
processes include raw import (`process_import_data_raw`), notch and
band-pass filters, SSP for blinks and heartbeats, ICA, epoch import
(`process_import_data_event`), averaging, head model, noise covariance and
inverse (`process_inverse_2018`).

Run headless with `brainstorm server` or `brainstorm nogui`, or the
standalone binary with a script argument.

## Strengths to use

- Source imaging for EEG, MEG and sEEG with tutorials matching each step.
- sEEG and ECoG: contact localisation on post-implant CT co-registered to
  MRI, anatomical labelling, and epileptogenicity mapping.
- fNIRS through the NIRSTORM plugin.
- Plugins manager installs FieldTrip functions, SPM, FreeSurfer
  interfaces and others on demand.

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Wrong file type chosen at Review raw file | wrong scaling or channel names | check one channel against the vendor viewer |
| Filtering imported epochs instead of the continuous file | edge artefacts | filter the raw link, then import |
| SSP or ICA computed but not checked | brain signal removed | inspect topographies and time courses; record which were removed |
| Default anatomy used for source claims about individuals | wrong localisation | individual MRI for single-subject claims; template only for group summaries |
| Database moved or renamed outside Brainstorm | broken links | move protocols with File > Export / Load protocol |

## Report

Brainstorm version (Help > About, date-based), processes in order with
their options (the generated script is the best record), artefact method
and components removed, anatomy used, head model type and inverse method.
