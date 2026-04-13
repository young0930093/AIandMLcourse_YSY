import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt
from widgets.plot_canvas import PlotCanvas
from models.perceptron import Perceptron


X_DATA = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
GATES = {
    'AND': np.array([0, 0, 0, 1]),
    'OR':  np.array([0, 1, 1, 1]),
    'XOR': np.array([0, 1, 1, 0]),
}


class PerceptronTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # ── 왼쪽 패널 ──────────────────────────────────
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop)

        # 게이트 선택
        gate_box = QGroupBox("Gate Type")
        gate_layout = QVBoxLayout(gate_box)
        self.gate_group = QButtonGroup(self)
        for i, name in enumerate(['AND', 'OR', 'XOR']):
            rb = QRadioButton(name)
            if i == 0:
                rb.setChecked(True)
            self.gate_group.addButton(rb, i)
            gate_layout.addWidget(rb)
        left.addWidget(gate_box)

        # 학습률
        lr_box = QGroupBox("Learning Rate (η)")
        lr_layout = QVBoxLayout(lr_box)
        self.lr_slider = QSlider(Qt.Horizontal)
        self.lr_slider.setRange(1, 100)
        self.lr_slider.setValue(10)
        self.lr_label = QLabel("0.10")
        self.lr_slider.valueChanged.connect(
            lambda v: self.lr_label.setText(f"{v/100:.2f}")
        )
        lr_layout.addWidget(self.lr_slider)
        lr_layout.addWidget(self.lr_label)
        left.addWidget(lr_box)

        # 에폭
        epoch_box = QGroupBox("Epochs")
        epoch_layout = QVBoxLayout(epoch_box)
        self.epoch_spin = QSpinBox()
        self.epoch_spin.setRange(10, 500)
        self.epoch_spin.setValue(100)
        epoch_layout.addWidget(self.epoch_spin)
        left.addWidget(epoch_box)

        # Train 버튼
        self.train_btn = QPushButton("Train")
        self.train_btn.clicked.connect(self.on_train)
        left.addWidget(self.train_btn)

        # 결과 메시지
        self.msg_label = QLabel("")
        self.msg_label.setWordWrap(True)
        left.addWidget(self.msg_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # ── 오른쪽 그래프 ───────────────────────────────
        self.canvas = PlotCanvas(nrows=1, ncols=3, figsize=(10, 4))
        layout.addWidget(self.canvas)

        self.on_train()

    def on_train(self):
        gate_names = ['AND', 'OR', 'XOR']
        selected = gate_names[self.gate_group.checkedId()]
        lr = self.lr_slider.value() / 100
        epochs = self.epoch_spin.value()

        if selected == 'XOR':
            self.msg_label.setText(
                "⚠ XOR은 단일 퍼셉트론으로\n선형 분리가 불가능합니다."
            )
        else:
            self.msg_label.setText("")

        self.canvas.clear_all()
        axes = self.canvas.axes

        for i, (name, y) in enumerate(GATES.items()):
            p = Perceptron(input_size=2, learning_rate=lr)
            p.train(X_DATA, y, epochs=epochs)
            xx, yy, Z = p.get_decision_boundary()

            ax = axes[i]
            ax.contourf(xx, yy, Z, alpha=0.3,
                        levels=[-0.5, 0.5, 1.5], colors=['blue', 'red'])
            for point, label in zip(X_DATA, y):
                color = 'red' if label == 1 else 'blue'
                marker = 'o' if label == 1 else 'x'
                ax.scatter(point[0], point[1], c=color, marker=marker,
                           s=200, edgecolors='black', linewidth=2)
            ax.set_title(name)
            ax.set_xlim(-0.5, 1.5)
            ax.set_ylim(-0.5, 1.5)
            ax.grid(True, alpha=0.3)

        self.canvas.draw_safe()