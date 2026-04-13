# TRD (Technical Requirements Document)
## Neural Networks Explorer — Week 3 GUI Application

| 항목 | 내용 |
|------|------|
| 과목 | AI와 머신러닝 |
| 소속 | 부산대학교 물리학과 |
| 학번 | 202312140 |
| 작성자 | 윤서영 |
| 작성일 | 2026년 3월 31일 |

---

## 1. 개요

본 문서는 PRD에서 정의한 Neural Networks Explorer의 기능 요구사항을 실제 코드 구조, 클래스 설계, 데이터 흐름으로 구체화한 기술 설계 문서이다.

---

## 2. 기술 스택

| 구분 | 기술 | 용도 |
|------|------|------|
| 언어 | Python 3.12 | 전체 애플리케이션 |
| GUI 프레임워크 | PySide6 | 윈도우 및 위젯 |
| 그래프 | Matplotlib | FigureCanvas 임베드 |
| 수치 연산 | NumPy | 신경망 연산 |
| 패키지 관리 | uv | 의존성 관리 및 실행 |

### 의존성 설정 (pyproject.toml)

```toml
[project]
dependencies = [
    "PySide6>=6.5",
    "matplotlib>=3.7",
    "numpy>=1.24",
]
```

### 실행

```bash
uv run main.py
```

---

## 3. 디렉토리 구조

```
week3_gui/
├── main.py                    # 진입점, QApplication 실행
├── app/
│   ├── main_window.py         # QMainWindow + QTabWidget
│   └── tabs/
│       ├── tab_perceptron.py
│       ├── tab_activation.py
│       ├── tab_forward.py
│       ├── tab_mlp.py
│       └── tab_universal.py
├── models/
│   ├── perceptron.py          # 01_perceptron.py 로직 이식
│   ├── activations.py         # 02_activation_functions.py 로직 이식
│   ├── forward_prop.py        # 03_forward_propagation.py 로직 이식
│   ├── mlp.py                 # 04_mlp_numpy.py 로직 이식
│   └── universal.py           # 05_universal_approximation.py 로직 이식
└── widgets/
    └── plot_canvas.py         # matplotlib FigureCanvas 공통 래퍼
```

---

## 4. 아키텍처 설계

### 4.1 레이어 분리 원칙

Model-View 패턴을 따른다.

- `models/` — 기존 스크립트의 NumPy 연산 로직만 담는다. Qt 의존성을 갖지 않는다.
- `app/tabs/` — GUI 레이어. 모델을 import하여 결과를 시각화한다.
- 이 구조 덕분에 기존 .py 파일 코드를 `models/`에 거의 그대로 이식할 수 있다.

### 4.2 데이터 흐름

```
사용자 조작 (슬라이더 / 버튼)
        ↓
Qt 시그널 (valueChanged / clicked)
        ↓
Tab 클래스의 슬롯 메서드
        ↓
models/ 함수 호출 (NumPy 연산)
        ↓
PlotCanvas에 결과 전달
        ↓
그래프 갱신 (axes.clear → redraw)
```

---

## 5. 클래스 설계

### 5.1 MainWindow

```python
class MainWindow(QMainWindow):
    def __init__(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(PerceptronTab(),  "Perceptron")
        self.tab_widget.addTab(ActivationTab(),  "Activation Functions")
        self.tab_widget.addTab(ForwardTab(),     "Forward Propagation")
        self.tab_widget.addTab(MLPTab(),         "MLP / Backprop")
        self.tab_widget.addTab(UniversalTab(),   "Universal Approximation")
```

### 5.2 PlotCanvas (공통 위젯)

```python
class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, nrows=1, ncols=1):
        self.fig, self.axes = plt.subplots(nrows, ncols)
        super().__init__(self.fig)

    def clear(self):
        for ax in np.array(self.axes).flat:
            ax.clear()

    def draw_safe(self):
        self.fig.tight_layout()
        self.draw()
```

### 5.3 탭별 클래스 구조

| 클래스 | 주요 시그널/슬롯 | 사용 모델 |
|--------|----------------|----------|
| PerceptronTab | gate_changed, train_clicked → on_train() | models/perceptron.py |
| ActivationTab | slider.valueChanged → on_update() | models/activations.py |
| ForwardTab | randomize_clicked → on_forward() | models/forward_prop.py |
| MLPTab | train_clicked → on_train() / QThread | models/mlp.py |
| UniversalTab | func_changed → on_update() | models/universal.py |

### 5.4 학습 스레드 처리 (Tab 4)

MLP 학습은 최대 10,000 에폭으로 UI를 블로킹할 수 있다. QThread를 사용하여 백그라운드에서 학습하고, 시그널로 진행 상황을 메인 스레드에 전달한다.

```python
class TrainWorker(QThread):
    progress = Signal(int, float)   # epoch, loss
    finished = Signal(object)       # 최종 모델

    def run(self):
        for epoch, loss in self.model.train_step():
            self.progress.emit(epoch, loss)
        self.finished.emit(self.model)
```

---

## 6. 모듈별 구현 명세

### models/perceptron.py

- 기존 `01_perceptron.py`의 `Perceptron` 클래스 이식
- matplotlib 의존성 제거, 순수 NumPy만 사용
- `train()` → (weights_history, error_history) 반환
- `get_decision_boundary()` → (xx, yy, Z) meshgrid 반환

### models/activations.py

- sigmoid / tanh / relu / leaky_relu 함수 및 각 미분 함수 정의
- `get_all(x_range, alpha)` → 전체 함수값/미분값 dict 반환

### models/forward_prop.py

- 기존 `03_forward_propagation.py`의 `SimpleNetwork` 클래스 이식
- 네트워크 구조 2-3-1 고정
- `forward(X)` → z1, a1, z2, a2 반환

### models/mlp.py

- 기존 `04_mlp_numpy.py`의 `MLP` 클래스 이식
- `train_step()` → generator로 (epoch, loss) yield하여 실시간 진행 가능
- 은닉층 뉴런 수 4개 고정

### models/universal.py

- 기존 `05_universal_approximation.py`의 `UniversalApproximator` 클래스 이식
- `approximate(func_name, n_neurons)` → (x, y_true, y_pred, mse) 반환
- 지원 함수: 'sine', 'step', 'complex'
- 활성화 함수 tanh 고정

---

## 7. UI 위젯 명세

| 탭 | 위젯 종류 | 범위 / 옵션 | 기본값 |
|----|----------|------------|--------|
| Perceptron | QButtonGroup | AND / OR / XOR | AND |
| Perceptron | QSlider (학습률 η) | 0.01 ~ 1.0 | 0.1 |
| Perceptron | QSpinBox (에폭) | 10 ~ 500 | 100 |
| Activation | QSlider (x 범위) | -10 ~ +10 | -5 ~ +5 |
| Activation | QDoubleSpinBox (alpha) | 0.001 ~ 0.1 | 0.01 |
| Forward | QPushButton (랜덤 입력) | — | — |
| MLP | QSlider (학습률) | 0.001 ~ 1.0 | 0.01 |
| MLP | QSpinBox (에폭) | 100 ~ 10,000 | 5,000 |
| Universal | QComboBox (함수 선택) | sine / step / complex | sine |

---

## 8. 테스트 계획

| ID | 항목 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-01 | AND 게이트 학습 | η=0.1, epoch=100 | 정확도 100%, 선형 결정 경계 |
| TC-02 | XOR 게이트 선택 | 게이트=XOR | 선형 분리 불가 안내 문구 표시 |
| TC-03 | ReLU gradient | x=-5 ~ +5 | x>0: gradient=1, x≤0: gradient=0 |
| TC-04 | MLP XOR 수렴 | η=0.5, epoch=10,000 | Loss < 0.01, 정확도 100% |
| TC-05 | UAT 50 뉴런 | 함수=sine, n=50 | MSE < 0.01 |
| TC-06 | 그래프 갱신 속도 | 임의 파라미터 변경 | 3초 이내 갱신 |

---

## 9. 구현 순서

| 단계 | 작업 | 비고 |
|------|------|------|
| Step 1 | models/ 폴더 생성, 기존 스크립트 로직 이식 | matplotlib 제거, NumPy만 유지 |
| Step 2 | PlotCanvas 위젯 구현 및 단독 테스트 | FigureCanvas 정상 렌더링 확인 |
| Step 3 | MainWindow + QTabWidget 뼈대 구성 | 빈 탭 5개 동작 확인 |
| Step 4 | Tab 1~3 구현 | 단순 렌더링 위주 |
| Step 5 | Tab 4 구현 (MLP + QThread) | 학습 중 UI 블로킹 방지 |
| Step 6 | Tab 5 구현 | 3개 뉴런 수 동시 플롯 |
| Step 7 | 전체 통합 테스트 | TC-01 ~ TC-06 확인 |
