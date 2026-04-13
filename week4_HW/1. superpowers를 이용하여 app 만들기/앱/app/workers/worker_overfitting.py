import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback


def true_function(x):
    return np.sin(2 * x) + 0.5 * x


def generate_data(n_train=100, n_val=50, n_test=200, noise_level=0.3):
    x_tr = np.random.uniform(-2, 2, n_train).reshape(-1, 1)
    y_tr = true_function(x_tr) + np.random.normal(0, noise_level, (n_train, 1))
    x_val = np.random.uniform(-2, 2, n_val).reshape(-1, 1)
    y_val = true_function(x_val) + np.random.normal(0, noise_level, (n_val, 1))
    x_te = np.linspace(-2, 2, n_test).reshape(-1, 1)
    y_te = true_function(x_te).reshape(-1, 1)
    return x_tr, y_tr, x_val, y_val, x_te, y_te


def create_underfit(lr=0.001):
    m = keras.Sequential([
        keras.layers.Input(shape=(1,)),
        keras.layers.Dense(4, activation='relu'),
        keras.layers.Dense(1),
    ])
    m.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return m


def create_good(lr=0.001):
    m = keras.Sequential([
        keras.layers.Input(shape=(1,)),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(1),
    ])
    m.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return m


def create_overfit(lr=0.001):
    m = keras.Sequential([
        keras.layers.Input(shape=(1,)),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1),
    ])
    m.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return m


STAGES = ['underfit', 'good', 'overfit']
MODEL_FACTORIES = {
    'underfit': create_underfit,
    'good': create_good,
    'overfit': create_overfit,
}


class OverfittingWorker(BaseWorker):
    """3개 모델을 순차 학습."""

    def run(self):
        try:
            p = self.params
            x_tr, y_tr, x_val, y_val, x_te, y_te = generate_data(
                noise_level=p['noise_level']
            )
            epochs = p['epochs']
            results = {}

            for i, stage in enumerate(STAGES):
                if self._callback and self._callback._stop:
                    return
                self.signals.log.emit(f'\n--- {stage.upper()} 모델 학습 중... ---')
                model = MODEL_FACTORIES[stage](lr=p['lr'])

                stage_idx = i  # capture for closure

                class StagedCallback(EpochCallback):
                    def on_epoch_end(self_inner, epoch, logs=None):
                        if self_inner._stop:
                            self_inner.model.stop_training = True
                            return
                        logs = logs or {}
                        tl = float(logs.get('loss', 0.0))
                        vl = float(logs.get('val_loss', 0.0))
                        ep_global = stage_idx * epochs + epoch
                        self_inner.signals.epoch_end.emit(ep_global, tl, vl)
                        prog = int((ep_global + 1) / (3 * epochs) * 100)
                        self_inner.signals.progress.emit(min(prog, 100))
                        if (epoch + 1) % max(1, epochs // 10) == 0:
                            self_inner.signals.log.emit(
                                f"[{stage}] Epoch {epoch+1}/{epochs} "
                                f"loss:{tl:.4f} val:{vl:.4f}"
                            )

                cb = StagedCallback(self.signals, epochs)
                self._callback = cb

                history = model.fit(
                    x_tr, y_tr,
                    validation_data=(x_val, y_val),
                    epochs=epochs,
                    batch_size=16,
                    verbose=0,
                    callbacks=[cb],
                )
                if cb._stop:
                    return

                y_pred = model.predict(x_te, verbose=0)
                results[stage] = {
                    'history': history.history,
                    'y_pred': y_pred,
                }

            self.signals.training_done.emit({
                'x_tr': x_tr, 'y_tr': y_tr,
                'x_te': x_te, 'y_te': y_te,
                'results': results,
            })
        except Exception as e:
            self.signals.error.emit(str(e))
