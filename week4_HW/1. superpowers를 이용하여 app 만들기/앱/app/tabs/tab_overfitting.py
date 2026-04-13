from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton,
    QProgressBar, QTextEdit, QLabel,
)
from PySide6.QtCore import Slot
from app.utils.plot_canvas import MplCanvas
from app.workers.worker_overfitting import OverfittingWorker

COLORS = {'underfit': 'blue', 'good': 'green', 'overfit': 'red'}
TITLES = {
    'underfit': 'Underfitting\n(Too Simple)',
    'good': 'Good Fit\n(Just Right)',
    'overfit': 'Overfitting\n(Too Complex)',
}


class OverfittingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._epochs_done = []
        self._train_losses = []
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)

        ctrl = QWidget()
        ctrl.setFixedWidth(280)
        vbox = QVBoxLayout(ctrl)
        form = QFormLayout()

        self._epochs_sp = QSpinBox()
        self._epochs_sp.setRange(50, 500)
        self._epochs_sp.setValue(200)
        form.addRow('Epochs:', self._epochs_sp)

        self._lr_sp = QDoubleSpinBox()
        self._lr_sp.setRange(0.0001, 0.01)
        self._lr_sp.setValue(0.001)
        self._lr_sp.setDecimals(4)
        form.addRow('Learning Rate:', self._lr_sp)

        self._noise_sp = QDoubleSpinBox()
        self._noise_sp.setRange(0.0, 1.0)
        self._noise_sp.setValue(0.3)
        self._noise_sp.setSingleStep(0.05)
        form.addRow('Noise Level:', self._noise_sp)

        vbox.addLayout(form)
        vbox.addWidget(QLabel('순서: Underfit → Good → Overfit'))

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
        self._log.setMaximumHeight(250)
        vbox.addWidget(QLabel('Log:'))
        vbox.addWidget(self._log)
        vbox.addStretch()

        root.addWidget(ctrl)
        self._canvas = MplCanvas(nrows=2, ncols=3, figsize=(14, 8))
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

        self._worker = OverfittingWorker({
            'epochs': self._epochs_sp.value(),
            'lr': self._lr_sp.value(),
            'noise_level': self._noise_sp.value(),
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

    @Slot(dict)
    def _on_done(self, r):
        axes = self._canvas.axes
        x_te, y_te = r['x_te'], r['y_te']
        x_tr, y_tr = r['x_tr'], r['y_tr']

        for idx, stage in enumerate(['underfit', 'good', 'overfit']):
            res = r['results'][stage]
            y_pred = res['y_pred']
            color = COLORS[stage]

            ax_top = axes[0, idx]
            ax_top.clear()
            ax_top.scatter(x_tr, y_tr, alpha=0.4, s=20, color='gray', label='Train data')
            ax_top.plot(x_te, y_te, 'k-', linewidth=2.5, label='True', alpha=0.7)
            ax_top.plot(x_te, y_pred, color=color, linestyle='--', linewidth=2, label='Pred')
            ax_top.set_title(TITLES[stage], fontsize=11, fontweight='bold')
            ax_top.set_xlabel('x')
            ax_top.set_ylabel('y')
            ax_top.legend(fontsize=7)
            ax_top.grid(True, alpha=0.3)

            ax_bot = axes[1, idx]
            ax_bot.clear()
            h = res['history']
            epochs_range = range(1, len(h['loss']) + 1)
            ax_bot.plot(epochs_range, h['loss'], color=color, linestyle='-', linewidth=2, label='Train')
            ax_bot.plot(epochs_range, h['val_loss'], color=color, linestyle='--', linewidth=2, label='Val')
            ax_bot.set_title(TITLES[stage], fontsize=11, fontweight='bold')
            ax_bot.set_xlabel('Epoch')
            ax_bot.set_ylabel('Loss')
            ax_bot.set_yscale('log')
            ax_bot.legend(fontsize=7)
            ax_bot.grid(True, alpha=0.3)

        self._canvas.fig.tight_layout()
        self._canvas.draw_idle()
        self._log.append('\n✓ 학습 완료!')

    @Slot(str)
    def _on_error(self, msg):
        self._log.append(f'ERROR: {msg}')

    def _on_finished(self):
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _reset_plots(self):
        self._epochs_done.clear()
        self._train_losses.clear()
        for row in self._canvas.axes:
            for ax in row:
                ax.clear()
        self._canvas.draw_idle()
