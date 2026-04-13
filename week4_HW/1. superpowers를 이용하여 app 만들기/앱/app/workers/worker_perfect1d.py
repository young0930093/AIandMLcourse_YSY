import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback

ARCHITECTURES = {
    'Small [32]': [32],
    'Medium [64, 64]': [64, 64],
    'Large [128, 128]': [128, 128],
    'VeryLarge [128, 128, 64]': [128, 128, 64],
}


def make_data(func_name: str):
    x_tr = np.linspace(-2 * np.pi, 2 * np.pi, 200).reshape(-1, 1)
    x_te = np.linspace(-2 * np.pi, 2 * np.pi, 400).reshape(-1, 1)
    if func_name == 'sin(x)':
        return x_tr, np.sin(x_tr), x_te, np.sin(x_te)
    elif func_name == 'cos(x) + 0.5sin(2x)':
        return x_tr, np.cos(x_tr) + 0.5 * np.sin(2 * x_tr), x_te, np.cos(x_te) + 0.5 * np.sin(2 * x_te)
    else:  # x·sin(x)
        return x_tr, x_tr * np.sin(x_tr), x_te, x_te * np.sin(x_te)


def create_model(hidden_layers: list, activation: str, lr: float):
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(1,)))
    for units in hidden_layers:
        model.add(keras.layers.Dense(units, activation=activation))
    model.add(keras.layers.Dense(1, activation='linear'))
    model.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return model


class Perfect1DWorker(BaseWorker):
    def run(self):
        try:
            p = self.params
            x_tr, y_tr, x_te, y_te = make_data(p['function'])
            hidden = ARCHITECTURES[p['architecture']]
            model = create_model(hidden, p['activation'], p['lr'])
            epochs = p['epochs']
            self._callback = EpochCallback(self.signals, epochs)

            history = model.fit(
                x_tr, y_tr,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                callbacks=[self._callback],
            )

            if self._callback._stop:
                return

            y_pred = model.predict(x_te, verbose=0)
            mse = float(np.mean((y_pred - y_te) ** 2))
            mae = float(np.mean(np.abs(y_pred - y_te)))
            max_err = float(np.max(np.abs(y_pred - y_te)))

            self.signals.training_done.emit({
                'x_tr': x_tr, 'y_tr': y_tr,
                'x_te': x_te, 'y_te': y_te, 'y_pred': y_pred,
                'history': history.history,
                'mse': mse, 'mae': mae, 'max_err': max_err,
            })
        except Exception as e:
            self.signals.error.emit(str(e))
