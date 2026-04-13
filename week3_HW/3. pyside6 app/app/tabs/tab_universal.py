from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from widgets.plot_canvas import PlotCanvas
from models.universal import approximate


class UniversalWorker(QThread):
    finished = Signal(object)

    def __init__(self, func_name):
        super().__init__()
        self.func_name = func_name

    def run(self):
        results = approximate(self.func_name)
        self.finished.emit(results)


class UniversalTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # ── 왼쪽 패널 ──────────────────────────────────
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop)

        func_box = QGroupBox("Target Function")
        func_layout = QVBoxLayout(func_box)
        self.func_combo = QComboBox()
        self.func_combo.addItems(['sine', 'step', 'complex'])
        func_layout.addWidget(self.func_combo)
        left.addWidget(func_box)

        info_box = QGroupBox("Fixed Settings")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel("Neurons: 3 / 10 / 50"))
        info_layout.addWidget(QLabel("Activation: tanh (고정)"))
        info_layout.addWidget(QLabel("Epochs: 10000"))
        left.addWidget(info_box)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run)
        left.addWidget(self.run_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        left.addWidget(self.progress_bar)

        self.mse_label = QLabel("")
        self.mse_label.setWordWrap(True)
        left.addWidget(self.mse_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # ── 오른쪽 그래프 ───────────────────────────────
        self.canvas = PlotCanvas(nrows=1, ncols=3, figsize=(12, 4))
        layout.addWidget(self.canvas)

    def on_run(self):
        self.run_btn.setEnabled(False)
        self.mse_label.setText("학습 중... 잠시 기다려줘")
        self.progress_bar.setVisible(True)
        func_name = self.func_combo.currentText()
        self.worker = UniversalWorker(func_name)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, results):
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        mse_text = ""
        self.canvas.clear_all()
        axes = self.canvas.axes

        for i, r in enumerate(results):
            ax = axes[i]
            ax.plot(r['x'], r['y_true'], 'b-', linewidth=2, label='True', alpha=0.7)
            ax.plot(r['x'], r['y_pred'], 'r--', linewidth=2, label=f"NN ({r['n']} neurons)")
            ax.set_title(f"{r['n']} Neurons\nMSE: {r['mse']:.4f}")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            mse_text += f"{r['n']} neurons: MSE = {r['mse']:.4f}\n"

        self.mse_label.setText(mse_text.strip())
        self.canvas.draw_safe()