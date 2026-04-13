import pytest
import sys
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope='module')
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    return app

def test_mplcanvas_single_axes(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=1, ncols=1)
    # axes가 단일 Axes 객체여야 함
    assert hasattr(canvas.axes, 'plot')

def test_mplcanvas_multi_axes(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=2, ncols=3)
    # axes가 2x3 배열이어야 함
    assert canvas.axes.shape == (2, 3)

def test_mplcanvas_fig_exists(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=1, ncols=2)
    assert canvas.fig is not None
