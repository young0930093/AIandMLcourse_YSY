# RESULT.md
## Neural Networks Explorer — 실행 결과 보고서

| 항목 | 내용 |
|------|------|
| 과목 | AI와 머신러닝 |
| 소속 | 부산대학교 물리학과 |
| 학번 | 202312140 |
| 작성자 | 윤서영 |
| 작성일 | 2026년 3월 31일 |

---

## 1. 실행 방법

### 환경 설정

```bash
cd "3. pyside6 app"
uv run main.py
```

### 요구 패키지

```
PySide6 >= 6.5
numpy >= 1.24
matplotlib >= 3.7
```

---

## 2. 실행 결과

### Tab 1 — Perceptron

- AND / OR / XOR 게이트 학습 결과를 결정 경계 그래프로 시각화
- AND, OR: 직선 하나로 분리 가능 → 퍼셉트론 학습 성공
- XOR: 단일 퍼셉트론으로 선형 분리 불가능함을 시각적으로 확인
- 학습률(η), 에폭 수를 슬라이더/입력창으로 실시간 조절 가능

**실행 조건:** η = 0.10, Epochs = 100

---

### Tab 2 — Activation Functions

- Sigmoid, Tanh, ReLU, Leaky ReLU 4가지 함수 및 각 미분값 동시 표시
- x 범위 슬라이더, Leaky ReLU alpha 값 실시간 조절 가능
- Sigmoid vs Tanh 비교: Tanh가 0 중심으로 음수 출력 가능함을 확인
- ReLU vs Leaky ReLU 비교: Leaky ReLU가 음수 영역에서도 기울기 유지함을 확인

**실행 조건:** X Range = ±5, Alpha = 0.010

---

### Tab 3 — Forward Propagation

- 2-3-1 구조 신경망의 순전파 과정 단계별 시각화
- 랜덤 입력 생성 버튼으로 매번 새로운 입력값으로 계산 가능
- Layer 1: z1(pre-ReLU) vs a1(post-ReLU) 막대그래프
- Layer 2: z2(pre-Sigmoid) vs a2(post-Sigmoid) 수평 막대그래프
- Forward Pass Summary: 각 레이어 수식 및 수치 텍스트로 표시

**실행 예시:** 입력 = [0.215, -0.659] → 출력 = 0.4881

---

### Tab 4 — MLP / Backprop

- XOR 문제를 MLP(은닉층 4개 뉴런)로 학습
- Training Loss, Decision Boundary, Hidden Activations 3가지 그래프 표시
- QThread 활용으로 학습 중에도 UI 블로킹 없이 진행 바 표시

**실행 조건:** Learning Rate = 0.50, Epochs = 5000

| 항목 | 결과 |
|------|------|
| 최종 Loss | 0.000012 |
| 정확도 | 100.0% |

---

### Tab 5 — Universal Approximation

- Sine / Step / Complex 함수를 뉴런 수 3 / 10 / 50으로 근사
- 활성화 함수 tanh 고정, 각 뉴런 수별 MSE 수치 표시

**초기 설정 문제 및 수정 사항:**

초기 설정(학습률 0.01, 에폭 5000)에서 50 neurons의 MSE가 0.1980으로 높게 나왔다. 학습률을 0.05로, 에폭을 10000으로 조정한 결과 정상적으로 수렴하였다.

**실행 조건:** 함수 = Sine, Epochs = 10000, lr = 0.05 (전 뉴런 동일)

| 뉴런 수 | MSE |
|--------|-----|
| 3 neurons | 0.0056 |
| 10 neurons | 0.0031 |
| 50 neurons | 0.0026 |

뉴런 수가 증가할수록 MSE가 감소하며 근사 정확도가 향상됨을 확인하였다. 전 뉴런 구성에서 목표치(MSE 0.01 이하)를 달성하였다.

---

## 3. 전체 결과 요약

| 탭 | 항목 | 결과 |
|----|------|------|
| Tab 1 | AND/OR 학습 | 성공 |
| Tab 1 | XOR 선형 분리 불가 확인 | 확인 |
| Tab 2 | 4가지 활성화 함수 시각화 | 정상 |
| Tab 3 | 순전파 단계별 시각화 | 정상 |
| Tab 4 | XOR 학습 정확도 | 100% |
| Tab 4 | 최종 Loss | 0.000012 |
| Tab 5 | MSE (50 neurons, Sine) | 0.0026 |

5개 탭 모두 정상 실행되었으며, 모든 성공 기준을 달성하였다.
