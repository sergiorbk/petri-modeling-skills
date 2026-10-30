---
name: petri-modeling
description: Build, inspect or explain Petri net models of production and queueing systems while preserving token flow, resource capacity, time units and composed-model semantics.
---

# Model the system before drawing the net

Use this guide for a modeling request or an explanation of an existing model.
A greeting, a capability question or a request to explain theory does not by itself
authorize replacing the current net. Inspect the current model before modifying it.
Use the application's actual tools and current element identifiers; these guides do
not prescribe an API or grant additional permissions.

Identify arrivals, entities, queues, processing steps, resources, exits and the
requested measurements. Record the meaning of a token in each part of the model.
State assumptions that affect the result. Ask about a missing parameter when its
meaning changes the topology or the interpretation of the result; otherwise an
explicit reasonable default can be used.

## Token flow and resources

- Keep the P/T net bipartite. Ordinary arcs connect a place to a transition or a
  transition to a place. Connecting two queues requires a transition, or an explicit
  place-fusion operation when the two places represent one shared pool.
- A transition requiring a job and a free resource must require both at the same
  firing. Seed reusable resource places with their capacity, not with arriving jobs.
  Release each seized resource once at the appropriate completion event.
- Parallel servers drawing from one queue compete for its tokens. Connecting the
  first server's output to the second server's input makes a sequential pipeline.
  Choose the topology from the requested behavior, not from the order of tool calls.
- An unlimited queue does not imply unlimited service capacity. Service channels
  require an explicit capacity representation supported by the chosen engine.
- Timed-transition engines may hold tokens inside an in-flight transition. Include
  those tokens when checking conservation or resource occupancy; an empty visible
  busy place alone does not prove the server is idle.
- Confirm the direction of priority ordering in the target engine. A fallback
  transition must not compete probabilistically with a preferred transition that
  is supposed to win whenever it is enabled.
- Verify read and inhibitor arc capabilities before using guards. The current
  consuming engines can interpret an arc labeled inhibitor as a nonconsuming
  availability test, rather than a true zero-test. Use explicit complementary
  free-capacity or control places when the required absence test is unsupported.

## Time and distributions

Keep a consistent physical unit for all delays and the simulation horizon. When an
API accepts units explicitly, pass them with the user's numeric values. Otherwise
convert once into the engine's documented unit. Do not assume every client converts
automatically.

Distinguish a rate from a mean interval: 4 arrivals per minute corresponds to a mean
interval of 15 seconds for single arrivals. For batches, specify whether the rate
counts batches or individual items. A batch of 5 every 2 minutes has a mean item
rate of 2.5 per minute.

| Description | Suitable model | Detail to verify |
|---|---|---|
| Independent random arrivals at a stationary rate | Exponential interarrival time | Parameter may be mean interval or rate |
| Exactly every X time units | Deterministic delay | Fixed value and unit |
| Variation around a mean, with a stated standard deviation | Normal delay when physically appropriate | A stated tolerance is not automatically a standard deviation; negative-delay policy is engine-specific |
| Equally likely anywhere between a and b | Uniform delay | Some APIs take endpoints, others mean and half-range |
| Observed measurements or a specified distribution | The supplied model | Preserve the evidence instead of substituting an exponential default |

For an explicit uniform range, mean is `(a + b) / 2`, half-range is `(b - a) / 2`,
and standard deviation is `(b - a) / sqrt(12)`. Those last two parameters are not
interchangeable. Zero-time routing steps are valid, but an endlessly enabled cycle
of immediate transitions can prevent simulated time from advancing.
For distributions that can produce negative times, inspect and test the runtime's
policy. The consuming engines do not share one negative-sample policy; do not
assume automatic truncation or identical results for the same normal parameters.

## Counting without changing the system

A cumulative counter receives tokens and has no consuming transition. To count the
same completion in several counters, add output arcs from the existing completion
transition to each counter. Adding another consuming transition to the work queue
splits the stream instead of observing it. A throughput counter is cumulative;
queue length and work in progress are state measurements, not cumulative counters.

When two counters observe exactly the same event stream, their counts should agree.
If their counts merely sum to the expected total, check for competing consumers.
Account explicitly for batches, assembly, duplication, loss and in-flight work
before claiming a conservation invariant.

## Petri-objects

Use a flat net for a single linear flow unless the user chooses an object model.
Split into objects when genuinely separate subsystems interact at a small number of
interfaces, or when the user requests reusable or replicated modules.

- `placeFusion` means two place representations share one marking, for example a
  queue or resource pool. Specify that pool's initial marking consistently rather
  than counting the same capacity once per visual representation.
- `transitionToPlace` means a transition also delivers tokens into a place in a
  different object. It is not a shared queue and does not consume that place.
- The legacy `placeToTransition` link is retired in the consuming applications.
  Express cross-object consumption by fusing a local place with the shared pool,
  then drawing a local normal arc to the consuming transition. Use a local read
  arc only when the transition should test availability without consuming tokens.
- Verify the active editing object before each modification. Validate every object
  and every cross-object link, not just the currently visible subnet.

## Check the completed model

Trace one entity from arrival through each intended outcome. Check initial marking,
arc weights, capacities, probabilities, priorities, delays and time units. Inspect
rejected and reworked entities as well as successful exits. Test a small deterministic
case before interpreting stochastic statistics. A schema-valid PNML file can still
encode the wrong queue or resource policy.

Read [petri-patterns](../petri-patterns/SKILL.md) to choose a block, and
[pnml-standard](../pnml-standard/SKILL.md) before importing or exporting PNML.
Through MCP, read `petri://skills/petri-patterns` or `petri://skills/pnml-standard`.
