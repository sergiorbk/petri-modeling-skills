# Petri modeling pattern catalog

## Arrivals, storage and exits

| Block | Meaning | Modeling check |
|---|---|---|
| Generator | Creates arriving jobs after interarrival delays | Distinguish item rate, batch rate and delay distribution; define the first-arrival policy |
| Nonstationary generator | Changes arrival behavior over time windows | Define window units, boundary behavior and what happens outside the schedule |
| Buffer | Stores waiting jobs | A bare place is normally unbounded; capacity or FIFO order requires additional supported semantics |
| Terminator | Removes a job from the active flow and records a completed outcome | One exit per intended outcome; do not attach competing exits merely to count the same event twice |
| Finite population | A fixed population circulates through service and a return or thinking phase | Seed the finite population once; an unrestricted external generator changes the model into an open system |

## Service and reusable resources

| Block | Meaning | Modeling check |
|---|---|---|
| Machine or server | Waits for a job and a free service channel, processes it, then releases the channel | Seed c free-channel tokens for c simultaneous jobs; include in-flight work when checking capacity |
| Parallel servers from one queue | Several service choices consume from one shared queue | The servers compete for jobs; they are not a chain of sequential operations |
| Multi-resource operation | Requires all specified resource pools simultaneously | Use an AND precondition and return every seized resource on completion |
| Alternative resource set | Uses one available resource from a set of alternatives | This is an OR choice; requiring every resource would reduce capacity incorrectly |
| Setup machine | Adds a mandatory setup or changeover phase | Specify whether setup occurs per item, per batch or only after a product change |
| Breakdown and repair | Resource availability is interrupted by failure and recovery | State whether work resumes, restarts or is discarded and whether the resource remains seized |
| Preemptive machine | Higher-priority work interrupts lower-priority work | Specify resume versus restart semantics; transition priority alone may only affect selection before service starts |
| Scheduled availability | Makes a resource available according to a cyclic work schedule | Decide what happens to work in service at an off-duty boundary |
| Threshold activation | An additional service channel engages when queue length exceeds N | "More than N" means at least N+1; processing one job must not consume all N+1 jobs |
| Server vacation or N-policy | A sleeping server wakes after N jobs accumulate | Define the rule for returning to sleep and distinguish a persistent active period from one threshold-triggered job |
| WIP controller | Limits the number of entities admitted to a subsystem | Consume an admission permit on entry and return it at the subsystem's actual exit |

## Finite queues and loss policies

These policies are different behaviors. Clarify which the system requires.

- **Bounded queue with rejection:** arriving jobs are rejected when waiting capacity
  is exhausted. A complementary free-slots place starts with K tokens. Enqueue
  consumes a slot; every dequeue returns one. Connect that return to the actual
  consumer, including every parallel consumer. For waiting-only capacity, return
  the slot when service starts, not when service completes. For capacity that
  includes jobs in service, release the permit at the modeled system exit.
  Specify which of those meanings K has. A bare P/T place does not enforce FIFO order
  among distinguishable jobs.
- **Blocking machine:** a completed job cannot be handed off while the downstream
  buffer is full. Specify whether the job continues occupying the machine during
  this wait. Replacing blocking with rejection changes throughput and utilization.
- **Balking:** a new arrival decides not to join a queue based on its observed
  length or another admission condition. The customer leaves before waiting.
- **Reneging:** an admitted customer abandons after a patience delay. Ensure service
  and timeout do not both complete for the same customer. Individual patience may
  require more information than an uncolored aggregate P/T marking can express.
- **Retrial queue:** a busy arrival enters an orbit and retries after a delay. It
  stays part of the system until eventual service or an explicitly modeled loss.
  A retry is not a fresh external arrival.

## Routing, synchronization and token multiplicity

| Block | Meaning | Modeling check |
|---|---|---|
| Router | Chooses one outgoing branch by probability or priority | Probabilities belong to enabled competing choices and should sum to one under the API's convention; different guards or resources can change overall observed percentages |
| Quality check | Routes a processed item to pass or fail | A defect fraction of 0.04 means pass probability 0.96; define the destination of failed items |
| Priority choice | Uses a preferred feasible route, otherwise a fallback | Verify which priority value wins in the engine and ensure the preferred route's resource preconditions are explicit |
| Merge | Forwards a job from any of several incoming streams | An OR merge does not wait for one token from every branch |
| Assembly | Consumes required components from every input and produces an assembled unit | Input arc weights encode the bill of materials, so item counts change unit at the output |
| Duplicate | Produces a token on each output for one input event | This is broadcast, not a probabilistic split; conservation must account for the copies |
| Fork-join | Starts parallel work and waits for all required branches | An AND join synchronizes; an OR merge does not. Preserve job correlation if more than one job can overlap |
| Batch | Collects N individual tokens and emits one batch token | Use a weight-N input to the release transition; the output token represents N items |
| Unbatch | Turns one batch token into N individual output tokens | Confirm the expected batch size and use a weight-N output |
| Timed batch | Releases on count threshold or timeout | Specify whether the timeout emits a partial batch and how its actual size is represented |
| Rework or feedback loop | Sends failed items back for another processing attempt | Specify attempt limits, repeated inspection and a final loss path; avoid a zero-time endless loop |
| Read or controller connection | Tests the availability of a marking without consuming it | Use the engine's actual read-arc semantics; a normal consuming arc can steal the observed resource |

## Conveyors and transport

- **Sequential conveyor:** items pass through the required stations with travel time
  between them. State whether stations have waiting buffers or can block the belt.
- **Try-or-bypass workstation:** process if its resource is available, otherwise send
  the item to the next station. The feasible processing transition has precedence
  over the bypass. Random branch probabilities do not implement this rule.
- **Conveyor line with recirculation:** repeated try-or-bypass stations followed by a
  return path. Specify whether processed items leave immediately, how long the
  return takes, and whether the circulating carrier is itself a limited resource.
- **Cyclic transport resource:** a robot, forklift or vehicle seizes an item, travels,
  releases it and returns. Keep the transport resource unavailable for every phase
  required before it can take the next job.

## Small reference scenarios

**One random-arrival server:** mean interarrival 40 s, mean service 30 s, one channel,
both exponential. Connect arrival to the service queue and completion to one exit.
The offered load is 30/40 = 0.75; this is a diagnostic check, not a replacement for
simulation or a guarantee about finite-run results.

**Two different machines sharing work:** both consume the same queue, with separate
resource capacities and service delays. Route each completion to the intended
quality check, then merge successful output if appropriate. Separate queues would
require an explicit routing policy; sequential connection would require each item
to visit both machines.

**Assembly with 10 parts of each kind:** the assembly transition requires weight 10
from each of the two component pools. One output token represents one assembled
unit. If an empty carrier must move on when components are unavailable, add a
lower-precedence fallback that consumes the carrier without consuming components.
