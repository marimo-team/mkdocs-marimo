# Quick Start

This guide will help you get started with using marimo inside MkDocs. There are two main ways to use marimo in your documentation:

1. **Inline Code**: Write Python code directly in your Markdown files using marimo islands
2. **Playground Embed**: Embed full marimo notebooks using the marimo playground

## Prerequisites

Before you begin, make sure you have:

1. Installed the marimo plugin for MkDocs (see [Installation](installation.md))
2. Added the plugin to your `mkdocs.yml` file

## Approach 1: Inline Code with marimo Islands

This is the simplest way to add interactive Python code to your documentation. Code is written directly in your Markdown files and executed in place.

### Basic Example

````markdown
```python {marimo}
2 + 2
```
````

By default, marimo executes the code and displays the result. On page load, marimo re-hydrates the cell state and executes the code again using WebAssembly.

### Interactive Elements

````markdown
```python {marimo}
import marimo as mo
name = mo.ui.text(placeholder="Enter your name", debounce=False)
name
```

```python {marimo}
mo.md(f"Hello, **{name.value or '__'}**!")
```
````

This produces:

```python {marimo}
import marimo as mo
name = mo.ui.text(placeholder="Enter your name", debounce=False)
name
```

```python {marimo}
mo.md(f"Hello, **{name.value or '__'}**!")
```

## Approach 2: Embedding the marimo Playground

For more complex notebooks or when you want to provide a full notebook experience, you can embed the marimo playground. This approach requires the `pymdown-extensions` package.

```bash
pip install pymdown-extensions
```

### Basic Playground Example

````markdown
/// marimo-embed
    height: 400px
    mode: read
    app_width: medium

```python
@app.cell
def __():
    import marimo as mo
    name = mo.ui.text(placeholder="Enter your name")
    name
    return

@app.cell
def __():
    mo.md(f"Hello, **{name.value or '__'}**!")
    return
```

///
````

See [Embedding the marimo playground](blocks.md) for more details on this approach.

## Which Approach Should You Choose?

Use **Inline Code** when:

- You want to show simple, focused examples

Use **Playground Embed** when:

- You want to show complete notebooks
- You want users to be able to edit and experiment with the code
- You want to embed existing .py notebooks

## Working with Data

marimo integrates seamlessly with data analysis libraries. Here's an example using pandas:

````markdown
```python {marimo}
import marimo as mo
import pandas as pd
data = pd.read_csv("https://huggingface.co/datasets/scikit-learn/Fish/resolve/main/Fish.csv")
mo.ui.table(data, selection=None)
```
````

```python {marimo}
import pandas as pd
data = pd.read_csv("https://huggingface.co/datasets/scikit-learn/Fish/resolve/main/Fish.csv")
mo.ui.table(data, selection=None)
```

## Leveraging Reactivity

marimo's reactivity allows cells to update automatically when inputs or code changes. Here's a visualization example:

```python {marimo display_code}
import functools
import numpy as np
import matplotlib.pyplot as plt

@functools.cache
def plotsin(amplitude, period):
    # You can edit this code!
    x = np.linspace(0, 2 * np.pi, 256)
    plt.plot(x, amplitude * np.sin(2 * np.pi / period * x))
    plt.ylim(-2.2, 2.2)
    return plt.gca()

period = 2 * np.pi
amplitude = mo.ui.slider(1, 2, step=0.1); amplitude
```

```python {marimo display_code}
plotsin(amplitude.value, period)
```
