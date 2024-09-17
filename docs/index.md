---
title: Home
---

# marimo in mkdocs

This is a mkdocs plugin that allows you to write marimo code fences in your markdown files. Create interactive documentation with ease!

## Example

```python
data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
```

```marimo
import marimo as mo
data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
```

And now we can display it as a table:

```marimo
mo.ui.table(data)
```
