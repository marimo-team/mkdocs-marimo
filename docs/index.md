# marimo for MkDocs

[![PyPI](https://img.shields.io/pypi/v/mkdocs-marimo.svg)](https://pypi.org/project/mkdocs-marimo/)
[![License](https://img.shields.io/github/license/marimo-team/mkdocs-marimo)](https://github.com/marimo-team/mkdocs-marimo/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/marimo-team/mkdocs-marimo.svg)](https://github.com/marimo-team/mkdocs-marimo)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://marimo.io/discord)

<!-- [![Conda](https://img.shields.io/conda/v/conda-forge/mkdocs-marimo.svg)](https://anaconda.org/conda-forge/mkdocs-marimo) -->

A MkDocs plugin that brings interactive Python code execution to your documentation using [marimo](https://github.com/marimo-team/marimo).

## Features

- ⚡️ Two flexible ways to embed Python code:
  - **Inline Code**: Write and execute Python code directly in your Markdown files
  - **Playground Embed**: Embed full marimo notebooks with the marimo playground
- 🔄 Interactive widgets with real-time updates
- 📊 Seamless integration with data visualization libraries
- 🎨 Customizable styling to match your documentation theme
- 🚀 Easy to set up and use

## Quick Start

### 1. Install the plugin

=== "pip"

    ```bash
    pip install mkdocs-marimo
    ```

=== "uv"

    ```bash
    uv pip install mkdocs-marimo
    ```

=== "pixi"

    ```bash
    pixi add mkdocs-marimo
    ```

=== "conda"

    ```bash
    conda install -c conda-forge mkdocs-marimo
    ```

### 2. Add the plugin to your `mkdocs.yml`

```yaml
plugins:
  - marimo
```

### 3. Write interactive Python code in your Markdown files

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

## Example: Interactive Sine Wave

Instead of static code blocks, create interactive visualizations:

```python {marimo}
import marimo as mo
import functools
import numpy as np
import matplotlib.pyplot as plt

@functools.cache
def plotsin(amplitude, period):
    x = np.linspace(0, 2 * np.pi, 256)
    plt.plot(x, amplitude * np.sin(2 * np.pi / period * x))
    plt.ylim(-2.2, 2.2)
    return plt.gca()

period = 2 * np.pi
amplitude = mo.ui.slider(1, 2, step=0.1, label="Amplitude")
amplitude
```

```python {marimo}
plotsin(amplitude.value, period)
```

## Why mkdocs-marimo?

- **Interactive Documentation**: Engage your readers with live, interactive code examples.
- **Real-time Feedback**: Instantly see the effects of code changes and parameter adjustments.
- **Enhanced Learning**: Improve understanding through hands-on experimentation within the documentation.

## Getting Started

Check out our [Getting Started guide](getting-started/quick-start.md) to learn more about using marimo inside MkDocs.

## Community

- [GitHub Issues](https://github.com/marimo-team/mkdocs-marimo/issues): Report bugs or request features
- [Discord](https://marimo.io/discord): Ask questions and share ideas

## License

mkdocs-marimo is released under the [Apache License 2.0](https://github.com/marimo-team/mkdocs-marimo/blob/main/LICENSE).
