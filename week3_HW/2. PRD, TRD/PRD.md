# PRD (Product Requirements Document)
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

### 1.1 목적

본 문서는 Week 3 신경망 기초 실습을 PySide6 기반 GUI 애플리케이션으로 재구현하기 위한 요구사항을 정의한다.

### 1.2 배경

기존 Week 3 실습은 터미널에서 실행되는 5개의 독립 Python 스크립트로 구성되어 있다. 파라미터를 변경하려면 소스 코드를 직접 수정해야 하며, 결과를 즉시 비교할 수 없다. 이를 단일 GUI 애플리케이션으로 통합하여, 슬라이더와 버튼으로 파라미터를 실시간 조작하고 그래프를 즉시 확인할 수 있도록 한다.

### 1.3 대상 사용자

부산대학교 "AI와 머신러닝" 수강생

---

## 2. 앱 구조

5개의 실습 모듈을 탭(Tab) 구조의 단일 앱으로 통합한다.

| 탭 | 모듈명 | 원본 스크립트 |
|----|--------|--------------|
| Tab 1 | Perceptron | 01_perceptron.py |
| Tab 2 | Activation Functions | 02_activation_functions.py |
| Tab 3 | Forward Propagation | 03_forward_propagation.py |
| Tab 4 | MLP / Backprop | 04_mlp_numpy.py |
| Tab 5 | Universal Approximation | 05_universal_approximation.py |

---

## 3. 기능 요구사항

### Tab 1 — Perceptron

- 게이트 종류 선택 (AND / OR / XOR), 라디오 버튼
- 학습률(η) 슬라이더: 0.01 ~ 1.0
- 에폭 수 입력: 10 ~ 500
- Train 버튼 클릭 시 학습 실행 및 결정 경계 그래프 갱신
- XOR 선택 시 선형 분리 불가 안내 문구 표시

### Tab 2 — Activation Functions

- Sigmoid / Tanh / ReLU / Leaky ReLU 동시 표시
- x 범위 슬라이더: -10 ~ +10
- Leaky ReLU의 alpha 슬라이더: 0.001 ~ 0.1
- 함수값 그래프 및 미분값 그래프 동시 출력

### Tab 3 — Forward Propagation

- 네트워크 구조 2-3-1 고정
- 랜덤 입력 생성 버튼 클릭 시 순전파 재계산
- 레이어별 pre-activation(z)값, post-activation(a)값 막대그래프 시각화
- 네트워크 다이어그램 표시

### Tab 4 — MLP / Backprop

- 학습률 슬라이더: 0.001 ~ 1.0
- 에폭 수 입력: 100 ~ 10,000
- 은닉층 뉴런 수 4개 고정
- Train 버튼 클릭 시 XOR 학습 실행 및 Loss 곡선 갱신
- 학습 완료 후 결정 경계 및 정확도 표시

### Tab 5 — Universal Approximation

- 근사 대상 함수 선택 (Sine / Step / Complex), 콤보박스
- 뉴런 수 3 / 10 / 50개 결과 동시 플롯
- 각 뉴런 수별 MSE 수치 표시
- 활성화 함수 tanh 고정

---

## 4. 화면 레이아웃

모든 탭은 좌우 분할 구조를 사용한다.

```
┌──────────────────────────────────────────────────────┐
│  [Tab1] [Tab2] [Tab3] [Tab4] [Tab5]                  │
├─────────────────┬────────────────────────────────────┤
│                 │                                    │
│  파라미터 패널  │          그래프 영역               │
│  (슬라이더,     │       (matplotlib 캔버스)          │
│   버튼, 입력창) │                                    │
│                 │                                    │
│    좌측 30%     │           우측 70%                 │
└─────────────────┴────────────────────────────────────┘
```

---

## 5. 비기능 요구사항

| 항목 | 요구사항 |
|------|---------|
| 응답성 | 파라미터 변경 후 그래프 갱신 3초 이내 |
| 호환성 | macOS / Windows / Linux |
| 실행 | `uv run main.py` 단일 명령으로 실행 |
| 해상도 | 1280×800 이상에서 정상 표시 |
| 의존성 | PySide6, NumPy, Matplotlib |

---

## 6. 제약 사항

- 학습 연산은 NumPy 기반 CPU 연산으로만 수행한다
- GPU 가속은 지원하지 않는다
- 교육용 데모 목적으로 소규모 데이터셋만 사용한다

---

## 7. 성공 기준

| 항목 | 목표 |
|------|------|
| 5개 탭 정상 실행 | 필수 |
| 그래프 갱신 속도 | 3초 이내 |
| Tab 4 XOR 정확도 | 100% (충분한 에폭 기준) |
| Tab 5 MSE (50 뉴런, Sine) | 0.01 이하 |
