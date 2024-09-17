# Quick Start

After you [installed](installation.md) the plugin, you can write marimo code fences in your markdown files.

## Example

````markdown
```marimo
import marimo as mo
data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
mo.ui.table(data, selection=None)
```
````

This would produce an interactive table in your MkDocs documentation, powered by marimo.

```marimo
import marimo as mo
data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
mo.ui.table(data, selection=None)
```
