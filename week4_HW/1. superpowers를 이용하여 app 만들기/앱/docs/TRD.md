# TRD — Physics Neural Network GUI App
**Version:** 1.0
**Date:** 2026-04-06
**Course:** AI와 머신러닝 — Week 4 과제

---

## 1. 기술 스택 (Tech Stack)

| 영역 | 라이브러리 | 버전 | 용도 |
|------|-----------|------|------|
| GUI | PySide6 | ≥6.5 | 윈도우, 위젯, 이벤트 루프 |
| ML | TensorFlow/Keras | ≥2.12 | 신경망 모델 정의 및 학습 |
| 시각화 | matplotlib | ≥3.7 | 그래프 렌더링 (FigureCanvasQTAgg) |
| 수치 계산 | numpy | ≥1.23 | 데이터 생성, 수식 계산 |
| Python | Python | ≥3.10 | 런타임 |

---

## 2. 아키텍처 (Architecture)

### 2.1 레이어 구조

```
┌─────────────────────────────────────────────┐
│               main.py                       │
│         QApplication 초기화                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           MainWindow (QMainWindow)          │
│           QTabWidget (4 tabs)               │
└──┬──────────┬──────────┬──────────┬─────────┘
   │          │          │          │
Tab1        Tab2        Tab3        Tab4
   │
┌──▼──────────────────┐    ┌───────────────────┐
│  Tab Widget          │    │  Worker (QThread)  │
│  - Control Panel     │◄───│  - model.fit()     │
│  - MplCanvas         │    │  - EpochCallback   │
│  - Log / ProgressBar │    │  - pyqtSignal      │
└──────────────────────┘    └───────────────────┘
```

### 2.2 스레드-시그널 설계

학습은 반드시 메인(UI) 스레드 외부에서 실행되어야 한다.

```python
# worker_base.py
class EpochCallback(keras.callbacks.Callback):
    def __init__(self, signals):
        self.signals = signals
        self._stop = False

    def on_epoch_end(self, epoch, logs=None):
        if self._stop:
            self.model.stop_training = True
            return
        self.signals.epoch_end.emit(epoch, logs['loss'],
                                     logs.get('val_loss', 0.0))

class WorkerSignals(QObject):
    epoch_end = Signal(int, float, float)   # epoch, train_loss, val_loss
    training_done = Signal(dict)            # 최종 결과
    error = Signal(str)                     # 오류 메시지

class BaseWorker(QThread):
    def __init__(self, params: dict):
        super().__init__()
        self.params = params
        self.signals = WorkerSignals()
        self._callback = EpochCallback(self.signals)

    def stop(self):
        self._callback._stop = True
```

---

## 3. 컴포넌트 상세 (Component Details)

### 3.1 `utils/plot_canvas.py` — MplCanvas

```python
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, nrows, ncols, figsize=(10, 6)):
        fig, self.axes = plt.subplots(nrows, ncols, figsize=figsize)
        super().__init__(fig)
```

- 모든 탭에서 공유하는 matplotlib 임베딩 위젯
- `draw_idle()` 호출로 실시간 업데이트 (UI 블로킹 최소화)

### 3.2 탭 공통 구조

각 탭(`BasePysicsTab`)은 다음을 구현:
- `_build_controls()`: 좌측 컨트롤 패널 위젯 생성
- `_build_canvas()`: 우측 matplotlib 캔버스 생성
- `on_run()`: Worker 생성 및 시그널 연결 후 `start()`
- `on_stop()`: Worker에 `stop()` 호출
- `on_epoch_update(epoch, train_loss, val_loss)`: Loss curve 실시간 업데이트
- `on_training_complete(results)`: 최종 결과 그래프 렌더링

### 3.3 탭별 모델 구조

#### Tab 1 — Perfect 1D
```
Input(1) → Dense(N, tanh/relu) × k layers → Dense(1, linear)
Architecture 선택에 따라 N, k 변경:
  Small:     [32]
  Medium:    [64, 64]
  Large:     [128, 128]
  VeryLarge: [128, 128, 64]
Optimizer: Adam(lr), Loss: MSE
```

#### Tab 2 — Projectile Motion
```
Input(3: v0, theta, t)
→ Dense(128, relu) → Dropout(0.1)
→ Dense(64, relu)  → Dropout(0.1)
→ Dense(32, relu)  → Dropout(0.1)
→ Dense(2: x, y, linear)
Optimizer: Adam(lr), Loss: MSE, Metrics: MAE
validation_split: 0.2
```

#### Tab 3 — Overfitting
```
Underfit:  Input(1) → Dense(4, relu) → Dense(1)
Good Fit:  Input(1) → Dense(32, relu) → Dropout(0.2) → Dense(16, relu) → Dropout(0.2) → Dense(1)
Overfit:   Input(1) → Dense(256, relu) → Dense(128) → Dense(64) → Dense(32) → Dense(1)
순차 학습: Underfit 완료 → Good 완료 → Overfit 완료 (각각 별도 Worker)
```

#### Tab 4 — Pendulum
```
Input(2: L, theta0)
→ Dense(64, relu) → Dropout(0.1)
→ Dense(32, relu) → Dropout(0.1)
→ Dense(16, relu) → Dropout(0.1)
→ Dense(1: T, linear)
Optimizer: Adam(lr), Loss: MSE, Metrics: MAE, MAPE
validation_split: 0.2

RK4 시뮬레이션 (학습 후):
  d²θ/dt² = -(g/L)sin(θ),  dt=0.01s
```

---

## 4. 데이터 흐름 (Data Flow)

### Tab 2 데이터 생성
```
generate_projectile_data(n_samples, noise_level)
  v0 ~ Uniform(10, 50), theta ~ Uniform(20, 70)
  x = v0·cos(θ)·t,  y = v0·sin(θ)·t - 0.5·g·t²
  y<0 필터링 후 (v0, theta, t) → (x, y) 매핑
```

### Tab 4 데이터 생성
```
generate_pendulum_data(n_samples, noise_level)
  L ~ Uniform(0.5, 3.0), theta0 ~ Uniform(5, 80)
  T = 2π√(L/g) · (1 + θ²/16 + 11θ⁴/3072)  [타원 적분 근사]
  T_noisy = T · (1 + N(0, noise_level))
```

---

## 5. 파일별 책임 (File Responsibilities)

| 파일 | 책임 |
|------|------|
| `main.py` | `QApplication` 생성, `MainWindow` 표시 |
| `app/main_window.py` | `QMainWindow`, `QTabWidget`, 4개 탭 인스턴스 생성 |
| `app/workers/worker_base.py` | `EpochCallback`, `WorkerSignals`, `BaseWorker` |
| `app/workers/worker_*.py` | 탭별 모델 정의 및 `run()` 구현 |
| `app/tabs/tab_*.py` | 탭 UI 레이아웃, 시그널 연결, 그래프 렌더링 |
| `app/utils/plot_canvas.py` | `MplCanvas` (재사용 matplotlib 위젯) |
| `docs/PRD.md` | 제품 요구사항 |
| `docs/TRD.md` | 기술 설계 (본 문서) |
| `requirements.txt` | 의존성 목록 |

---

## 6. 의존성 (requirements.txt)

```
pyside6>=6.5.0
tensorflow>=2.12.0
matplotlib>=3.7.0
numpy>=1.23.0
```

---

## 7. 실행 방법

```bash
cd week4_HW
pip install -r requirements.txt
python main.py
```
