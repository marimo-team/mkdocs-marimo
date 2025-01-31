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

### Embedding inline HTML components

This uses code fences to embed marimo components as [marimo islands](https://docs.marimo.io/guides/exporting/?h=#embed-marimo-outputs-in-html-using-islands).

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

### Embedding the marimo playground

For an easy way to embed marimo notebooks or applications, we recommend embedding the marimo playground. This feature uses `pymdownx.blocks` to embed marimo notebooks in your MkDocs documentation, creating iframes that render the marimo playground.

````markdown
/// marimo-embed
    height: 400px
    mode: run

```python
@app.cell
def __():
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.figure(figsize=(8, 4))
    plt.plot(x, y)
    plt.title('Sine Wave')
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.grid(True)
    plt.gca()
    return
///
````

Available options for `marimo-embed`:

- `height`: Named sizes (`small`, `medium`, `large`, `xlarge`, `xxlarge`) or custom pixel values (e.g. `500px`) (default: medium)
- `mode`: read, edit (default: read)
- `app_width`: wide, full, compact (default: wide)

You can also embed marimo files directly:

````markdown
/// marimo-embed-file
    filepath: path/to/your/file.py
    height: 400px
    mode: read
    show_source: true
///
````

Additional options for `marimo-embed-file`:

- `filepath`: path to the marimo file to embed (required)
- `show_source`: true, false (default: true) - whether to show the source code below the embed

## Examples

Checkout the [documentation](https://marimo-team.github.io/mkdocs-marimo) for more examples.

## Contributions welcome

Feel free to ask questions, enhancements and to contribute to this project!

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Credits

- Repo template from [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)
