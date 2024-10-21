# Quick Start

This guide will help you get started with marimo for MkDocs quickly. We'll cover the basics of writing interactive Python code in your documentation.

## Prerequisites

Before you begin, make sure you have:

1. Installed the marimo plugin for MkDocs (see [Installation](installation.md))
2. Added the plugin to your `mkdocs.yml` file

## Writing Your First marimo Cell

marimo cells are special Python code blocks that can be executed interactively. Here's how to create one:

````markdown
```python {marimo}
2 + 2
```
````

By default, marimo executes the code and displays the result. On page load, marimo re-hydrates the cell state and executes the code again using WebAssembly.

## Creating Interactive Elements

Let's create a more interesting example with user input:

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
