from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton,
    QProgressBar, QTextEdit, QLabel, QSlider,
)
from PySide6.QtCore import Slot, Qt
from app.utils.plot_canvas import MplCanvas
from app.workers.worker_projectile import ProjectileWorker


class ProjectileTab(QWidget):
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

        self._samples_sp = QSpinBox()
        self._samples_sp.setRange(500, 5000)
        self._samples_sp.setValue(2000)
        self._samples_sp.setSingleStep(500)
        form.addRow('n_samples:', self._samples_sp)

        self._v0_sl = QSlider(Qt.Horizontal)
        self._v0_sl.setRange(10, 50)
        self._v0_sl.setValue(30)
        self._v0_label = QLabel('v₀ = 30 m/s')
        self._v0_sl.valueChanged.connect(lambda v: self._v0_label.setText(f'v₀ = {v} m/s'))
        form.addRow(self._v0_label, self._v0_sl)

        self._theta_sl = QSlider(Qt.Horizontal)
        self._theta_sl.setRange(20, 70)
        self._theta_sl.setValue(45)
        self._theta_label = QLabel('θ = 45°')
        self._theta_sl.valueChanged.connect(lambda v: self._theta_label.setText(f'θ = {v}°'))
        form.addRow(self._theta_label, self._theta_sl)

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

        params = {
            'epochs': self._epochs_sp.value(),
            'lr': self._lr_sp.value(),
            'n_samples': self._samples_sp.value(),
            'v0_test': float(self._v0_sl.value()),
            'theta_test': float(self._theta_sl.value()),
        }
        self._worker = ProjectileWorker(params)
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
        ax0.plot(r['x_true'], r['y_true'], 'b-', linewidth=2.5, label='True', alpha=0.7)
        ax0.plot(r['x_pred'], r['y_pred'], 'r--', linewidth=2, label='NN Prediction')
        ax0.set_xlabel('x (m)')
        ax0.set_ylabel('y (m)')
        ax0.set_title(f'v₀={r["v0_test"]} m/s, θ={r["theta_test"]}°')
        ax0.set_xlim(left=0)
        ax0.set_ylim(bottom=0)
        ax0.legend(fontsize=8)
        ax0.grid(True, alpha=0.3)

        ax2 = axes[1, 0]
        ax2.clear()
        ax2.plot(r['angles'], r['errors_angle'], 'go-', linewidth=2, markersize=6)
        ax2.set_xlabel('Launch Angle (°)')
        ax2.set_ylabel('MSE')
        ax2.set_title('Error vs Angle (v₀=30)')
        ax2.grid(True, alpha=0.3)

        ax3 = axes[1, 1]
        ax3.clear()
        ax3.plot(r['velocities'], r['errors_vel'], 'mo-', linewidth=2, markersize=6)
        ax3.set_xlabel('Initial Velocity (m/s)')
        ax3.set_ylabel('MSE')
        ax3.set_title('Error vs Velocity (θ=45°)')
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
