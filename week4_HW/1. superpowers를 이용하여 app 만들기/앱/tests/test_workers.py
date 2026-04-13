import sys
import pytest
import numpy as np
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope='module')
def qapp():
    return QApplication.instance() or QApplication(sys.argv)

def test_epoch_callback_emits_signal(qapp):
    """EpochCallback이 epoch_end 시그널을 발사하는지 확인."""
    import tensorflow as tf
    from tensorflow import keras
    from app.workers.worker_base import WorkerSignals, EpochCallback

    signals = WorkerSignals()
    received = []
    signals.epoch_end.connect(lambda e, tl, vl: received.append((e, tl, vl)))

    callback = EpochCallback(signals, total_epochs=3)

    model = keras.Sequential([
        keras.layers.Input(shape=(1,)),
        keras.layers.Dense(4, activation='relu'),
        keras.layers.Dense(1),
    ])
    model.compile(optimizer='adam', loss='mse')
    x = np.linspace(0, 1, 20).reshape(-1, 1)
    y = x * 2

    model.fit(x, y, epochs=2, verbose=0, callbacks=[callback])

    assert len(received) == 2
    assert received[0][0] == 0  # 첫 번째 epoch 인덱스

def test_epoch_callback_stop(qapp):
    """_stop=True 시 model.stop_training이 설정되는지 확인."""
    import tensorflow as tf
    from tensorflow import keras
    from app.workers.worker_base import WorkerSignals, EpochCallback

    signals = WorkerSignals()
    callback = EpochCallback(signals, total_epochs=10)
    callback._stop = True

    model = keras.Sequential([
        keras.layers.Input(shape=(1,)),
        keras.layers.Dense(1),
    ])
    model.compile(optimizer='adam', loss='mse')

    callback.set_model(model)
    callback.on_epoch_end(0, logs={'loss': 0.1})

    assert model.stop_training is True

def test_perfect1d_data_shapes():
    from app.workers.worker_perfect1d import make_data
    for func in ['sin(x)', 'cos(x) + 0.5sin(2x)', 'x·sin(x)']:
        x_tr, y_tr, x_te, y_te = make_data(func)
        assert x_tr.shape == (200, 1)
        assert y_tr.shape == (200, 1)
        assert x_te.shape == (400, 1)
        assert y_te.shape == (400, 1)

def test_perfect1d_model_shape():
    from app.workers.worker_perfect1d import create_model
    model = create_model([32], 'tanh', 0.01)
    import numpy as np
    out = model.predict(np.zeros((5, 1)), verbose=0)
    assert out.shape == (5, 1)
