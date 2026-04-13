# Physics NN GUI App — Design Spec
**Date:** 2026-04-06
**Status:** Approved

---

## Overview

Week 4 과제: TensorFlow로 작성된 4개의 물리 신경망 스크립트를 PySide6 탭 기반 GUI 앱으로 재구현한다. 각 탭에서 하이퍼파라미터를 조정하고 Run을 누르면 실시간으로 학습이 진행되며 에폭마다 그래프가 업데이트된다.

---

## Architecture

### Threading Model
- 학습은 `QThread` 기반 Worker에서 실행 (UI 블로킹 방지)
- 커스텀 Keras `Callback`(`EpochCallback`)이 `on_epoch_end`에서 `pyqtSignal` 발사
- UI 스레드는 시그널을 받아 matplotlib 캔버스 업데이트
- Stop 버튼: Worker에 중단 플래그 설정 → Callback이 `self.model.stop_training = True`

```
Worker (QThread)
  └─ model.fit(callbacks=[EpochCallback])
       └─ on_epoch_end()
            └─ epoch_signal.emit(epoch, train_loss, val_loss)
                 └─ Tab.on_epoch_update()  ← UI thread (Qt event loop)

  └─ training_done_signal.emit(results: dict)
       └─ Tab.on_training_complete()
```

### File Structure
```
week4_HW/
├── main.py
├── app/
│   ├── main_window.py           # QMainWindow + QTabWidget
│   ├── tabs/
│   │   ├── tab_perfect1d.py
│   │   ├── tab_projectile.py
│   │   ├── tab_overfitting.py
│   │   └── tab_pendulum.py
│   ├── workers/
│   │   ├── worker_base.py       # BaseWorker + EpochCallback
│   │   ├── worker_perfect1d.py
│   │   ├── worker_projectile.py
│   │   ├── worker_overfitting.py
│   │   └── worker_pendulum.py
│   └── utils/
│       └── plot_canvas.py       # MplCanvas(FigureCanvasQTAgg)
├── docs/
│   ├── PRD.md
│   └── TRD.md
└── requirements.txt
```

---

## Common Tab Layout

모든 탭은 좌(컨트롤) / 우(그래프) 2열 구조:

```
┌──────────────────┬──────────────────────────────────┐
│  Control Panel   │  Matplotlib Canvas               │
│  (300px fixed)   │  (stretch)                       │
│                  │                                  │
│  [파라미터 위젯]  │  실시간 업데이트 그래프           │
│  [Run] [Stop]    │                                  │
│  Progress bar    │                                  │
│  Log (QTextEdit) │                                  │
└──────────────────┴──────────────────────────────────┘
```

---

## Per-Tab Design

### Tab 1 — Perfect 1D Function Approximation

**Controls:**
- Function: `QComboBox` — sin(x) / cos(x)+0.5sin(2x) / x·sin(x)
- Architecture: `QComboBox` — Small[32] / Medium[64,64] / Large[128,128] / VeryLarge[128,128,64]
- Activation: `QComboBox` — tanh / relu
- Epochs: `QSpinBox` (500–5000, default 3000)
- Learning Rate: `QDoubleSpinBox` (0.0001–0.1, default 0.01)

**Plots (1×3 grid):**
1. Function Approximation: True vs Predicted + training scatter
2. Training Loss (log scale, real-time update per epoch)
3. Absolute Error (filled area)

---

### Tab 2 — Projectile Motion

**Controls:**
- Epochs: `QSpinBox` (50–500, default 100)
- Learning Rate: `QDoubleSpinBox` (default 0.001)
- n_samples: `QSpinBox` (500–5000, default 2000)
- Test v₀: `QSlider` 10–50 m/s
- Test θ: `QSlider` 20–70°

**Plots (2×2 grid):**
1. Trajectory: True vs NN (for selected v₀, θ)
2. Training/Validation Loss (real-time, log scale)
3. Error vs Launch Angle (v₀=30 fixed)
4. Error vs Initial Velocity (θ=45° fixed)

Plots 3 & 4 rendered after training completes.

---

### Tab 3 — Overfitting vs Underfitting

**Controls:**
- Epochs: `QSpinBox` (50–500, default 200)
- Learning Rate: `QDoubleSpinBox` (default 0.001)
- Noise Level: `QDoubleSpinBox` (0.0–1.0, default 0.3)

**Training sequence:** Underfit → Good Fit → Overfit (순차 실행, 로그에 단계 표시)

**Plots (2×3 grid):**
- Row 1: 모델별 예측 vs True function (Underfit / Good / Overfit)
- Row 2: 모델별 Train/Val Loss curve (3개 각각)

---

### Tab 4 — Pendulum Period Prediction

**Controls:**
- Epochs: `QSpinBox` (50–500, default 100)
- Learning Rate: `QDoubleSpinBox` (default 0.001)
- L (test): `QDoubleSpinBox` 0.5–3.0 m
- θ₀ (test): `QSpinBox` 5–80°

**Plots (2×2 grid):**
1. Period vs Angle: True vs NN prediction (for selected L)
2. Training/Validation Loss (real-time, log scale)
3. Pendulum Motion (RK4 simulation, angle vs time)
4. Phase Space (θ vs ω)

Plots 3 & 4 use RK4 simulation after training completes.

---

## Error Handling

- TF 임포트 실패 시 탭에 에러 메시지 표시
- Worker 예외는 `error_signal`로 UI에 전달, 로그에 출력
- Stop 도중 학습 재시작 가능 (Worker 재생성)

---

## Documents

- `docs/PRD.md`: 목적 / 기능 / 사용자 요구사항
- `docs/TRD.md`: 기술 스택 / 아키텍처 / 구현 세부사항
