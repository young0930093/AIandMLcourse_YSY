import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QProgressBar, QTextEdit, QLabel,
)
from PySide6.QtCore import Slot
from app.utils.plot_canvas import MplCanvas
from app.workers.worker_perfect1d import Perfect1DWorker


class Perfect1DTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._epochs_done = []
        self._train_losses = []
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)

        # --- 좌측 컨트롤 패널 ---
        ctrl = QWidget()
        ctrl.setFixedWidth(280)
        vbox = QVBoxLayout(ctrl)

        form = QFormLayout()
        self._func_cb = QComboBox()
        self._func_cb.addItems(['sin(x)', 'cos(x) + 0.5sin(2x)', 'x·sin(x)'])
        form.addRow('Function:', self._func_cb)

        self._arch_cb = QComboBox()
        self._arch_cb.addItems(['Small [32]', 'Medium [64, 64]', 'Large [128, 128]', 'VeryLarge [128, 128, 64]'])
        self._arch_cb.setCurrentIndex(2)
        form.addRow('Architecture:', self._arch_cb)

        self._act_cb = QComboBox()
        self._act_cb.addItems(['tanh', 'relu'])
        form.addRow('Activation:', self._act_cb)

        self._epochs_sp = QSpinBox()
        self._epochs_sp.setRange(100, 5000)
        self._epochs_sp.setValue(1000)
        self._epochs_sp.setSingleStep(100)
        form.addRow('Epochs:', self._epochs_sp)

        self._lr_sp = QDoubleSpinBox()
        self._lr_sp.setRange(0.0001, 0.1)
        self._lr_sp.setValue(0.01)
        self._lr_sp.setSingleStep(0.001)
        self._lr_sp.setDecimals(4)
        form.addRow('Learning Rate:', self._lr_sp)

        vbox.addLayout(form)

        btn_row = QHBoxLayout()
        self._run_btn = QPushButton('▶ Run')
        self._stop_btn = QPushButton('■ Stop')
        self._stop_btn.setEnabled(False)
        btn_row.addWidget(self._run_btn)
        btn_row.addWidget(self._stop_btn)
        vbox.addLayout(btn_row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        vbox.addWidget(self._progress)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(200)
        vbox.addWidget(QLabel('Log:'))
        vbox.addWidget(self._log)
        vbox.addStretch()

        root.addWidget(ctrl)

        # --- 우측 캔버스 ---
        self._canvas = MplCanvas(nrows=1, ncols=3, figsize=(12, 4))
        root.addWidget(self._canvas)

        # 시그널 연결
        self._run_btn.clicked.connect(self._on_run)
        self._stop_btn.clicked.connect(self._on_stop)

    def _on_run(self):
        if self._worker and self._worker.isRunning():
            return
        self._reset_plots()
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._progress.setValue(0)
        self._log.clear()

        params = {
            'function': self._func_cb.currentText(),
            'architecture': self._arch_cb.currentText(),
            'activation': self._act_cb.currentText(),
            'epochs': self._epochs_sp.value(),
            'lr': self._lr_sp.value(),
        }
        self._worker = Perfect1DWorker(params)
        self._worker.signals.epoch_end.connect(self._on_epoch)
        self._worker.signals.progress.connect(self._progress.setValue)
        self._worker.signals.log.connect(self._log.append)
        self._worker.signals.training_done.connect(self._on_done)
        self._worker.signals.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_stop(self):
        if self._worker:
            self._worker.stop()

    @Slot(int, float, float)
    def _on_epoch(self, epoch, train_loss, val_loss):
        self._epochs_done.append(epoch)
        self._train_losses.append(train_loss)
        ax = self._canvas.axes[1]
        ax.clear()
        ax.plot(self._epochs_done, self._train_losses, 'g-', linewidth=1.5, label='Train Loss')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('MSE')
        ax.set_title('Training Loss')
        ax.set_yscale('log')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()

    @Slot(dict)
    def _on_done(self, r):
        axes = self._canvas.axes
        func = self._func_cb.currentText()

        # Plot 0: 함수 근사
        ax0 = axes[0]
        ax0.clear()
        ax0.plot(r['x_te'], r['y_te'], 'b-', linewidth=2.5, label='True', alpha=0.7)
        ax0.plot(r['x_te'], r['y_pred'], 'r--', linewidth=2, label='Predicted')
        ax0.scatter(r['x_tr'][::10], r['y_tr'][::10], c='black', s=15, alpha=0.3)
        ax0.set_title(f'{func}\nMSE: {r["mse"]:.6f}', fontsize=11, fontweight='bold')
        ax0.set_xlabel('x')
        ax0.set_ylabel('y')
        ax0.legend(fontsize=8)
        ax0.grid(True, alpha=0.3)

        # Plot 2: 오차
        ax2 = axes[2]
        ax2.clear()
        error = np.abs(r['y_pred'] - r['y_te'])
        ax2.plot(r['x_te'], error, 'r-', linewidth=1.5)
        ax2.fill_between(r['x_te'].flatten(), 0, error.flatten(), color='r', alpha=0.3)
        ax2.set_title(f'Absolute Error\nMax: {r["max_err"]:.6f}', fontsize=11, fontweight='bold')
        ax2.set_xlabel('x')
        ax2.set_ylabel('Error')
        ax2.grid(True, alpha=0.3)

        self._canvas.fig.tight_layout()
        self._canvas.draw_idle()
        self._log.append(f'\n✓ Done — MSE: {r["mse"]:.8f}  MAE: {r["mae"]:.8f}  Max: {r["max_err"]:.8f}')

    @Slot(str)
    def _on_error(self, msg):
        self._log.append(f'ERROR: {msg}')

    def _on_finished(self):
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _reset_plots(self):
        self._epochs_done.clear()
        self._train_losses.clear()
        for ax in self._canvas.axes:
            ax.clear()
        self._canvas.draw_idle()
