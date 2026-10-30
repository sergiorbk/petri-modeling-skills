---
name: petri-training-export
description: Export an explicitly requested Petri modeling session into an auditable ZIP for LLM training, preserving real tasks, model artifacts, available conversations, tool traces and verification provenance.
---

# Export a modeling session for training

Use this guide when the user requests a training archive or has authorized an
end-of-session export. There is no universal session-end event across clients:
invoke the application's export tool or ZIP export button explicitly. Export the
useful evidence the application actually has, and distinguish missing evidence from
an empty but observed result. Do not manufacture a transcript or successful checks.

## Capture boundary

The application can export its current model and its own observed session data.
An external MCP client holds its own conversation and must explicitly supply the
task, messages or external traces if they should be included. Record that origin as
`client-provided`; the application's inability to read an external conversation is
not evidence that the conversation was empty. Do not collect unrelated files or
other sessions to fill gaps.

Export actual user and assistant messages as conversation records. Store actual
tool requests and outcomes separately. Do not append system prompts, the shared
skill text or reconstructed summaries as if they were real conversation turns.
An explicitly written task description belongs in `task.json`, with its assumptions
and acceptance criteria, rather than in an invented user message.

Exclude authentication headers, MCP tokens, provider API keys, passwords and other
credentials from exported messages, tool arguments, results and error text.
Petri-net token counts are model data, not credentials. If redaction removes useful
evidence, record that limitation without preserving the secret itself.

## Canonical ZIP contents

The schema of record is
`petri_modeling_skills/schemas/training-bundle.schema.json`. Python adapters can
load it with `read_schema("training-bundle")`; other applications package the same
JSON file. Its top-level schema validates `manifest.json`; its `$defs` validate the
individual JSON artifacts. Both applications must use the same schema version.

| File | Content |
|---|---|
| `manifest.json` | Schema version, title, UTC creation time, application and shared-skills provenance, review status, capture scope, file hashes and missing-data reasons |
| `task.json` | Original task when known, actual clarifications, stated assumptions and acceptance criteria |
| `model.pnml` | Final actual graph exported by the application's normal PNML writer |
| `conversation.jsonl` | Real user and assistant messages, one JSON object per line |
| `tool-calls.jsonl` | Real captured tool names, arguments and observed outcomes, one JSON object per line |
| `verification.json` | Recorded checks and simulation evidence, with provenance; `unknown` when unobserved |
| `network.png` | Optional image of the actual final net without application chrome, using the application's reusable network-image renderer |
| `model-geometry.json` | Optional element geometry for that exact network image, with its pixel coordinate system, origin, scale and dimensions |
| `screenshot.png` | Optional application view for human quality review |
| `editor-observations.json` | Optional raw protocol, statistics or control values with their origin; they may be stale and do not count as verified simulation evidence |

The five artifacts besides `manifest.json` are always present. If a conversation or
tool trace is unavailable, write a zero-byte JSONL file and list it in `missing_data`
with a reason. Use `null` for an unknown original task and for an unobserved
simulation. An empty assumptions or clarifications array means none were supplied;
it does not authorize fabricating them.

List every artifact, including optional image or observation files, in `files` with its actual
media type, purpose and SHA-256 hash of the uncompressed file bytes. Do not include
`manifest.json` in its own hash list. Use only the canonical archive entry names,
UTF-8 JSON/JSONL and UTF-8 PNML. Reject duplicate entry names and unsafe paths.

Store the ZIP under a sanitized, meaningful session title plus a UTC timestamp,
for example `parallel-machines-20261030T120000Z.zip`. A useful title does not change
the user's original task or create missing evidence.

## Reusable image and geometry

Use the same network-image renderer for a standalone image export and `network.png`
inside the training ZIP. Render the real model, not a reconstructed diagram. Keep
application chrome in `screenshot.png`, rather than mixing it into the net image.

`model-geometry.json` describes pixel-space element bounds for `network.png`, with
`coordinate_system: "image-pixels"`, image dimensions and a transform where
`pixel = (world - origin) * scale`. Supply the exact viewport and scale used by the
renderer. Include geometry only with its matching image and identify clipped
elements. The schema's `modelGeometry` definition records those fields.

Set `label_status` to `renderer-derived` only when the bounds are derived from the
same rendered shapes and clipping as the supplied image. Raw PNML coordinates,
unrelated editor positions or estimated boxes are `unverified`; they are not
ground-truth detector labels. Geometry can help a later image-training pipeline,
but do not manufacture classes or mark unreviewed annotations as accepted labels.

## Verification and review status

Keep archive review `status` separate from `verification.status`:

- New exports are `unreviewed` unless an actual review decision was supplied.
- `accepted` records an explicit review decision and is suitable as a positive
  training example only when the model and its recorded checks are validated.
- `rejected` examples and failed traces can support a separate correction or
  diagnostic dataset. Do not mix them into accepted positive examples implicitly.
- `verification.status` is `unknown` when no actual checks were recorded. Writing
  a ZIP, parsing XML or seeing a plausible diagram alone does not prove the model
  meets the task. A passed schema check proves its own limited claim, not all
  semantic acceptance criteria.

Preserve the parameters, recorded results and provenance of any included simulation.
Do not invent a seed, sample count, run duration, expected metric or successful
outcome. Include failure details as observed facts, and describe unsupported or
unperformed checks in `missing_data` or as `unknown` verification checks.

Before delivery, verify required files, parseability of observed JSONL records,
manifest hashes and agreement with the shared schema. Report where the ZIP was
written and any important missing evidence. Do not claim it was uploaded or used
for training unless that separate action actually occurred.
