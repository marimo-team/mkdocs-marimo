# mkdocs-marimo

MkDocs plugin that renders reactive marimo cells in Markdown docs. Published to PyPI as `mkdocs-marimo`.

## Development

Tooling is driven by [pixi](https://pixi.sh) (all tasks defined in `pixi.toml`):

```bash
pixi run postinstall           # editable install into the env
pixi run test                  # pytest
pixi run mypy mkdocs_marimo    # type check
pixi run pre-commit-run        # lint/format (ruff, taplo, typos) — matches CI lint job
pixi run docs                  # serve docs locally (pixi run docs-build to build)
```

- CI runs `test` + `mypy` across the `py39`–`py313` environments (`pixi run -e py312 test`).
- No pixi? These map to `pytest`, `mypy`, and `pre-commit run -a` under the env deps in `pixi.toml`.
