from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """재사용 가능한 matplotlib PySide6 임베딩 위젯."""

    def __init__(self, nrows=1, ncols=1, figsize=(10, 6)):
        self.fig = Figure(figsize=figsize)
        self.axes = self.fig.subplots(nrows, ncols)
        super().__init__(self.fig)
        self.fig.tight_layout()
