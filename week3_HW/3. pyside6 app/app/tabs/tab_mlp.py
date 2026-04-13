import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from widgets.plot_canvas import PlotCanvas
from models.mlp import MLP


X_XOR = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
Y_XOR = np.array([[0],[1],[1],[0]], dtype=float)


class TrainWorker(QThread):
    progress = Signal(int, float)
    finished = Signal(object)

    def __init__(self, model, epochs):
        super().__init__()
        self.model = model
        self.epochs = epochs

    def run(self):
        for epoch, loss in self.model.train(X_XOR, Y_XOR, self.epochs):
            if epoch % 100 == 0:
                self.progress.emit(epoch, loss)
        self.finished.emit(self.model)


class MLPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.model = MLP()
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # ── 왼쪽 패널 ──────────────────────────────────
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop)

        # 학습률
        lr_box = QGroupBox("Learning Rate")
        lr_layout = QVBoxLayout(lr_box)
        self.lr_slider = QSlider(Qt.Horizontal)
        self.lr_slider.setRange(1, 100)
        self.lr_slider.setValue(50)
        self.lr_label = QLabel("0.50")
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
        self.epoch_spin.setRange(100, 10000)
        self.epoch_spin.setValue(5000)
        self.epoch_spin.setSingleStep(100)
        epoch_layout.addWidget(self.epoch_spin)
        left.addWidget(epoch_box)

        info_box = QGroupBox("Fixed Settings")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel("Hidden neurons: 4 (고정)"))
        info_layout.addWidget(QLabel("Task: XOR"))
        left.addWidget(info_box)

        self.train_btn = QPushButton("Train")
        self.train_btn.clicked.connect(self.on_train)
        left.addWidget(self.train_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        left.addWidget(self.progress_bar)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        left.addWidget(self.result_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # ── 오른쪽 그래프 ───────────────────────────────
        self.canvas = PlotCanvas(nrows=1, ncols=3, figsize=(12, 4))
        layout.addWidget(self.canvas)

    def on_train(self):
        self.train_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.result_label.setText("학습 중...")
        lr = self.lr_slider.value() / 100
        epochs = self.epoch_spin.value()
        self.model = MLP(learning_rate=lr)
        self.worker = TrainWorker(self.model, epochs)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, epoch, loss):
        epochs = self.epoch_spin.value()
        pct = int(epoch / epochs * 100)
        self.progress_bar.setValue(pct)

    def _on_finished(self, model):
        self.model = model
        self.train_btn.setEnabled(True)
        self.progress_bar.setValue(100)

        preds = model.predict(X_XOR)
        acc = np.mean(preds == Y_XOR.astype(int)) * 100
        final_loss = model.loss_history[-1]
        self.result_label.setText(
            f"완료!\nLoss: {final_loss:.6f}\n정확도: {acc:.1f}%"
        )
        self._draw(model)

    def _draw(self, model):
        self.canvas.clear_all()
        axes = self.canvas.axes

        # Loss 곡선
        ax = axes[0]
        ax.plot(model.loss_history, linewidth=2)
        ax.set_title('Training Loss')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)

        # 결정 경계
        ax = axes[1]
        xx, yy, Z = model.get_decision_boundary()
        ax.contourf(xx, yy, Z, levels=20, cmap='RdYlBu', alpha=0.8)
        for point, label in zip(X_XOR, Y_XOR):
            color = 'red' if label[0] == 1 else 'blue'
            marker = 'o' if label[0] == 1 else 'x'
            ax.scatter(point[0], point[1], c=color, marker=marker,
                       s=300, edgecolors='black', linewidth=2, zorder=5)
        ax.set_title('Decision Boundary')
        ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.5, 1.5)
        ax.grid(True, alpha=0.3)

        # 은닉층 활성화
        ax = axes[2]
        model.forward(X_XOR)
        im = ax.imshow(model.a1.T, cmap='viridis', aspect='auto')
        ax.set_yticks(range(4))
        ax.set_yticklabels([f'H{i+1}' for i in range(4)])
        ax.set_xticks(range(4))
        ax.set_xticklabels(['(0,0)', '(0,1)', '(1,0)', '(1,1)'])
        ax.set_title('Hidden Activations')
        self.canvas.fig.colorbar(im, ax=ax)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f'{model.a1[j,i]:.2f}',
                        ha='center', va='center', color='white', fontweight='bold')

        self.canvas.draw_safe()