# MkDocs marimo Plugin

> [!WARNING]
> The MkDocs marimo plugin is under active development. Features and documentation are being continuously updated and expanded.

This plugin allows you to embed interactive [marimo](https://github.com/marimo-team/marimo) notebooks in your MkDocs documentation.

## Installation

```bash
# pip
pip install mkdocs-marimo
# uv
uv pip install mkdocs-marimo
# pixi
pixi add mkdocs-marimo
```

## Usage

Create reactive and interactive Python blocks in your markdown files using [marimo](https://github.com/marimo-team/marimo).

````markdown
```python {marimo}
import marimo as mo

name = mo.ui.text(placeholder="Enter your name")
name
```

```python {marimo}
mo.md(f"Hello, **{name.value or '__'}**!")
```
````

Checkout the [documentation](https://marimo-team.github.io/mkdocs-marimo) for more examples.

## Contributions welcome

Feel free to ask questions, enhancements and to contribute to this project!

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Credits

- Repo template from [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)
