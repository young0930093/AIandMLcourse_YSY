# Week 9 Homework — 고전 역학 시뮬레이션

**202312140 윤서영**

## HTML 문서 생성 방식 비교

이 폴더에서는 Markdown을 HTML로 변환하는 두 가지 방식을 모두 시도해보았습니다.

| 방식 | 결과물 | 설명 |
|------|--------|------|
| 직접 변환 (markdown 라이브러리) | `README.html` | README.md를 Python markdown 라이브러리로 직접 HTML로 변환 |
| Sphinx 빌드 | `sphinx_docs/_build/html/` | sphinx-quickstart로 초기화 후 `make html`로 빌드한 공식 문서 |

- **README.html**: 단순 변환 방식. 별도 도구 없이 파일 하나로 빠르게 HTML 생성 가능
- **sphinx_docs/**: Sphinx를 사용한 방식. 목차, 검색, 사이드바 등 문서화 도구 기능 포함

---

## 개요

Week 9 실습 과제: 고전 역학의 핵심 개념들을 수치 시뮬레이션으로 구현하고 분석

## 실습 목록

| Lab | 주제 | 핵심 결과 |
|-----|------|---------|
| Lab 1 | Euler vs RK4 수치 적분 비교 | RK4가 Euler보다 2.8×10²⁸배 정확 |
| Lab 2 | 행성 운동 & 케플러 법칙 검증 | T²/a³ = 0.9994 (오차 0.06%) |
| Lab 3 | 이중 진자 혼돈 시스템 | 리아푸노프 지수 λ=0.556, 예측가능시간 1.8초 |
| Lab 4 | 뉴턴/라그랑지안/해밀토니안 비교 | 세 방법 차이 < 1e-10 rad |
| Ex 1 | 3체 문제 시뮬레이션 | 에너지 오차 0.000000% |
| Ex 2 | NumPy 코드 최적화 | 최대 2,290배 가속 |

## 파일 구조

```
week9_HW/
├── README.md               # 이 파일
├── README.html             # 직접 변환 방식 HTML
├── week9_analysis.md       # 상세 실행 결과 분석 보고서
├── sphinx_docs/            # Sphinx 빌드 방식 HTML 문서
│   ├── conf.py
│   ├── index.rst
│   └── _build/html/        # make html 빌드 결과
└── outputs/                # 시뮬레이션 결과 그래프
    ├── 01_euler_vs_rk4.png
    ├── 01_error_analysis.png
    ├── 02_solar_system.png
    ├── 02_kepler_laws.png
    ├── 03_double_pendulum.png
    ├── 03_chaos_analysis.png
    ├── 04_comparison.png
    └── ...
```

## 상세 분석

자세한 실행 결과 및 분석은 [week9_analysis.md](week9_analysis.md)를 참고
