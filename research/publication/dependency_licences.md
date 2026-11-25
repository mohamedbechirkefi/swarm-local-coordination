<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Generated in M6 from installed metadata: Python from the `.venv` created by `uv sync --frozen --all-groups --all-extras` (`importlib.metadata`: `License-Expression`, else the licence classifiers), npm from `demo/node_modules/*/package.json` after `npm ci --prefer-offline`. Third-party packages keep their own licences; none is vendored into this repository.

Accepted as permissive: MIT (including MIT-CMU), BSD, ISC, Apache-2.0, PSF, MPL-2.0, 0BSD, Zlib, CC0-1.0.

## Flags

- **pandoc 3.6.3 (build tool, not a dependency of the package).** Pandoc is published under GPL-2.0-or-later (its published licence, not re-read in M6; the binary's `--version` prints only the copyright line and states that it is free software). It is used as an external program to convert Markdown to Typst and LaTeX; it is not linked, imported or redistributed, and the generated documents are not derived from its code. Flagged for the owner's information only.
- **MPL-2.0 packages** (`hypothesis`, development only; `lightningcss` and `lightningcss-darwin-arm64`, build only through Vite): weak copyleft at file level, applying only if their files are modified and distributed. Neither happens here. Listed as permissive under the brief's list.
- **`pillow` (MIT-CMU)**: an MIT-style permissive licence (Historical Permission Notice variant).
- **`swarm-local-coordination` 0.1.0**: this project, licence `LicenseRef-SWARM-NC-Research-1.0` (custom, source-available, see `LICENSE`); the metadata field is empty because the licence is not on the SPDX list.
- **`hatchling` (build backend in `pyproject.toml`)**: not installed in `.venv`, so its licence was not read from metadata here; it is used only when building a wheel, which this project does not distribute.
- Nothing outside the accepted list was found among the installed packages.

## Toolchain outside the lockfiles

| tool | version | licence | source of the licence statement | role |
| --- | --- | --- | --- | --- |
| pandoc | 3.6.3 | GPL-2.0-or-later | published licence, not verified from the binary in M6 | Markdown to Typst and LaTeX (build) |
| typst (Python package) | 0.15.0 | Apache-2.0 | installed metadata | PDF compilation (build) |
| pypdf | 6.20.0 | BSD-3-Clause | installed metadata | PDF metadata check (M6 verification only) |
| uv | 0.9.5 | not read from metadata in M6 | none | environment manager (build) |
| Node.js | v22.23.3 | not read from metadata in M6 | none | demo build and tests (build) |

## Python (24 installed distributions)

| package | version | licence (metadata) | role | flag |
| --- | --- | --- | --- | --- |
| attrs | 26.1.0 | MIT | runtime | permissive |
| contourpy | 1.4.0 | BSD-3-Clause | runtime | permissive |
| cycler | 0.12.1 | BSD License | runtime | permissive |
| fonttools | 4.68.0 | MIT | runtime | permissive |
| hypothesis | 6.170.15 | MPL-2.0 | development | permissive |
| iniconfig | 2.3.1 | MIT | development | permissive |
| jsonschema | 4.26.0 | MIT | runtime | permissive |
| jsonschema-specifications | 2025.9.1 | MIT | runtime | permissive |
| kiwisolver | 1.5.1 | BSD License | runtime | permissive |
| matplotlib | 3.11.2 | Python Software Foundation License | runtime | permissive |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime | permissive |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | runtime | permissive |
| pillow | 13.0.0 | MIT-CMU | runtime | permissive |
| pluggy | 1.7.0 | MIT License | development | permissive |
| Pygments | 2.21.0 | BSD-2-Clause | development | permissive |
| pyparsing | 3.3.3 | MIT | runtime | permissive |
| pytest | 9.2.0 | MIT | development | permissive |
| python-dateutil | 4.0.0 | BSD-3-Clause | runtime | permissive |
| referencing | 0.37.0 | MIT | runtime | permissive |
| rpds-py | 2026.9.1 | MIT | runtime | permissive |
| sortedcontainers | 2.4.0 | Apache Software License | development | permissive |
| swarm-local-coordination | 0.1.0 | UNKNOWN | this project | project |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime (indirect) | permissive |
| tzdata | 2026.6 | Apache-2.0 | runtime (indirect) | permissive |

## npm, demo (`demo/node_modules`, 53 packages)

`react` and `react-dom` are bundled into the static page (runtime); every other package is a build or test tool.

| package | version | licence (package.json) | role | flag |
| --- | --- | --- | --- | --- |
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | build/test | permissive |
| @oxc-project/types | 0.156.0 | MIT | build/test | permissive |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | build/test | permissive |
| @rolldown/pluginutils | 1.1.1 | MIT | build/test | permissive |
| @standard-schema/spec | 1.1.0 | MIT | build/test | permissive |
| @types/chai | 5.2.3 | MIT | build/test | permissive |
| @types/deep-eql | 4.0.2 | MIT | build/test | permissive |
| @types/estree | 1.0.11 | MIT | build/test | permissive |
| @types/react | 19.3.0 | MIT | build/test | permissive |
| @types/react-dom | 19.3.0 | MIT | build/test | permissive |
| @vitejs/plugin-react | 6.1.2 | MIT | build/test | permissive |
| @vitest/expect | 4.1.12 | MIT | build/test | permissive |
| @vitest/mocker | 4.1.12 | MIT | build/test | permissive |
| @vitest/pretty-format | 4.1.12 | MIT | build/test | permissive |
| @vitest/runner | 4.1.12 | MIT | build/test | permissive |
| @vitest/snapshot | 4.1.12 | MIT | build/test | permissive |
| @vitest/spy | 4.1.12 | MIT | build/test | permissive |
| @vitest/utils | 4.1.12 | MIT | build/test | permissive |
| assertion-error | 2.0.1 | MIT | build/test | permissive |
| chai | 6.3.0 | MIT | build/test | permissive |
| convert-source-map | 2.0.0 | MIT | build/test | permissive |
| csstype | 3.2.4 | MIT | build/test | permissive |
| detect-libc | 2.1.2 | Apache-2.0 | build/test | permissive |
| es-module-lexer | 2.3.2 | MIT | build/test | permissive |
| estree-walker | 3.0.3 | MIT | build/test | permissive |
| expect-type | 1.4.0 | Apache-2.0 | build/test | permissive |
| fdir | 6.5.0 | MIT | build/test | permissive |
| fsevents | 2.3.3 | MIT | build/test | permissive |
| lightningcss | 1.33.0 | MPL-2.0 | build/test | permissive |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | build/test | permissive |
| magic-string | 0.30.21 | MIT | build/test | permissive |
| nanoid | 3.3.20 | MIT | build/test | permissive |
| obug | 2.2.1 | MIT | build/test | permissive |
| pathe | 2.0.3 | MIT | build/test | permissive |
| picocolors | 1.1.1 | ISC | build/test | permissive |
| picomatch | 4.0.7 | MIT | build/test | permissive |
| postcss | 8.5.33 | MIT | build/test | permissive |
| react | 19.3.1 | MIT | runtime (bundled) | permissive |
| react-dom | 19.3.1 | MIT | runtime (bundled) | permissive |
| rolldown | 1.2.19 | MIT | build/test | permissive |
| scheduler | 0.28.0 | MIT | runtime (bundled) | permissive |
| siginfo | 2.0.0 | ISC | build/test | permissive |
| source-map-js | 1.2.4 | BSD-3-Clause | build/test | permissive |
| stackback | 0.0.2 | MIT | build/test | permissive |
| std-env | 4.3.0 | MIT | build/test | permissive |
| tinybench | 2.9.0 | MIT | build/test | permissive |
| tinyexec | 1.4.0 | MIT | build/test | permissive |
| tinyglobby | 0.2.17 | MIT | build/test | permissive |
| tinyrainbow | 3.2.0 | MIT | build/test | permissive |
| typescript | 5.9.3 | Apache-2.0 | build/test | permissive |
| vite | 8.3.5 | MIT | build/test | permissive |
| vitest | 4.1.12 | MIT | build/test | permissive |
| why-is-node-running | 2.3.0 | MIT | build/test | permissive |
