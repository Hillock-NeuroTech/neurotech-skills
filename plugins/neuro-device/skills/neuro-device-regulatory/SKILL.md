---
name: neuro-device-regulatory
description: Map a neurotechnology device (implanted BCI, neurostimulator, EEG/BCI wearable, neural recording system) to the regulatory testing and documentation it will need - FDA implanted-BCI guidance, ISO 14971 risk management, IEC 62304 software lifecycle, IEC 60601, ISO 14708, ISO 10993, IEC 62366, cybersecurity, EU MDR - and build a requirements-to-risk traceability matrix. Use whenever the user plans verification, prepares for a pre-submission or design review, or asks what standards apply. Engineering support, not certification or legal advice.
---

# Neurotech device regulatory mapping

Scope: engineering planning support. Classification and submission
strategy belong to the regulatory lead and, ideally, an FDA Q-Submission
or notified-body discussion.

## 0. Load the tool reference

Read `references/databases-and-tools.md`: neurotech FDA product codes,
public databases and requirements tools. Look up any product code live
with `scripts/fda_lookup.py` (class, 510(k)/De Novo/PMA records, MAUDE
reports, recalls) through openFDA.

## 1. Describe the device

Intended use and population, implanted or external, recording and/or
stimulation, wireless links, software (on-device, app, cloud), power
source, materials in contact with tissue and contact duration.

## 2. Map to standards and guidance

| Area | Typical references |
|---|---|
| Quality system | ISO 13485 |
| Risk management | ISO 14971 (hazard analysis, risk controls, residual risk) |
| Software lifecycle | IEC 62304 (safety class A/B/C), FDA guidance on content of premarket submissions for device software functions (Basic vs Enhanced documentation) |
| Electrical safety, EMC | IEC 60601-1, IEC 60601-1-2; ISO 14708-1 and -3 for active implants and neurostimulators |
| Biocompatibility | ISO 10993 series per contact type and duration |
| Usability | IEC 62366-1 |
| Cybersecurity | FDA premarket cybersecurity guidance; threat model, SBOM |
| MRI | ASTM F2052, F2213, F2182, F2119 for MR conditional labeling |
| Implanted BCI specifics | FDA guidance on implanted BCI devices for patients with paralysis or amputation (2021): non-clinical testing areas and clinical considerations |
| EU | MDR 2017/745 (active implantables are class III), harmonised standards |

Check the current versions of each document; they are revised.

## 3. Plan verification

For each requirement, define the verification method (test, analysis,
inspection), acceptance criterion, and the standard clause it serves.
Bench areas commonly needed for implanted neural interfaces: electrode
and lead mechanical durability, hermeticity and encapsulation lifetime
(accelerated ageing), electrochemical stimulation limits, electrical
safety and leakage, EMC, wireless performance, MRI safety, software
verification, and animal studies where bench tests cannot answer.

## 4. Traceability matrix

Use `assets/trace_matrix_template.csv`: requirement ID, requirement,
source (user need, standard clause), design output, verification ID and
method, result, linked hazard IDs, risk control. Every hazard with a risk
control must trace to a requirement and a verification; every safety
requirement must trace to a hazard. List gaps.

## Output

Device description, applicable standards table with reasons, verification
plan, filled traceability matrix with gaps highlighted, and open questions
for the regulatory lead.
