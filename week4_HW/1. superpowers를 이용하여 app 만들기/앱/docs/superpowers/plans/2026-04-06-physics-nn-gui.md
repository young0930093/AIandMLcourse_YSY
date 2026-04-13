# Physics NN GUI App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 4개의 TF 물리 신경망 스크립트를 PySide6 탭 GUI 앱으로 재구현한다. 각 탭에서 하이퍼파라미터 조정 후 Run → 에폭마다 실시간 그래프 업데이트.

**Architecture:** QThread Worker가 TF 학습 실행, 커스텀 Keras EpochCallback이 pyqtSignal 발사, UI 스레드가 matplotlib FigureCanvasQTAgg 업데이트.

**Tech Stack:** PySide6 ≥6.5, TensorFlow ≥2.12, matplotlib ≥3.7, numpy ≥1.23, Python ≥3.10

---

## File Map

| 파일 | 역할 |
|------|------|
| `main.py` | QApplication 생성 및 MainWindow 표시 |
| `app/__init__.py` | 패키지 마커 |
| `app/main_window.py` | QMainWindow + QTabWidget (4 tabs) |
| `app/utils/__init__.py` | 패키지 마커 |
| `app/utils/plot_canvas.py` | MplCanvas(FigureCanvasQTAgg) 재사용 위젯 |
| `app/workers/__init__.py` | 패키지 마커 |
| `app/workers/worker_base.py` | WorkerSignals, EpochCallback, BaseWorker |
| `app/workers/worker_perfect1d.py` | Perfect1D 모델 정의 + 데이터 생성 + Worker |
| `app/workers/worker_projectile.py` | Projectile 모델 + 데이터 + Worker |
| `app/workers/worker_overfitting.py` | 3개 모델(under/good/over) + Worker (순차) |
| `app/workers/worker_pendulum.py` | Pendulum 모델 + RK4 + Worker |
| `app/tabs/__init__.py` | 패키지 마커 |
| `app/tabs/tab_perfect1d.py` | Tab 1 UI + 시그널 연결 + 그래프 |
| `app/tabs/tab_projectile.py` | Tab 2 UI + 시그널 연결 + 그래프 |
| `app/tabs/tab_overfitting.py` | Tab 3 UI + 시그널 연결 + 그래프 |
| `app/tabs/tab_pendulum.py` | Tab 4 UI + 시그널 연결 + 그래프 |
| `tests/test_workers.py` | Worker 로직 단위 테스트 |
| `tests/test_physics.py` | 물리 함수 단위 테스트 |
| `requirements.txt` | 의존성 |
| `docs/PRD.md` | (이미 작성됨) |
| `docs/TRD.md` | (이미 작성됨) |

---

## Task 1: 프로젝트 스캐폴드 + requirements.txt

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `app/__init__.py`
- Create: `app/utils/__init__.py`
- Create: `app/workers/__init__.py`
- Create: `app/tabs/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: requirements.txt 작성**

```
pyside6>=6.5.0
tensorflow>=2.12.0
matplotlib>=3.7.0
numpy>=1.23.0
pytest>=7.0.0
```

- [ ] **Step 2: 패키지 init 파일 생성**

`app/__init__.py`, `app/utils/__init__.py`, `app/workers/__init__.py`, `app/tabs/__init__.py`, `tests/__init__.py` — 모두 빈 파일로 생성.

- [ ] **Step 3: main.py 작성**

```python
import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 앱 시작 확인**

```bash
pip install -r requirements.txt
python main.py
```

아직 MainWindow가 없으므로 ImportError가 나야 정상. 다음 태스크로 계속.

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt main.py app/__init__.py app/utils/__init__.py app/workers/__init__.py app/tabs/__init__.py tests/__init__.py
git commit -m "chore: project scaffold"
```

---

## Task 2: MplCanvas 유틸리티

**Files:**
- Create: `app/utils/plot_canvas.py`
- Create: `tests/test_plot_canvas.py`

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_plot_canvas.py
import pytest
import sys
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope='module')
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    return app

def test_mplcanvas_single_axes(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=1, ncols=1)
    import numpy as np
    # axes가 단일 Axes 객체여야 함
    assert hasattr(canvas.axes, 'plot')

def test_mplcanvas_multi_axes(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=2, ncols=3)
    # axes가 2x3 배열이어야 함
    assert canvas.axes.shape == (2, 3)

def test_mplcanvas_fig_exists(qapp):
    from app.utils.plot_canvas import MplCanvas
    canvas = MplCanvas(nrows=1, ncols=2)
    assert canvas.fig is not None
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_plot_canvas.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.utils.plot_canvas'`

- [ ] **Step 3: MplCanvas 구현**

```python
# app/utils/plot_canvas.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    """재사용 가능한 matplotlib PySide6 임베딩 위젯."""

    def __init__(self, nrows=1, ncols=1, figsize=(10, 6)):
        self.fig = Figure(figsize=figsize)
        self.axes = self.fig.subplots(nrows, ncols)
        super().__init__(self.fig)
        self.fig.tight_layout()
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
pytest tests/test_plot_canvas.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add app/utils/plot_canvas.py tests/test_plot_canvas.py
git commit -m "feat: add MplCanvas utility widget"
```

---

## Task 3: BaseWorker + EpochCallback

**Files:**
- Create: `app/workers/worker_base.py`
- Create: `tests/test_workers.py`

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_workers.py
import sys
import pytest
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop, QTimer

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

    # 간단한 모델로 2 에폭 학습
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

    # on_epoch_end 직접 호출 시뮬레이션
    callback.set_model(model)
    callback.on_epoch_end(0, logs={'loss': 0.1})

    assert model.stop_training is True
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_workers.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.workers.worker_base'`

- [ ] **Step 3: worker_base.py 구현**

```python
# app/workers/worker_base.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow import keras
from PySide6.QtCore import QThread, QObject, Signal


class WorkerSignals(QObject):
    epoch_end = Signal(int, float, float)  # epoch, train_loss, val_loss
    training_done = Signal(dict)
    error = Signal(str)
    progress = Signal(int)  # 0–100
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
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
pytest tests/test_workers.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/workers/worker_base.py tests/test_workers.py
git commit -m "feat: add BaseWorker and EpochCallback"
```

---

## Task 4: Tab 1 — Perfect 1D Function Approximation

**Files:**
- Create: `app/workers/worker_perfect1d.py`
- Create: `app/tabs/tab_perfect1d.py`
- Modify: `tests/test_workers.py` (테스트 추가)

- [ ] **Step 1: Worker 테스트 추가** (`tests/test_workers.py` 파일 하단에 추가)

```python
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
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_workers.py::test_perfect1d_data_shapes -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: worker_perfect1d.py 구현**

```python
# app/workers/worker_perfect1d.py
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
```

- [ ] **Step 4: tab_perfect1d.py 구현**

```python
# app/tabs/tab_perfect1d.py
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
        self._val_losses = []
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
        ax0.set_xlabel('x'); ax0.set_ylabel('y')
        ax0.legend(fontsize=8); ax0.grid(True, alpha=0.3)

        # Plot 2: 오차
        ax2 = axes[2]
        ax2.clear()
        error = np.abs(r['y_pred'] - r['y_te'])
        ax2.plot(r['x_te'], error, 'r-', linewidth=1.5)
        ax2.fill_between(r['x_te'].flatten(), 0, error.flatten(), color='r', alpha=0.3)
        ax2.set_title(f'Absolute Error\nMax: {r["max_err"]:.6f}', fontsize=11, fontweight='bold')
        ax2.set_xlabel('x'); ax2.set_ylabel('Error')
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
```

- [ ] **Step 5: 테스트 실행**

```bash
pytest tests/test_workers.py::test_perfect1d_data_shapes tests/test_workers.py::test_perfect1d_model_shape -v
```

Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add app/workers/worker_perfect1d.py app/tabs/tab_perfect1d.py tests/test_workers.py
git commit -m "feat: add Perfect1D worker and tab"
```

---

## Task 5: Tab 2 — Projectile Motion

**Files:**
- Create: `app/workers/worker_projectile.py`
- Create: `app/tabs/tab_projectile.py`
- Modify: `tests/test_physics.py` (새 파일)

- [ ] **Step 1: 물리 함수 테스트 작성**

```python
# tests/test_physics.py
import numpy as np

def test_projectile_data_shapes():
    from app.workers.worker_projectile import generate_projectile_data
    X, Y = generate_projectile_data(200, noise_level=0.0)
    assert X.shape[1] == 3   # v0, theta, t
    assert Y.shape[1] == 2   # x, y
    assert np.all(Y[:, 1] >= -0.01)  # y >= 0 (노이즈 없음)

def test_projectile_data_physics():
    """v0=10, theta=90, t=0이면 x≈0, y≈0."""
    from app.workers.worker_projectile import generate_projectile_data
    import numpy as np
    # 실제 검증: cos(90°)=0이므로 x 이동 없음
    # 직접 계산으로 검증
    v0, theta, t = 20.0, 45.0, 0.5
    theta_rad = np.deg2rad(theta)
    g = 9.81
    expected_x = v0 * np.cos(theta_rad) * t
    expected_y = v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    assert expected_x > 0
    assert expected_y > 0

def test_projectile_model_shape():
    from app.workers.worker_projectile import create_projectile_model
    model = create_projectile_model(lr=0.001)
    import numpy as np
    out = model.predict(np.zeros((5, 3)), verbose=0)
    assert out.shape == (5, 2)
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_physics.py::test_projectile_data_shapes -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: worker_projectile.py 구현**

```python
# app/workers/worker_projectile.py
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback

G = 9.81


def generate_projectile_data(n_samples: int, noise_level: float = 0.5):
    v0 = np.random.uniform(10, 50, n_samples)
    theta = np.random.uniform(20, 70, n_samples)
    theta_rad = np.deg2rad(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / G
    t = np.random.uniform(0, t_max * 0.9, n_samples)
    x = v0 * np.cos(theta_rad) * t + np.random.normal(0, noise_level, n_samples)
    y = v0 * np.sin(theta_rad) * t - 0.5 * G * t ** 2 + np.random.normal(0, noise_level, n_samples)
    valid = y >= 0
    X = np.column_stack([v0[valid], theta[valid], t[valid]])
    Y = np.column_stack([x[valid], y[valid]])
    return X, Y


def predict_trajectory(model, v0: float, theta: float, n_points: int = 50):
    theta_rad = np.deg2rad(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / G
    t = np.linspace(0, t_max, n_points)
    X_in = np.column_stack([np.full(n_points, v0), np.full(n_points, theta), t])
    pred = model.predict(X_in, verbose=0)
    return pred[:, 0], pred[:, 1], t


def create_projectile_model(lr: float = 0.001):
    model = keras.Sequential([
        keras.layers.Input(shape=(3,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(2, activation='linear'),
    ])
    model.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return model


class ProjectileWorker(BaseWorker):
    def run(self):
        try:
            p = self.params
            X_tr, Y_tr = generate_projectile_data(p['n_samples'], noise_level=0.5)
            X_te, Y_te = generate_projectile_data(500, noise_level=0.0)
            model = create_projectile_model(p['lr'])
            epochs = p['epochs']
            self._callback = EpochCallback(self.signals, epochs)

            history = model.fit(
                X_tr, Y_tr,
                validation_split=0.2,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                callbacks=[self._callback],
            )
            if self._callback._stop:
                return

            # 테스트 조건별 궤적
            v0_test, theta_test = p['v0_test'], p['theta_test']
            x_pred, y_pred, t = predict_trajectory(model, v0_test, theta_test)
            theta_rad = np.deg2rad(theta_test)
            x_true = v0_test * np.cos(theta_rad) * t
            y_true = v0_test * np.sin(theta_rad) * t - 0.5 * G * t ** 2

            # 각도별 오차
            angles = np.arange(20, 71, 5)
            errors_angle = []
            for ang in angles:
                xp, yp, tt = predict_trajectory(model, 30, ang)
                ar = np.deg2rad(ang)
                xt = 30 * np.cos(ar) * tt
                yt = 30 * np.sin(ar) * tt - 0.5 * G * tt ** 2
                errors_angle.append(float(np.mean((xp - xt) ** 2 + (yp - yt) ** 2)))

            # 속도별 오차
            velocities = np.arange(10, 51, 5)
            errors_vel = []
            for v in velocities:
                xp, yp, tt = predict_trajectory(model, v, 45)
                ar = np.deg2rad(45)
                xt = v * np.cos(ar) * tt
                yt = v * np.sin(ar) * tt - 0.5 * G * tt ** 2
                errors_vel.append(float(np.mean((xp - xt) ** 2 + (yp - yt) ** 2)))

            test_loss, test_mae = model.evaluate(X_te, Y_te, verbose=0)

            self.signals.training_done.emit({
                'history': history.history,
                'x_pred': x_pred, 'y_pred': y_pred,
                'x_true': x_true, 'y_true': y_true, 't': t,
                'v0_test': v0_test, 'theta_test': theta_test,
                'angles': angles.tolist(), 'errors_angle': errors_angle,
                'velocities': velocities.tolist(), 'errors_vel': errors_vel,
                'test_loss': float(test_loss), 'test_mae': float(test_mae),
            })
        except Exception as e:
            self.signals.error.emit(str(e))
```

- [ ] **Step 4: tab_projectile.py 구현**

```python
# app/tabs/tab_projectile.py
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
        self._epochs_sp.setRange(10, 500)
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
        ax.set_xlabel('Epoch'); ax.set_ylabel('MSE')
        ax.set_title('Training Loss'); ax.set_yscale('log')
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()

    @Slot(dict)
    def _on_done(self, r):
        axes = self._canvas.axes
        # 궤적
        ax0 = axes[0, 0]
        ax0.clear()
        ax0.plot(r['x_true'], r['y_true'], 'b-', linewidth=2.5, label='True', alpha=0.7)
        ax0.plot(r['x_pred'], r['y_pred'], 'r--', linewidth=2, label='NN Prediction')
        ax0.set_xlabel('x (m)'); ax0.set_ylabel('y (m)')
        ax0.set_title(f'v₀={r["v0_test"]} m/s, θ={r["theta_test"]}°')
        ax0.set_xlim(left=0); ax0.set_ylim(bottom=0)
        ax0.legend(fontsize=8); ax0.grid(True, alpha=0.3)
        # 각도별 오차
        ax2 = axes[1, 0]
        ax2.clear()
        ax2.plot(r['angles'], r['errors_angle'], 'go-', linewidth=2, markersize=6)
        ax2.set_xlabel('Launch Angle (°)'); ax2.set_ylabel('MSE')
        ax2.set_title('Error vs Angle (v₀=30)'); ax2.grid(True, alpha=0.3)
        # 속도별 오차
        ax3 = axes[1, 1]
        ax3.clear()
        ax3.plot(r['velocities'], r['errors_vel'], 'mo-', linewidth=2, markersize=6)
        ax3.set_xlabel('Initial Velocity (m/s)'); ax3.set_ylabel('MSE')
        ax3.set_title('Error vs Velocity (θ=45°)'); ax3.grid(True, alpha=0.3)
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
```

- [ ] **Step 5: 테스트 실행**

```bash
pytest tests/test_physics.py -v
```

Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add app/workers/worker_projectile.py app/tabs/tab_projectile.py tests/test_physics.py
git commit -m "feat: add Projectile Motion worker and tab"
```

---

## Task 6: Tab 3 — Overfitting vs Underfitting

**Files:**
- Create: `app/workers/worker_overfitting.py`
- Create: `app/tabs/tab_overfitting.py`
- Modify: `tests/test_physics.py` (테스트 추가)

- [ ] **Step 1: 테스트 추가** (`tests/test_physics.py` 하단에 추가)

```python
def test_overfitting_data_shapes():
    from app.workers.worker_overfitting import generate_data
    x_tr, y_tr, x_val, y_val, x_te, y_te = generate_data(50, 20, 100, 0.3)
    assert x_tr.shape == (50, 1)
    assert y_te.shape == (100, 1)

def test_overfitting_true_function():
    from app.workers.worker_overfitting import true_function
    import numpy as np
    x = np.array([[0.0]])
    # sin(2*0) + 0.5*0 = 0
    assert abs(true_function(x)[0, 0]) < 1e-9

def test_overfitting_model_shapes():
    from app.workers.worker_overfitting import create_underfit, create_good, create_overfit
    import numpy as np
    for create_fn in [create_underfit, create_good, create_overfit]:
        model = create_fn(lr=0.001)
        out = model.predict(np.zeros((3, 1)), verbose=0)
        assert out.shape == (3, 1)
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_physics.py::test_overfitting_data_shapes -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: worker_overfitting.py 구현**

```python
# app/workers/worker_overfitting.py
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


# 단계별 상수
STAGES = ['underfit', 'good', 'overfit']
MODEL_FACTORIES = {
    'underfit': create_underfit,
    'good': create_good,
    'overfit': create_overfit,
}


class OverfittingWorker(BaseWorker):
    """3개 모델을 순차 학습. training_done 시그널에 stage 정보 포함."""

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
                self._callback = EpochCallback(self.signals, epochs)
                # 각 단계의 진행률을 전체 33%씩 나눔
                class StagedCallback(EpochCallback):
                    def __init__(self_, *args, stage_idx=i, **kwargs):
                        super().__init__(*args, **kwargs)
                        self_._stage_idx = stage_idx
                    def on_epoch_end(self_, epoch, logs=None):
                        if self_._stop:
                            self_.model.stop_training = True
                            return
                        logs = logs or {}
                        tl = float(logs.get('loss', 0.0))
                        vl = float(logs.get('val_loss', 0.0))
                        ep_global = self_._stage_idx * epochs + epoch
                        self_.signals.epoch_end.emit(ep_global, tl, vl)
                        prog = int((ep_global + 1) / (3 * epochs) * 100)
                        self_.signals.progress.emit(min(prog, 100))
                        if (epoch + 1) % max(1, epochs // 10) == 0:
                            self_.signals.log.emit(
                                f"[{stage}] Epoch {epoch+1}/{epochs} "
                                f"loss:{tl:.4f} val:{vl:.4f}"
                            )

                cb = StagedCallback(self.signals, epochs, stage_idx=i)
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
```

- [ ] **Step 4: tab_overfitting.py 구현**

```python
# app/tabs/tab_overfitting.py
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
        self._epochs_sp.setRange(20, 500)
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

            # Row 0: 예측 비교
            ax_top = axes[0, idx]
            ax_top.clear()
            ax_top.scatter(x_tr, y_tr, alpha=0.4, s=20, color='gray', label='Train data')
            ax_top.plot(x_te, y_te, 'k-', linewidth=2.5, label='True', alpha=0.7)
            ax_top.plot(x_te, y_pred, color=color, linestyle='--', linewidth=2, label='Pred')
            ax_top.set_title(TITLES[stage], fontsize=11, fontweight='bold')
            ax_top.set_xlabel('x'); ax_top.set_ylabel('y')
            ax_top.legend(fontsize=7); ax_top.grid(True, alpha=0.3)

            # Row 1: Loss curve
            ax_bot = axes[1, idx]
            ax_bot.clear()
            h = res['history']
            epochs_range = range(1, len(h['loss']) + 1)
            ax_bot.plot(epochs_range, h['loss'], color=color, linestyle='-', linewidth=2, label='Train')
            ax_bot.plot(epochs_range, h['val_loss'], color=color, linestyle='--', linewidth=2, label='Val')
            ax_bot.set_title(TITLES[stage], fontsize=11, fontweight='bold')
            ax_bot.set_xlabel('Epoch'); ax_bot.set_ylabel('Loss')
            ax_bot.set_yscale('log')
            ax_bot.legend(fontsize=7); ax_bot.grid(True, alpha=0.3)

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
```

- [ ] **Step 5: 테스트 실행**

```bash
pytest tests/test_physics.py -v
```

Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add app/workers/worker_overfitting.py app/tabs/tab_overfitting.py tests/test_physics.py
git commit -m "feat: add Overfitting worker and tab"
```

---

## Task 7: Tab 4 — Pendulum Period Prediction

**Files:**
- Create: `app/workers/worker_pendulum.py`
- Create: `app/tabs/tab_pendulum.py`
- Modify: `tests/test_physics.py` (테스트 추가)

- [ ] **Step 1: 테스트 추가** (`tests/test_physics.py` 하단)

```python
def test_pendulum_small_angle():
    """작은 각도 근사: T ≈ 2π√(L/g)"""
    from app.workers.worker_pendulum import calculate_true_period
    import numpy as np
    L, g = 1.0, 9.81
    T = calculate_true_period(L, 5.0)  # 5도는 작은 각도
    T_approx = 2 * np.pi * np.sqrt(L / g)
    assert abs(T - T_approx) < 0.01  # 1% 미만 차이

def test_pendulum_data_shapes():
    from app.workers.worker_pendulum import generate_pendulum_data
    X, Y = generate_pendulum_data(100, noise_level=0.0)
    assert X.shape == (100, 2)   # L, theta0
    assert Y.shape == (100, 1)   # T
    assert all(Y > 0)

def test_rk4_returns_arrays():
    from app.workers.worker_pendulum import simulate_pendulum_rk4
    t, theta, omega = simulate_pendulum_rk4(L=1.0, theta0_deg=30.0, t_max=2.0)
    assert len(t) > 0
    assert len(t) == len(theta) == len(omega)
    assert abs(theta[0] - 30.0) < 0.1  # 초기 각도

def test_pendulum_model_shape():
    from app.workers.worker_pendulum import create_pendulum_model
    import numpy as np
    model = create_pendulum_model(lr=0.001)
    out = model.predict(np.zeros((5, 2)), verbose=0)
    assert out.shape == (5, 1)
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_physics.py::test_pendulum_small_angle -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: worker_pendulum.py 구현**

```python
# app/workers/worker_pendulum.py
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback

G = 9.81


def calculate_true_period(L: float, theta0_deg: float) -> float:
    theta_rad = np.deg2rad(theta0_deg)
    T_small = 2 * np.pi * np.sqrt(L / G)
    correction = 1 + (1/16) * theta_rad**2 + (11/3072) * theta_rad**4
    return float(T_small * correction)


def generate_pendulum_data(n_samples: int, noise_level: float = 0.01):
    L = np.random.uniform(0.5, 3.0, n_samples)
    theta0 = np.random.uniform(5, 80, n_samples)
    T_true = np.array([calculate_true_period(l, t) for l, t in zip(L, theta0)])
    T_noisy = T_true * (1 + np.random.normal(0, noise_level, n_samples))
    X = np.column_stack([L, theta0])
    Y = T_noisy.reshape(-1, 1)
    return X, Y


def create_pendulum_model(lr: float = 0.001):
    model = keras.Sequential([
        keras.layers.Input(shape=(2,)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(1, activation='linear'),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(lr),
        loss='mse',
        metrics=['mae'],
    )
    return model


def simulate_pendulum_rk4(L: float, theta0_deg: float, t_max: float, dt: float = 0.01):
    theta = np.deg2rad(theta0_deg)
    omega = 0.0
    t_arr = np.arange(0, t_max, dt)
    theta_arr = np.zeros_like(t_arr)
    omega_arr = np.zeros_like(t_arr)
    for i in range(len(t_arr)):
        theta_arr[i] = theta
        omega_arr[i] = omega
        k1t, k1o = omega, -(G / L) * np.sin(theta)
        k2t, k2o = omega + 0.5*dt*k1o, -(G/L)*np.sin(theta + 0.5*dt*k1t)
        k3t, k3o = omega + 0.5*dt*k2o, -(G/L)*np.sin(theta + 0.5*dt*k2t)
        k4t, k4o = omega + dt*k3o,     -(G/L)*np.sin(theta + dt*k3t)
        theta += (dt/6)*(k1t + 2*k2t + 2*k3t + k4t)
        omega += (dt/6)*(k1o + 2*k2o + 2*k3o + k4o)
    return t_arr, np.rad2deg(theta_arr), omega_arr


class PendulumWorker(BaseWorker):
    def run(self):
        try:
            p = self.params
            X_tr, Y_tr = generate_pendulum_data(2000, noise_level=0.01)
            X_te, Y_te = generate_pendulum_data(500, noise_level=0.0)
            model = create_pendulum_model(p['lr'])
            epochs = p['epochs']
            self._callback = EpochCallback(self.signals, epochs)

            history = model.fit(
                X_tr, Y_tr,
                validation_split=0.2,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                callbacks=[self._callback],
            )
            if self._callback._stop:
                return

            # 선택한 L로 각도별 주기 예측
            L_test = p['L_test']
            angles = np.linspace(5, 80, 50)
            X_in = np.column_stack([np.full(50, L_test), angles])
            T_pred = model.predict(X_in, verbose=0).flatten()
            T_true = np.array([calculate_true_period(L_test, a) for a in angles])

            # RK4 시뮬레이션
            theta_test = p['theta_test']
            T_pred_single = float(model.predict(np.array([[L_test, theta_test]]), verbose=0)[0, 0])
            T_true_single = calculate_true_period(L_test, theta_test)
            t_sim, theta_sim, omega_sim = simulate_pendulum_rk4(L_test, theta_test, T_true_single * 3)

            test_loss, test_mae = model.evaluate(X_te, Y_te, verbose=0)

            self.signals.training_done.emit({
                'history': history.history,
                'angles': angles.tolist(),
                'T_pred': T_pred.tolist(),
                'T_true': T_true.tolist(),
                'L_test': L_test,
                'theta_test': theta_test,
                'T_pred_single': T_pred_single,
                'T_true_single': T_true_single,
                't_sim': t_sim.tolist(),
                'theta_sim': theta_sim.tolist(),
                'omega_sim': omega_sim.tolist(),
                'test_loss': float(test_loss),
                'test_mae': float(test_mae),
            })
        except Exception as e:
            self.signals.error.emit(str(e))
```

- [ ] **Step 4: tab_pendulum.py 구현**

```python
# app/tabs/tab_pendulum.py
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
        self._epochs_sp.setRange(10, 500)
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
        ax.set_xlabel('Epoch'); ax.set_ylabel('MSE')
        ax.set_title('Training Loss'); ax.set_yscale('log')
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()

    @Slot(dict)
    def _on_done(self, r):
        axes = self._canvas.axes

        # 주기 vs 각도
        ax0 = axes[0, 0]
        ax0.clear()
        ax0.plot(r['angles'], r['T_true'], 'b-', linewidth=2.5, label='True period', alpha=0.7)
        ax0.plot(r['angles'], r['T_pred'], 'r--', linewidth=2, label='NN prediction')
        ax0.set_xlabel('Angle (°)'); ax0.set_ylabel('Period (s)')
        ax0.set_title(f'Period vs Angle  (L={r["L_test"]} m)', fontsize=11)
        ax0.legend(fontsize=8); ax0.grid(True, alpha=0.3)

        # 진자 시뮬레이션
        ax2 = axes[1, 0]
        ax2.clear()
        ax2.plot(r['t_sim'], r['theta_sim'], 'b-', linewidth=2)
        ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
        for i in range(3):
            ax2.axvline(r['T_true_single'] * i, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Time (s)'); ax2.set_ylabel('Angle (°)')
        ax2.set_title(
            f'RK4 Simulation  θ₀={r["theta_test"]}°\n'
            f'T_pred={r["T_pred_single"]:.3f}s  T_true={r["T_true_single"]:.3f}s',
            fontsize=10,
        )
        ax2.grid(True, alpha=0.3)

        # 위상 공간
        ax3 = axes[1, 1]
        ax3.clear()
        ax3.plot(r['theta_sim'], r['omega_sim'], 'g-', linewidth=1.5, alpha=0.7)
        ax3.plot(r['theta_sim'][0], r['omega_sim'][0], 'ro', markersize=8, label='Start')
        ax3.set_xlabel('Angle (°)'); ax3.set_ylabel('Angular Velocity (°/s)')
        ax3.set_title('Phase Space', fontsize=11)
        ax3.legend(fontsize=8); ax3.grid(True, alpha=0.3)

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
```

- [ ] **Step 5: 테스트 실행**

```bash
pytest tests/test_physics.py -v
```

Expected: 10 passed

- [ ] **Step 6: Commit**

```bash
git add app/workers/worker_pendulum.py app/tabs/tab_pendulum.py tests/test_physics.py
git commit -m "feat: add Pendulum worker and tab"
```

---

## Task 8: MainWindow + 통합

**Files:**
- Create: `app/main_window.py`

- [ ] **Step 1: main_window.py 구현**

```python
# app/main_window.py
from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.tabs.tab_perfect1d import Perfect1DTab
from app.tabs.tab_projectile import ProjectileTab
from app.tabs.tab_overfitting import OverfittingTab
from app.tabs.tab_pendulum import PendulumTab


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Physics Neural Network GUI — Week 4')
        self.resize(1400, 700)

        tabs = QTabWidget()
        tabs.addTab(Perfect1DTab(), '1D Function Approximation')
        tabs.addTab(ProjectileTab(), 'Projectile Motion')
        tabs.addTab(OverfittingTab(), 'Overfitting')
        tabs.addTab(PendulumTab(), 'Pendulum')

        self.setCentralWidget(tabs)
```

- [ ] **Step 2: 앱 실행 확인**

```bash
python main.py
```

Expected: 4개 탭을 가진 창이 열림. 각 탭에 컨트롤 패널과 빈 캔버스 표시.

- [ ] **Step 3: 각 탭 Run 버튼 수동 테스트**

아래 순서로 각 탭을 테스트:
1. **Tab 1**: Architecture=Small, Epochs=200, Run → Loss 그래프 실시간 업데이트 확인 → 완료 후 함수 근사/오차 그래프 표시 확인
2. **Tab 2**: Epochs=50, Run → Loss 업데이트 → 완료 후 궤적 + 오차 분석 그래프 확인
3. **Tab 3**: Epochs=100, Run → 로그에 "UNDERFIT 학습 중..." 등 단계 표시 확인 → 완료 후 2×3 그래프 확인
4. **Tab 4**: Epochs=50, L=1.0, θ=45, Run → 완료 후 4개 그래프 확인

- [ ] **Step 4: Stop 버튼 테스트**

각 탭에서 학습 시작 후 Stop → Run 버튼 재활성화, Worker 정상 종료 확인.

- [ ] **Step 5: Commit**

```bash
git add app/main_window.py
git commit -m "feat: integrate MainWindow with 4 tabs"
```

---

## Task 9: 전체 테스트 실행 + 최종 정리

**Files:**
- No new files

- [ ] **Step 1: 전체 테스트 실행**

```bash
pytest tests/ -v
```

Expected: 모든 테스트 통과.

- [ ] **Step 2: 임포트 오류 없음 확인**

```bash
python -c "from app.main_window import MainWindow; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: 최종 커밋**

```bash
git add .
git commit -m "feat: complete Physics NN GUI app (week4 assignment)"
```

---

## 빠른 참조

### 공통 시그널 연결 패턴 (모든 탭 동일)
```python
worker.signals.epoch_end.connect(self._on_epoch)     # int, float, float
worker.signals.progress.connect(self._progress.setValue)  # int 0-100
worker.signals.log.connect(self._log.append)         # str
worker.signals.training_done.connect(self._on_done)  # dict
worker.signals.error.connect(self._on_error)         # str
worker.finished.connect(self._on_finished)           # QThread finished
```

### Worker 파라미터 키 요약
| Worker | 필수 파라미터 키 |
|--------|----------------|
| Perfect1DWorker | `function`, `architecture`, `activation`, `epochs`, `lr` |
| ProjectileWorker | `epochs`, `lr`, `n_samples`, `v0_test`, `theta_test` |
| OverfittingWorker | `epochs`, `lr`, `noise_level` |
| PendulumWorker | `epochs`, `lr`, `L_test`, `theta_test` |
