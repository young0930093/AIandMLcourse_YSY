import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QSlider, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from widgets.plot_canvas import PlotCanvas
from models.activations import get_all


class ActivationTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # ── 왼쪽 패널 ──────────────────────────────────
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop)

        # x 범위
        range_box = QGroupBox("X Range")
        range_layout = QVBoxLayout(range_box)
        self.range_slider = QSlider(Qt.Horizontal)
        self.range_slider.setRange(1, 10)
        self.range_slider.setValue(5)
        self.range_label = QLabel("±5")
        self.range_slider.valueChanged.connect(self._on_update)
        range_layout.addWidget(self.range_slider)
        range_layout.addWidget(self.range_label)
        left.addWidget(range_box)

        # Leaky ReLU alpha
        alpha_box = QGroupBox("Leaky ReLU Alpha")
        alpha_layout = QVBoxLayout(alpha_box)
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.001, 0.1)
        self.alpha_spin.setSingleStep(0.001)
        self.alpha_spin.setDecimals(3)
        self.alpha_spin.setValue(0.01)
        self.alpha_spin.valueChanged.connect(self._on_update)
        alpha_layout.addWidget(self.alpha_spin)
        left.addWidget(alpha_box)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # ── 오른쪽 그래프 ───────────────────────────────
        self.canvas = PlotCanvas(nrows=2, ncols=2, figsize=(10, 7))
        layout.addWidget(self.canvas)

        self._on_update()

    def _on_update(self):
        r = self.range_slider.value()
        self.range_label.setText(f"±{r}")
        alpha = self.alpha_spin.value()
        x = np.linspace(-r, r, 300)
        d = get_all(x, alpha)

        self.canvas.clear_all()
        axes = self.canvas.axes

        # 함수 비교
        ax = axes[0, 0]
        ax.plot(x, d['sigmoid'],    label='Sigmoid', linewidth=2)
        ax.plot(x, d['tanh'],       label='Tanh',    linewidth=2)
        ax.plot(x, d['relu'],       label='ReLU',    linewidth=2)
        ax.plot(x, d['leaky_relu'], label='Leaky ReLU', linewidth=2, linestyle='--')
        ax.axhline(0, color='k', alpha=0.3)
        ax.axvline(0, color='k', alpha=0.3)
        ax.set_title('Activation Functions')
        ax.legend(); ax.grid(True, alpha=0.3)

        # 미분 비교
        ax = axes[0, 1]
        ax.plot(x, d['sigmoid_grad'],    label="Sigmoid'",    linewidth=2)
        ax.plot(x, d['tanh_grad'],       label="Tanh'",       linewidth=2)
        ax.plot(x, d['relu_grad'],       label="ReLU'",       linewidth=2)
        ax.plot(x, d['leaky_relu_grad'], label="Leaky ReLU'", linewidth=2, linestyle='--')
        ax.axhline(0, color='k', alpha=0.3)
        ax.set_title('Derivatives (Gradients)')
        ax.legend(); ax.grid(True, alpha=0.3)

        # Sigmoid vs Tanh
        ax = axes[1, 0]
        ax.plot(x, d['sigmoid'], label='Sigmoid: (0,1)', linewidth=3)
        ax.plot(x, d['tanh'],    label='Tanh: (-1,1)',   linewidth=3)
        ax.axhline(0, color='k', alpha=0.3)
        ax.set_title('Sigmoid vs Tanh')
        ax.legend(); ax.grid(True, alpha=0.3)

        # ReLU vs Leaky ReLU
        ax = axes[1, 1]
        ax.plot(x, d['relu'],       label='ReLU',       linewidth=3)
        ax.plot(x, d['leaky_relu'], label='Leaky ReLU', linewidth=3)
        ax.axhline(0, color='k', alpha=0.3)
        ax.set_title('ReLU vs Leaky ReLU')
        ax.legend(); ax.grid(True, alpha=0.3)

        self.canvas.draw_safe()