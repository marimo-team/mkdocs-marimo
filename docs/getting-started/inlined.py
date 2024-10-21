import marimo

app = marimo.App()


@app.cell
def __(mo):
    mo.md("## You can also embed marimo apps inline with mkdocs!")
    return


@app.cell
def __(mo):
    mo.md(
        f"""
        This marimo notebook was embedded inline with mkdocs, by adding the

        ```markdown
        !marimo_file {__file__}
        ```
        """
    )
    return


@app.cell
def __(mo):
    import functools

    import matplotlib.pyplot as plt
    import numpy as np

    @functools.cache
    def plotsin(amplitude, period):
        x = np.linspace(0, 2 * np.pi, 256)
        plt.plot(x, amplitude * np.sin(2 * np.pi / period * x))
        plt.ylim(-2.2, 2.2)
        return plt.gca()

    period = 2 * np.pi
    amplitude = mo.ui.slider(1, 2, step=0.1, label="Amplitude")
    amplitude
    mo.show_code(amplitude)
    return


@app.cell
def __(mo):
    mo.show_code(plotsin(amplitude.value, period))
    return


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
