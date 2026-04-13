from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton,
    QProgressBar, QTextEdit, QLabel,
)
from PySide6.QtCore import Slot
from app.utils.plot_canvas import MplCanvas
from app.workers.worker_pendulum import PendulumWorker


class PendulumTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._epochs_done = []
        self._train_losses = []
        self._val_losses = []
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)

        ctrl = QWidget()
        ctrl.setFixedWidth(280)
        vbox = QVBoxLayout(ctrl)
        form = QFormLayout()

        self._epochs_sp = QSpinBox()
        self._epochs_sp.setRange(50, 500)
        self._epochs_sp.setValue(100)
        form.addRow('Epochs:', self._epochs_sp)

        self._lr_sp = QDoubleSpinBox()
        self._lr_sp.setRange(0.0001, 0.01)
        self._lr_sp.setValue(0.001)
        self._lr_sp.setDecimals(4)
        form.addRow('Learning Rate:', self._lr_sp)

        self._L_sp = QDoubleSpinBox()
        self._L_sp.setRange(0.5, 3.0)
        self._L_sp.setValue(1.0)
        self._L_sp.setSingleStep(0.1)
        form.addRow('L (m):', self._L_sp)

        self._theta_sp = QSpinBox()
        self._theta_sp.setRange(5, 80)
        self._theta_sp.setValue(45)
        form.addRow('θ₀ (°):', self._theta_sp)

        vbox.addLayout(form)

        btn_row = QHBoxLayout()
        self._run_btn = QPushButton('▶ Run')
        self._stop_btn = QPushButton('■ Stop')
        self._stop_btn.setEnabled(False)
        btn_row.addWidget(self._run_btn)
        btn_row.addWidget(self._stop_btn)
        vbox.addLayout(btn_row)

        self._progress = QProgressBar()
        vbox.addWidget(self._progress)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(200)
        vbox.addWidget(QLabel('Log:'))
        vbox.addWidget(self._log)
        vbox.addStretch()

        root.addWidget(ctrl)
        self._canvas = MplCanvas(nrows=2, ncols=2, figsize=(12, 8))
        root.addWidget(self._canvas)

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

        self._worker = PendulumWorker({
            'epochs': self._epochs_sp.value(),
            'lr': self._lr_sp.value(),
            'L_test': self._L_sp.value(),
            'theta_test': float(self._theta_sp.value()),
        })
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
        self._val_losses.append(val_loss)
        ax = self._canvas.axes[0, 1]
        ax.clear()
        ax.plot(self._epochs_done, self._train_losses, 'b-', linewidth=1.5, label='Train')
        ax.plot(self._epochs_done, self._val_losses, 'r--', linewidth=1.5, label='Val')
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

        ax0 = axes[0, 0]
        ax0.clear()
        ax0.plot(r['angles'], r['T_true'], 'b-', linewidth=2.5, label='True period', alpha=0.7)
        ax0.plot(r['angles'], r['T_pred'], 'r--', linewidth=2, label='NN prediction')
        ax0.set_xlabel('Angle (°)')
        ax0.set_ylabel('Period (s)')
        ax0.set_title(f'Period vs Angle  (L={r["L_test"]} m)', fontsize=11)
        ax0.legend(fontsize=8)
        ax0.grid(True, alpha=0.3)

        ax2 = axes[1, 0]
        ax2.clear()
        ax2.plot(r['t_sim'], r['theta_sim'], 'b-', linewidth=2)
        ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
        for i in range(3):
            ax2.axvline(r['T_true_single'] * i, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Angle (°)')
        ax2.set_title(
            f'RK4 Simulation  θ₀={r["theta_test"]}°\n'
            f'T_pred={r["T_pred_single"]:.3f}s  T_true={r["T_true_single"]:.3f}s',
            fontsize=10,
        )
        ax2.grid(True, alpha=0.3)

        ax3 = axes[1, 1]
        ax3.clear()
        ax3.plot(r['theta_sim'], r['omega_sim'], 'g-', linewidth=1.5, alpha=0.7)
        ax3.plot(r['theta_sim'][0], r['omega_sim'][0], 'ro', markersize=8, label='Start')
        ax3.set_xlabel('Angle (°)')
        ax3.set_ylabel('Angular Velocity (°/s)')
        ax3.set_title('Phase Space', fontsize=11)
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)

        self._canvas.fig.tight_layout()
        self._canvas.draw_idle()
        self._log.append(f'\n✓ Done — Test MSE: {r["test_loss"]:.6f}  MAE: {r["test_mae"]:.6f}')

    @Slot(str)
    def _on_error(self, msg):
        self._log.append(f'ERROR: {msg}')

    def _on_finished(self):
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _reset_plots(self):
        self._epochs_done.clear()
        self._train_losses.clear()
        self._val_losses.clear()
        for row in self._canvas.axes:
            for ax in row:
                ax.clear()
        self._canvas.draw_idle()
