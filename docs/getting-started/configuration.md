# Plugin Configuration

The marimo plugin for MkDocs allows you to embed interactive marimo cells in your documentation. You can configure how these cells are rendered using various options.

## Global Configuration

You can set global configuration options for the marimo plugin in your `mkdocs.yml` file. These options serve as defaults for all marimo code blocks but can be overridden by individual code fence options.

```yaml
plugins:
  - marimo:
      enabled: true
      display_code: false
      display_output: true
      is_reactive: true
      marimo_version: '0.1.0' # Specify the version of marimo to use
```

### Available Global Options

| Option         | Type    | Description                                                                                  | Default           |
| -------------- | ------- | -------------------------------------------------------------------------------------------- | ----------------- |
| enabled        | boolean | Controls whether the marimo plugin is active.                                                | `true`            |
| display_code   | boolean | Controls whether the source code is displayed in the rendered output.                        | `false`           |
| display_output | boolean | Determines if the output of the code execution is included in the rendered HTML.             | `true`            |
| is_reactive    | boolean | Specifies whether code blocks will run with pyodide, making them interactive in the browser. | `true`            |
| marimo_version | string  | Specifies the version of marimo to use.                                                      | Installed version |

## Code Fence Options

When you create a marimo code fence in your markdown, you can specify options that control how the cell is rendered. These options are placed inside the opening code fence and will override the global configuration for that specific cell.

````markdown
```python {marimo display_code=true display_output=true is_reactive=false}
# Your marimo code here
```
````

### Available Code Fence Options

| Option         | Type    | Description                                                                                    | Example                |
| -------------- | ------- | ---------------------------------------------------------------------------------------------- | ---------------------- |
| display_code   | boolean | Controls whether the source code is displayed in the rendered output.                          | `display_code=true`    |
| display_output | boolean | Determines if the output of the code execution is included in the rendered HTML.               | `display_output=false` |
| is_reactive    | boolean | Specifies whether this code block will run with pyodide, making it interactive in the browser. | `is_reactive=false`    |

### Example

Here's an example of a marimo code fence with all options specified:

````markdown
```python {marimo display_code=true display_output=true is_reactive=false}
import marimo as mo

slider = mo.ui.slider(1, 10, value=5)
mo.md(f"Change the slider value: {slider}")
```
````

This will render a marimo cell that displays the source code and shows the output, but is not interactive in the browser (overriding the global `is_reactive` setting).

Remember that options specified in individual code fences will override the global settings for that specific cell.

## Releasing (for maintainers)

To release a new version:

1. Bump the version:

   ```bash
   hatch version patch  # or minor/major
   git add pyproject.toml
   git commit -m "chore: bump version to $(hatch version --no-color)"
   git push origin main
   ```

2. Create and push a tag:

   ```bash
   git tag $(hatch version --no-color)
   git push origin $(hatch version --no-color)
   ```

This will trigger the GitHub Actions workflow to build and publish the package to PyPI.
