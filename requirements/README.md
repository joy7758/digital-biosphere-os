# Telemetry Admission Supply-Chain Locks

These lock files close the local `TA-T22` dependency/build control for the
DQ-018 offline reference slice. They do not authorize publication, deployment,
Collector creation, network access, or a production claim.

## Runtime lock

`telemetry-admission-runtime-py312-macos-arm64.lock` is the exact seven-package
transitive runtime closure selected for the reference environment:

```text
CPython 3.12
macOS 11 or newer
arm64
```

It is deliberately platform-scoped because the PyYAML and rpds-py wheels are
platform-specific. Using it on another platform must fail closed; create and
review a separately named lock instead of weakening hashes or claiming
cross-platform equivalence.

Install the locked dependencies, then the locally built wheel without allowing
dependency re-resolution:

```bash
python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/telemetry-admission-runtime-py312-macos-arm64.lock
python -m pip install --no-deps dist/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
python -m pip check
```

## Reproducible wheel build

The build backend and orchestration tools are exact-hash locked. Use a clean
environment, a fixed `SOURCE_DATE_EPOCH`, and no build isolation so the build
cannot silently resolve a newer backend:

```bash
python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/telemetry-admission-build.lock
SOURCE_DATE_EPOCH=1784678400 python -m build --wheel --no-isolation --outdir dist-a
SOURCE_DATE_EPOCH=1784678400 python -m build --wheel --no-isolation --outdir dist-b
shasum -a 256 dist-a/*.whl dist-b/*.whl
```

Equal hashes prove deterministic packaging only for the exact source tree,
toolchain and epoch. They do not prove source trust, vulnerability absence,
runtime correctness, interoperability or production readiness. SBOM generation,
vulnerability audit, conformance tests and Human Review remain separate gates.
