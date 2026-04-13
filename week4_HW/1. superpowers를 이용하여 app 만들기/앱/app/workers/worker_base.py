import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow import keras
from PySide6.QtCore import QThread, QObject, Signal


class WorkerSignals(QObject):
    epoch_end = Signal(int, float, float)  # epoch, train_loss, val_loss
    training_done = Signal(dict)
    error = Signal(str)
    progress = Signal(int)  # 0-100
    log = Signal(str)


class EpochCallback(keras.callbacks.Callback):
    def __init__(self, signals: WorkerSignals, total_epochs: int):
        super().__init__()
        self.signals = signals
        self.total_epochs = total_epochs
        self._stop = False

    def on_epoch_end(self, epoch, logs=None):
        if self._stop:
            self.model.stop_training = True
            return
        logs = logs or {}
        train_loss = float(logs.get('loss', 0.0))
        val_loss = float(logs.get('val_loss', 0.0))
        progress = int((epoch + 1) / self.total_epochs * 100)
        self.signals.epoch_end.emit(epoch, train_loss, val_loss)
        self.signals.progress.emit(min(progress, 100))
        if (epoch + 1) % max(1, self.total_epochs // 20) == 0:
            self.signals.log.emit(
                f"Epoch {epoch+1}/{self.total_epochs} — loss: {train_loss:.6f}"
                + (f"  val_loss: {val_loss:.6f}" if val_loss else "")
            )


class BaseWorker(QThread):
    def __init__(self, params: dict):
        super().__init__()
        self.params = params
        self.signals = WorkerSignals()
        self._callback: EpochCallback | None = None

    def stop(self):
        if self._callback is not None:
            self._callback._stop = True

    def run(self):
        raise NotImplementedError
