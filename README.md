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
| `petri-training-export` | Auditable ZIP exports with real session evidence for LLM training |
| `petri-image-reconstruction` | Interpret a supplied net photo or diagram and rebuild its observed graph through available application tools |
| `petri-training-review` | Review exact model revisions and interpret recorded simulation trajectories |

`petri_modeling_skills/manifest.json` lists the allowlisted resources and package
version. Each `SKILL.md` declares its own name and description. References are
ordinary Markdown files. Those files are the shared source of truth for both
applications.

## Python

Install the versioned wheel from GitHub Releases. Consumers pin the release URL
and SHA-256 in their dependency configuration and lockfile; no PyPI account or
Git submodule is needed:

```bash
pip install https://github.com/sergiorbk/petri-modeling-skills/releases/download/v0.4.0/petri_modeling_skills-0.4.0-py3-none-any.whl
```

Use the installed package normally:

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

`read_schema("training-bundle")` returns the canonical JSON schema for training ZIP
manifests and their individual JSON artifacts. Schemas have their own manifest
allowlist and are not concatenated into modeling guidance as if they were Markdown.
`read_schema("petri-image-observation")` provides an optional intermediate format for
visual observations, local IDs, layout transforms and explicit uncertainties. The
external vision client performs recognition; this package adds no OCR dependency or
image-upload service. The observation schema does not alter the training ZIP contract.

`read_schema("training-history")` describes revision chains, review findings and
execution evidence, including sampled tokens and active transition channels.

## Java and other clients

Download `petri-modeling-skills-0.4.0-resources.zip` from the same GitHub Release
and verify its pinned SHA-256 before extraction. The archive contains
`petri-modeling-skills/manifest.json`, `skills/**/*.md`, `schemas/**/*.json`,
`LICENSE` and `NOTICE`. Maven can fetch and unpack it during generate-resources
and include that directory as nonfiltered JAR resources. A small loader reads
the manifest and returns only its listed resource IDs. Java consumers need no
Python interpreter or Git submodule.

An MCP adapter can expose each catalog entry at `petri://skills/{id}`, and include
the selected text in a modeling prompt. Read the modeling guide first, then load
pattern or PNML details when the task needs them. An application using a cached
system prompt can load all guides with `modeling_guidance()`.

## Updates and checks

Both applications should use the same reviewed package version. Update the
release URL and SHA-256 deliberately and rebuild; runtime loading does not fetch
remote instructions. Plain Git checkouts and ordinary build commands are enough.
The release files must exist before merging consumer dependency updates.

Install the optional `test` extra for schema validation, then run
`python -m unittest discover -s tests`. Build a wheel with
`python -m build` or `uv build`. To produce the files used by both applications,
run `python scripts/build_release_assets.py` with uv installed. The script
normalizes text line endings and creates a repeatable wheel, resource ZIP, source
archive and SHA256SUMS.txt. The Build release assets workflow can be run manually
to review downloadable artifacts; it only attaches files after an existing GitHub
Release is published and never creates a release or tag. Test the consuming applications' resource and prompt
adapters after a content update. The skill folders can also be installed as standard
`SKILL.md` skills using a client's normal skill mechanism.

## License and provenance

The source material was extracted and adapted from Petri Net Sim's modeling prompt,
pattern documentation and PNML guide. It remains under the original PolyForm
Noncommercial License 1.0.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
