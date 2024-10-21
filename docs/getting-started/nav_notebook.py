import marimo

app = marimo.App()


@app.cell
def __(mo):
    mo.md("""
    ## You can link directly to marimo notebooks, in the mkdocs.yml file.

    This content comes from a marimo notebook.
    """)
    return


@app.cell
def __(mo):
    mo.md(
        """
        ```markdown
        nav:
            Examples:
                - Simple: simple_example.py
                - Complex: complex_example.py
        ```
        """
    )
    return


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
