# Embedding marimo Notebooks with the Playground

This guide covers the second approach to using marimo in your documentation: embedding full marimo notebooks using the marimo playground, [like in our own documentation](https://docs.marimo.io/api/inputs/button/). This approach is ideal when you want to:

- Show complete, multi-cell notebooks
- Allow users to edit and experiment with the code
- Embed existing .py notebooks

If you're looking for simpler, inline code examples, check out the [Quick Start](quick-start.md) guide's section on inline code.

This feature uses `pymdownx.blocks` to embed marimo notebooks in your MkDocs documentation, creating iframes that render the marimo playground.

## Setup

To use the marimo playground, you need to install the `pymdown-extensions` package.

```bash
pip install mkdocs-marimo pymdown-extensions
```

## Basic Example

Here's a simple example of embedding a marimo notebook using blocks:

````markdown
/// marimo-embed
    height: 400px
    mode: read
    app_width: wide

```python
@app.cell
def __():
    import marimo as mo

    name = mo.ui.text(placeholder="Enter your name", debounce=False)
    name
    return

@app.cell
def __():
    mo.md(f"Hello, **{name.value or '__'}**!")
    return
```

///
````

/// marimo-embed
    height: 400px
    mode: read
    app_width: wide

```python
@app.cell
def __():
    import marimo as mo

    name = mo.ui.text(placeholder="Enter your name", debounce=False)
    name
    return

@app.cell
def __():
    mo.md(f"Hello, **{name.value or '__'}**!")
    return
```

///

## Interactive Plot Example

Here's an example with an interactive plot:

````markdown
/// marimo-embed
    height: 800px
    mode: read
    app_width: wide

```python
@app.cell
def __():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    # Create interactive sliders
    freq = mo.ui.slider(1, 10, value=2, label="Frequency")
    amp = mo.ui.slider(0.1, 2, value=1, label="Amplitude")

    mo.hstack([freq, amp])
    return

@app.cell
def __():
    # Plot the sine wave
    x = np.linspace(0, 10, 1000)
    y = amp.value * np.sin(freq.value * x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title('Interactive Sine Wave')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.gca()
    return
```

///
````

/// marimo-embed
    height: 800px
    mode: read
    app_width: wide

```python
@app.cell
def __():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    # Create interactive sliders
    freq = mo.ui.slider(1, 10, value=2, label="Frequency")
    amp = mo.ui.slider(0.1, 2, value=1, label="Amplitude")

    mo.hstack([freq, amp])
    return

@app.cell
def __():
    # Plot the sine wave
    x = np.linspace(0, 10, 1000)
    y = amp.value * np.sin(freq.value * x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title('Interactive Sine Wave')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.gca()
    return
```

///

## Example with Hidden Code

Here's an example that hides the code:

/// marimo-embed
    height: 400px
    mode: read
    app_width: wide
    include_code: false

```python
@app.cell
def __():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plt.plot(x, y)
    plt.title('Simple Sine Wave')
    plt.gca()
    return
```

///

## Configuration Options

### marimo-embed

| Option | Description | Values |
| --- | --- | --- |
| `height` | Controls the height of the embed | - Named sizes: `small` (300px), `medium` (400px), `large` (600px),<br> `xlarge` (800px), `xxlarge` (1000px)<br>- Custom size: Any pixel value (e.g. `500px`) |
| `mode` | Controls the interaction mode | - `read`: Read-only view (default)<br>- `edit`: Allows editing the code |
| `app_width` | Controls the width of the marimo app | - `wide`: Standard width (default)<br>- `full`: Full width<br>- `compact`: Narrow width |
| `include_code` | Controls whether code is included in the embed | - `true`: Show code (default)<br>- `false`: Hide code |

### marimo-embed-file

The `marimo-embed-file` block is used to embed existing marimo files:

/// marimo-embed-file
    filepath: getting-started/inlined.py
    height: 600px
    mode: read
    show_source: true
///

| Option | Description | Default |
| --- | --- | --- |
| `filepath` | Path to the marimo file to embed | Required |
| `show_source` | Whether to show the source code below the embed | `true` |
| `include_code` | Controls whether code is included in the embed | `true` |
