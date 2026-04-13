import numpy as np
import matplotlib.patches as mpatches
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLabel
)
from PySide6.QtCore import Qt
from widgets.plot_canvas import PlotCanvas
from models.forward_prop import SimpleNetwork


class ForwardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.network = SimpleNetwork()
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # ── 왼쪽 패널 ──────────────────────────────────
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop)

        info_box = QGroupBox("Network Structure")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel("구조: 2 → 3 → 1 (고정)"))
        info_layout.addWidget(QLabel("Hidden: ReLU"))
        info_layout.addWidget(QLabel("Output: Sigmoid"))
        left.addWidget(info_box)

        self.rand_btn = QPushButton("랜덤 입력 생성")
        self.rand_btn.clicked.connect(self.on_forward)
        left.addWidget(self.rand_btn)

        self.input_label = QLabel("")
        self.input_label.setWordWrap(True)
        left.addWidget(self.input_label)

        self.output_label = QLabel("")
        left.addWidget(self.output_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # ── 오른쪽 그래프 ───────────────────────────────
        self.canvas = PlotCanvas(nrows=2, ncols=2, figsize=(10, 7))
        layout.addWidget(self.canvas)

        self.on_forward()

    def on_forward(self):
        self.network.randomize_weights()
        X = np.random.uniform(-1, 1, 2)
        self.network.forward(X)

        self.input_label.setText(f"입력: [{X[0]:.3f}, {X[1]:.3f}]")
        self.output_label.setText(f"출력: {self.network.a2[0]:.4f}")

        self.canvas.clear_all()
        axes = self.canvas.axes

        # 네트워크 다이어그램
        ax = axes[0, 0]
        ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
        ax.set_title('Network Architecture (2-3-1)')
        for i, y in enumerate([1, 3]):
            c = mpatches.Circle((0.5, y), 0.2, color='lightblue', ec='black', lw=2)
            ax.add_patch(c)
            ax.text(0.5, y, f'x{i+1}', ha='center', va='center', fontweight='bold')
        for i, y in enumerate([0.5, 2, 3.5]):
            c = mpatches.Circle((2, y), 0.2, color='lightgreen', ec='black', lw=2)
            ax.add_patch(c)
            ax.text(2, y, f'h{i+1}', ha='center', va='center', fontweight='bold')
        c = mpatches.Circle((3.5, 2), 0.2, color='lightcoral', ec='black', lw=2)
        ax.add_patch(c)
        ax.text(3.5, 2, 'y', ha='center', va='center', fontweight='bold')
        for iy in [1, 3]:
            for hy in [0.5, 2, 3.5]:
                ax.plot([0.7, 1.8], [iy, hy], 'k-', alpha=0.3, lw=1)
        for hy in [0.5, 2, 3.5]:
            ax.plot([2.2, 3.3], [hy, 2], 'k-', alpha=0.3, lw=1)

        # Layer 1 값
        ax = axes[0, 1]
        labels = [f'N{i+1}' for i in range(3)]
        pos = np.arange(3)
        w = 0.3
        ax.bar(pos - w, self.network.z1, w, label='z1 (pre-ReLU)',  color='orange', alpha=0.8)
        ax.bar(pos,     self.network.a1, w, label='a1 (post-ReLU)', color='green',  alpha=0.8)
        ax.set_title('Layer 1: z1 vs a1')
        ax.set_xticks(pos); ax.set_xticklabels(labels)
        ax.legend(); ax.grid(True, alpha=0.3)

        # Layer 2 값
        ax = axes[1, 0]
        items = ['z2 (pre-Sigmoid)', 'a2 (post-Sigmoid)']
        vals  = [self.network.z2[0], self.network.a2[0]]
        colors = ['orange', 'red']
        bars = ax.barh(items, vals, color=colors, alpha=0.8)
        for bar, val in zip(bars, vals):
            ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.4f}', va='center')
        ax.set_title('Layer 2: z2 vs a2')
        ax.grid(True, alpha=0.3)

        # 수식
        ax = axes[1, 1]
        ax.axis('off')
        ax.set_title('Forward Pass Summary')
        text = (
            f"Input X = [{X[0]:.3f}, {X[1]:.3f}]\n\n"
            f"Layer 1:\n"
            f"  z1 = X @ W1 + b1\n"
            f"  z1 = {np.round(self.network.z1, 3)}\n"
            f"  a1 = ReLU(z1)\n"
            f"  a1 = {np.round(self.network.a1, 3)}\n\n"
            f"Layer 2:\n"
            f"  z2 = a1 @ W2 + b2\n"
            f"  z2 = {self.network.z2[0]:.4f}\n"
            f"  a2 = Sigmoid(z2)\n"
            f"  a2 = {self.network.a2[0]:.4f}"
        )
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
                fontsize=9, va='top', family='monospace')

        self.canvas.draw_safe()