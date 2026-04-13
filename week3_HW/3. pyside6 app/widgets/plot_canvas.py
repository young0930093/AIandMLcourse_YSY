import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, nrows=1, ncols=1, figsize=(8, 6)):
        self.fig, self.axes = plt.subplots(nrows, ncols, figsize=figsize)
        super().__init__(self.fig)
        self.setParent(parent)

    def get_ax(self, row=0, col=0):
        if isinstance(self.axes, np.ndarray):
            if self.axes.ndim == 1:
                return self.axes[max(row, col)]
            return self.axes[row, col]
        return self.axes

    def clear_all(self):
        if isinstance(self.axes, np.ndarray):
            for ax in self.axes.flat:
                ax.clear()
        else:
            self.axes.clear()

    def draw_safe(self):
        self.fig.tight_layout()
        self.draw()