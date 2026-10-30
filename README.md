# petri-modeling-skills

Shared skills for building, explaining and validating Petri net models in
[Petri Net Sim](https://github.com/sergiorbk/petri-net-sim) and
[PetriObjModelPaint](https://github.com/StetsenkoInna/PetriObjModelPaint).

The package contains modeling knowledge, a catalog of block semantics and PNML
interchange guidance. It contains no simulation engine, model-building service or
application tool implementation. Application adapters provide their own tool names
and workflows without copying the shared modeling rules.

## Contents

| Resource | Purpose |
|---|---|
| `petri-modeling` | Token flow, capacities, timing, counters and composed models |
| `petri-patterns` | Choosing and connecting suitable building blocks |
| `pattern-catalog` | Arrivals, queues, service, resources, branching, assembly and transport |
| `pnml-standard` | P/T net interchange, references, extensions and validation |

`petri_modeling_skills/manifest.json` lists the allowlisted resources and package
version. Each `SKILL.md` declares its own name and description. References are
ordinary Markdown files. Those files are the shared source of truth for both
applications.

## Python

Install the package from a pinned checkout, or reference a git submodule as a local
dependency in the consuming project's package manager:

```python
from petri_modeling_skills import catalog, modeling_guidance, read_resource

resources = catalog()
guide = read_resource("petri://skills/petri-modeling")
system_prompt = modeling_guidance()
```

`catalog()` returns fresh dictionaries containing `id`, `name`, `description` and
`uri`. `read_skill(id)` and `read_resource(uri)` return Markdown without skill
frontmatter. Unknown IDs, arbitrary filesystem paths and noncanonical URIs are
rejected with `KeyError`. Loading uses Python package resources and works from an
installed wheel without the source checkout.

## Java and other clients

Pin this repository as a git submodule. Package `manifest.json`, `skills/**/*.md`,
`LICENSE` and `NOTICE` as nonfiltered application resources during the build. A
small loader reads the manifest and returns only its listed resource IDs. No
Python interpreter is required to load the Markdown in Java.

An MCP adapter can expose each catalog entry at `petri://skills/{id}`, and include
the selected text in a modeling prompt. Read the modeling guide first, then load
pattern or PNML details when the task needs them. An application using a cached
system prompt can load all guides with `modeling_guidance()`.

## Updates and checks

Both applications should point to the same reviewed commit of this repository.
Update the submodule pin deliberately and rebuild the application; runtime loading
does not fetch mutable remote instructions. CI checkouts must initialize submodules,
and Docker build contexts must include the pinned source before dependency install.

Run the loader tests with `python -m unittest discover -s tests`. Build a wheel with
`python -m build` or `uv build`. Test the consuming applications' resource and prompt
adapters after a content update. The skill folders can also be installed as standard
`SKILL.md` skills using a client's normal skill mechanism.

## License and provenance

The source material was extracted and adapted from Petri Net Sim's modeling prompt,
pattern documentation and PNML guide. It remains under the original PolyForm
Noncommercial License 1.0.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
