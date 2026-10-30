---
name: pnml-standard
description: Exchange and validate PNML Place/Transition nets using the ISO/IEC 15909-2 grammar, valid identifiers and references, standard graphics, and explicit application extensions.
---

# PNML is an interchange contract

Read this before importing, exporting or modifying the shape of PNML. Prefer the
application's existing reader and writer. Successful XML parsing does not prove
schema conformance or equivalence of the modeled behavior.

## Standard document structure

For the supported P/T net type, use namespace
`http://www.pnml.org/version-2009/grammar/pnml` and net type
`http://www.pnml.org/version-2009/grammar/ptnet`. Preserve the structure
`pnml / net / page` and write places, transitions, reference nodes and arcs in the
scope allowed by the grammar. Use the published RELAX NG P/T net definition
`ptnet.pntd`, including `pnmlcoremodel.rng` and `conventions.rng`, as the authority
for allowed elements, attributes, labels and value types.

- IDs must be valid XML NCNames and unique across the document. Resolve every arc endpoint and reference;
  do not infer identity from a display name or from visual proximity.
- A place marking is a nonnegative integer; an ordinary P/T arc weight is a positive
  integer. Use the standard `initialMarking/text` and `inscription/text` labels.
- Keep graph arcs local to their page. For cross-page composition use valid
  reference nodes that resolve to the intended concrete place or transition.
  Reference chains must resolve and must not form cycles or change node type.
  Put initial markings on concrete places, not on `referencePlace` nodes.
- Encode positions and other standard drawing information in `graphics`. Do not
  replace standard graphics with a private coordinate block.
- Preserve the distinction between a standard ordinary arc and an application's
  read or inhibitor arc. P/T net labels do not permit inventing an arbitrary new
  core arc element for those semantics.

## Application extensions and Petri-objects

Timed delays, distributions, priorities and application-specific object metadata
may require `toolspecific` extensions. Put nonstandard information inside the
extension permitted by the grammar rather than changing the PNML core vocabulary.
A schema-valid extension is still meaningful only to readers that implement it.

Preserve each producer's own `toolspecific` block and identify it by its documented
`tool` value. A product version is metadata, not necessarily a schema discriminator;
follow the consuming reader's actual compatibility contract. Do not silently
translate unsupported semantics into a superficially similar ordinary P/T net.

For the consuming applications' composed models, standard reference nodes carry
shared identity. A duplicated `petriObjectLinks` extension is supplementary metadata,
not a reason to ignore those references. Use `placeFusion` for one shared marking
and `transitionToPlace` for an additional cross-object delivery. The retired
`placeToTransition` operation must be represented using supported composition and
local arcs rather than emitted as a legacy link.

## Validate the exported model

Run RELAX NG validation against the real grammar. In addition, check document-wide
properties that local schema rules cannot establish: ID uniqueness, endpoint scope,
reference resolution, supported extension semantics and whole-model link validity.
Round-trip a representative file through the actual consuming reader and compare
markings, weights, delays, distributions, object relationships and layout.

When a document shape changes, regenerate fixtures with the real exporter and
explain the semantic difference. Do not fix a failing schema test by merely
loosening a private schema to accept an invented element.

References: [PNML reference framework](https://www.pnml.org/),
[P/T net grammar](https://www.pnml.org/version-2009/grammar/ptnet.pntd).
