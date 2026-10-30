---
name: petri-patterns
description: Choose and connect Petri net building blocks for arrivals, service, queues, routing, assembly, transport, resource constraints and rework.
---

# Choose blocks by behavior

Read the [pattern catalog](references/pattern-catalog.md) when selecting or composing
blocks. It is also available as the resource `petri://skills/pattern-catalog`.
The catalog describes semantics, not a promise that a particular client has a tool
for every block. Inspect the client's available tools or build an equivalent net
from its supported primitives.

Establish each block's input, output, resource ports and loss or bypass outputs
before wiring it. Use identifiers returned by the application, or names it has
explicitly resolved. Refresh those references after operations that merge places
or replace the model. Automatic sequential connection is an application feature,
not a rule of Petri nets; disable or correct it for parallel and branching flows.

Keep job tokens, batch tokens, resource tokens and control tokens distinct in the
model description. Document where a block changes the token unit. Connect rejection,
bypass and rework outputs deliberately rather than leaving a plausible-looking
main path and losing the exceptional flow.

Before substituting a simpler block, compare its enabling condition, seized
resources, timing, output multiplicity and fallback behavior with the requested
system. A probability router cannot implement "use this machine if it is free,
otherwise bypass", and an ordinary unlimited buffer cannot implement a finite
waiting room with loss.
