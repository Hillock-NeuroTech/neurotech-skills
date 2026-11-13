# FDA databases, product codes and requirements tools

Product codes and counts below were retrieved live from openFDA on 13
November 2026 with `scripts/fda_lookup.py`. Classifications change: query
again before relying on one. Engineering support, not regulatory advice.

## Looking up a product code

```bash
python3 scripts/fda_lookup.py codes "transcranial magnetic"
python3 scripts/fda_lookup.py profile GWQ --json gwq.json
```

`profile` returns device class, regulation number, implant flag, the
number of 510(k), De Novo and PMA records with the latest decisions,
MAUDE adverse-event reports by type and year, and recalls with root
causes. Example, product code MHY (implanted stimulator for Parkinsonian
tremor, Class III, implant): 638 PMA records, the latest a Percept PC
BrainSense supplement decided on 30 October 2026; about 27,000
malfunction, 25,900 injury and 750 death reports in MAUDE; 46 recalls,
with software design, process design and device design among the root
causes. MAUDE reports are unverified and have no denominators: never read
them as incidence rates.

## Neurotech product codes found

| Code | Device | Class |
|---|---|---|
| GWQ | Full-montage standard electroencephalograph | II |
| OMC | Reduced-montage standard electroencephalograph | II |
| OLT | Non-normalising quantitative EEG software | II |
| OLX | Source localisation software for EEG or MEG | II |
| PIW | Brain-injury adjunctive interpretive EEG assessment aid | II |
| IKN | Diagnostic electromyograph | II |
| GWF, GWJ, GWE | Electrical, auditory, photic evoked-response stimulators | II |
| MHY | Implanted stimulator for Parkinsonian tremor (DBS) | III |
| SGS | Deep brain stimulation for dystonia | III |
| PFN | Implanted brain stimulator for epilepsy | III |
| QQC | Brain stimulation programming planning software | II |
| LGW, GZB | Implanted spinal-cord stimulators for pain | III, II |
| QAK, PKR | Non-invasive vagus nerve stimulators (migraine, headache) | II |
| SFJ | Vagus nerve stimulator for rheumatoid arthritis | III |
| OKP, QCI, QMD, SIG | TMS for migraine, OCD, smoking cessation, PTSD | II |
| JXK, QJQ | Cranial electrotherapy stimulators (depression; insomnia/anxiety) | III, II |

No classification exists for "brain-computer interface": implanted BCIs
have so far been studied under investigational device exemptions, and
the 2021 FDA guidance on implanted BCI devices describes the
non-clinical and clinical expectations.

## Other public sources

| Source | Use |
|---|---|
| FDA 510(k), De Novo, PMA and Classification databases (accessdata.fda.gov) | full decision summaries and predicate devices, beyond what openFDA returns |
| MAUDE (web) | individual adverse-event narratives |
| GUDID / AccessGUDID | device identifiers and labelling attributes |
| FDA Recognized Consensus Standards database | which standard editions FDA recognises |
| ClinicalTrials.gov | ongoing trials of comparable devices, endpoints |
| EUDAMED | EU device registration and certificates (modules rolling out) |
| Notified-body and competent-authority guidance (MDCG documents) | EU MDR interpretation |

## Requirements, risk and traceability tools

| Tool | Notes |
|---|---|
| Spreadsheet or CSV in version control (`assets/trace_matrix_template.csv`) | adequate for small teams; keep it diff-able |
| Greenlight Guru, Ketryx, Matrix Requirements | eQMS built for medical devices |
| Jama Connect, Polarion, Codebeamer | requirements management with traceability |
| Git-based (doorstop, sphinx-needs) | requirements as text next to code |

## Traps

| Trap | Effect | Fix |
|---|---|---|
| Picking a predicate by device name alone | wrong product code and pathway | compare intended use and technology, then the decision summary |
| Reading MAUDE counts as risk | false conclusions | use for hazard identification, not rates |
| Citing a standard edition FDA no longer recognises | test plan rejected | check the recognised-standards database |
| openFDA treated as complete | missing recent decisions | confirm on accessdata.fda.gov |
