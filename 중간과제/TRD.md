# TRD (Technical Requirements Document)

## 한끼 칼로리 트래커 (Meal Calorie Tracker)

**작성자:** 영이
**과목:** AI와 머신러닝 (부산대학교 물리학과)
**작성일:** 2026년 4월 21일

---

## 1. 기술 스택 개요

### 1.1 Frontend
- **프레임워크:** React + Vite
- **스타일링:** Tailwind CSS
- **차트 라이브러리:** Recharts (히스토리 그래프)
- **배포:** Vercel

### 1.2 Backend
- **프레임워크:** FastAPI (Python)
- **런타임:** Python 3.11+
- **패키지 관리:** uv
- **배포:** Railway 또는 로컬 실행

### 1.3 AI/ML
- **프레임워크:** TensorFlow / Keras
- **모델:** MobileNetV2 (Transfer Learning 기반)
- **학습 환경:** Google Colab (GPU) 또는 로컬

### 1.4 데이터 저장
- **영양 정보 DB:** JSON 파일 (백엔드 정적 파일, 음식명/칼로리/탄수화물/단백질/지방)
- **사용자 데이터(프로필 + 히스토리):** 브라우저 localStorage (클라이언트 전용)
- **저장 전략 근거:** 서버 DB 장애 리스크 회피, 로그인 불필요, 과제 시연 안정성 확보

---

## 2. 시스템 아키텍처

```
┌──────────────────────┐    HTTP/REST     ┌──────────────────┐
│  React Frontend      │ ───────────────► │  FastAPI Backend │
│  (Vercel)            │                  │  (Railway)       │
│                      │                  │                  │
│  ┌────────────────┐  │                  │  ┌────────────┐  │
│  │ localStorage   │  │                  │  │ CNN 모델   │  │
│  │ - 프로필       │  │                  │  │ MobileNet  │  │
│  │ - 식사 기록    │  │                  │  │ + Custom   │  │
│  │ - 목표량       │  │                  │  └────────────┘  │
│  └────────────────┘  │                  │        │         │
└──────────────────────┘                  │        ▼         │
                                          │  ┌────────────┐  │
                                          │  │ Nutrition  │  │
                                          │  │ DB (JSON)  │  │
                                          │  └────────────┘  │
                                          └──────────────────┘

핵심 원칙: 백엔드는 "순수한 AI 추론 서버"
         사용자 데이터는 모두 프론트엔드 localStorage에만 저장
```

---

## 3. AI 모델 상세 설계

### 3.1 Main Classifier (CNN)

**목적:** 업로드된 음식 사진을 20~30개 음식 카테고리 중 하나로 분류

**아키텍처:**
- Backbone: MobileNetV2 (ImageNet 사전학습, Frozen)
- Head:
  - GlobalAveragePooling2D
  - Dense(128, activation='relu')
  - Dropout(0.5) — Week 5에서 학습한 Overfitting 방지
  - Dense(N_CLASSES, activation='softmax')

**학습 설정:**
- Optimizer: Adam (learning_rate=0.001)
- Loss: Categorical Crossentropy
- Batch size: 32
- Epochs: 20 (Early Stopping 적용)
- Data Augmentation: 회전, 밝기, 좌우 반전 적용

**추론 출력:**
```json
{
  "predicted_class": "kimchi_stew",
  "confidence": 0.87,
  "top3": [
    { "class": "kimchi_stew", "score": 0.87 },
    { "class": "soybean_stew", "score": 0.09 },
    { "class": "sundubu", "score": 0.03 }
  ]
}
```

**신뢰도 임계값 처리:**
- confidence ≥ 0.7 → 바로 결과 표시
- 0.4 ≤ confidence < 0.7 → 결과 표시 + "정말 이거 맞아?" 확인 요청
- confidence < 0.4 → "인식 실패" 처리 → 힌트 모드 유도

### 3.2 Category-Specific Classifiers (힌트 모드)

**목적:** 사용자가 카테고리 힌트를 주면 해당 카테고리 내에서 재분류해 정확도 향상

**구현 방법 (두 가지 옵션):**

**Option A (권장):** Main Classifier의 출력 중 해당 카테고리 클래스만 필터링해 재정규화
```python
# 밥/면류에 속하는 클래스만 남기고 softmax 재적용
filtered_scores = {c: s for c, s in top_scores.items() if c in category_classes}
renormalized = softmax(filtered_scores)
```

**Option B:** 카테고리별 전용 Fine-tuned 모델 학습 (학습 시간 대비 효과 검토 후 결정)

**권장:** Option A로 시작, 시간 여유 있으면 Option B 확장.

### 3.3 Calorie Regression Model (Optional, P1)

**목적:** 음식 종류 + 사용자가 입력한 사이즈(소/중/대) → 정확한 칼로리 예측

**모델:** MLP (Week 3 활용)
- Input: [food_class_one_hot, size_one_hot]
- Hidden: Dense(32, relu) → Dense(16, relu)
- Output: Dense(1) — 회귀

**대안 (간단):** 음식별 기본 칼로리 × 사이즈 계수(0.7/1.0/1.3)로 단순 계산. MVP에선 이걸로 시작.

---

## 4. 데이터 파이프라인

### 4.1 학습 데이터 수집

**Primary Dataset:**
- Food-101 (101 classes, 101,000 images) — 공개 데이터셋
- 프로젝트 범위에 맞춰 20~30개 클래스 선별

**한식 보완 (선택):**
- AI Hub 한국 음식 이미지 데이터셋
- 구글 이미지 직접 크롤링 후 수동 정제 (소규모)

### 4.2 전처리
- 이미지 리사이즈: 224 × 224 (MobileNetV2 입력 규격)
- 정규화: pixel value / 255.0
- 학습 시 Data Augmentation:
  - Random Rotation (±20°)
  - Random Brightness (±0.2)
  - Random Horizontal Flip

### 4.3 Train/Validation/Test 분할
- Train: 70%
- Validation: 15%
- Test: 15%

---

## 5. API 설계

### 5.1 엔드포인트 목록

사용자 데이터는 localStorage에 저장되므로 백엔드 API는 AI 추론 및 영양 정보 조회에만 집중한다.

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/predict` | 음식 이미지 분류 (칼로리+탄단지 포함) |
| POST | `/api/predict-with-hint` | 카테고리 힌트 기반 재분류 |
| GET | `/api/nutrition/{food_class}` | 음식별 칼로리 + 탄단지 조회 |
| GET | `/api/categories` | 음식 카테고리 목록 조회 |
| GET | `/api/health` | 서버 상태 체크 |

### 5.2 주요 API 상세

**POST `/api/predict`**
- Request: `multipart/form-data` — image 파일
- Response:
```json
{
  "predicted_class": "kimchi_stew",
  "predicted_name_ko": "김치찌개",
  "confidence": 0.87,
  "nutrition": {
    "calorie": 150,
    "carbs_g": 10,
    "protein_g": 12,
    "fat_g": 8
  },
  "top3": [
    { "class": "kimchi_stew", "name_ko": "김치찌개", "score": 0.87 },
    { "class": "soybean_stew", "name_ko": "된장찌개", "score": 0.09 },
    { "class": "sundubu", "name_ko": "순두부찌개", "score": 0.03 }
  ],
  "is_confident": true
}
```

**POST `/api/predict-with-hint`**
- Request: `multipart/form-data` — image 파일 + category 필드
- Response: `/api/predict`와 동일 구조, 단 해당 카테고리 내에서 재분류된 결과

---

## 6. localStorage 데이터 스키마

사용자 데이터는 모두 브라우저 localStorage에 JSON 형태로 저장된다.

### 6.1 저장 키 구조

| 키 | 설명 |
|---|---|
| `meal_tracker:profiles` | 전체 프로필 목록 |
| `meal_tracker:active_profile_id` | 현재 선택된 프로필 ID |
| `meal_tracker:meals:{profile_id}` | 프로필별 식사 기록 |

### 6.2 프로필 스키마

```json
{
  "id": "profile_xxx",
  "name": "영이",
  "gender": "female",
  "age": 22,
  "height_cm": 165,
  "weight_kg": 55,
  "activity_level": "moderate",
  "bmr": 1358,
  "tdee": 2105,
  "goals": {
    "calorie": 2105,
    "carbs_g": 289,
    "protein_g": 55,
    "fat_g": 58
  },
  "created_at": "2026-04-22T10:00:00Z"
}
```

### 6.3 식사 기록 스키마

```json
[
  {
    "id": "meal_xxx",
    "date": "2026-04-22",
    "meal_type": "lunch",
    "items": [
      {
        "food_class": "rice",
        "name_ko": "쌀밥",
        "calorie": 300,
        "carbs_g": 66,
        "protein_g": 6,
        "fat_g": 1
      },
      {
        "food_class": "kimchi_stew",
        "name_ko": "김치찌개",
        "calorie": 150,
        "carbs_g": 10,
        "protein_g": 12,
        "fat_g": 8
      }
    ],
    "totals": {
      "calorie": 450,
      "carbs_g": 76,
      "protein_g": 18,
      "fat_g": 9
    },
    "created_at": "2026-04-22T12:30:00Z"
  }
]
```

### 6.4 클라이언트 측 계산 로직

**개인 맞춤 권장량 계산 (프로필 생성 시 1회 실행):**
```javascript
function calculateGoals(profile) {
  const { gender, age, height_cm, weight_kg, activity_level } = profile;

  // BMR - Harris-Benedict
  const bmr = gender === 'male'
    ? 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    : 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age);

  // TDEE
  const activityFactor = { low: 1.2, moderate: 1.55, high: 1.725 }[activity_level];
  const tdee = bmr * activityFactor;

  // 탄단지 목표
  return {
    bmr: Math.round(bmr),
    tdee: Math.round(tdee),
    goals: {
      calorie: Math.round(tdee),
      carbs_g: Math.round((tdee * 0.55) / 4),
      protein_g: Math.round(weight_kg * 1.0),
      fat_g: Math.round((tdee * 0.25) / 9)
    }
  };
}
```

**일일 누적 계산 (오늘 섭취량 합산):**
```javascript
function getDailySummary(profileId, date) {
  const meals = JSON.parse(
    localStorage.getItem(`meal_tracker:meals:${profileId}`) || '[]'
  );
  const todayMeals = meals.filter(m => m.date === date);

  return todayMeals.reduce((acc, meal) => ({
    calorie: acc.calorie + meal.totals.calorie,
    carbs_g: acc.carbs_g + meal.totals.carbs_g,
    protein_g: acc.protein_g + meal.totals.protein_g,
    fat_g: acc.fat_g + meal.totals.fat_g
  }), { calorie: 0, carbs_g: 0, protein_g: 0, fat_g: 0 });
}
```

**주간 추세 계산 (Week 1-2 선형 회귀 활용):**
```javascript
// 최근 7일 일일 칼로리 배열로 선형 회귀
// y = slope * x + intercept 계산
// 기울기로 "증가/감소/유지" 추세 판별
```

### 6.5 데이터 백업 및 복원 (P1)

사용자가 브라우저를 바꾸거나 데이터 유실에 대비해 JSON 내보내기/불러오기 기능 제공:

```javascript
// 내보내기
function exportData() {
  const data = {
    profiles: JSON.parse(localStorage.getItem('meal_tracker:profiles')),
    meals: { /* 모든 프로필의 식사 기록 */ }
  };
  // .json 파일로 다운로드
}

// 불러오기
function importData(jsonFile) {
  // 파일 읽어서 localStorage에 복원
}
```

---

## 7. Frontend 설계

### 7.1 페이지 구조

```
/profile        프로필 선택 / 생성 화면 (첫 진입 시)
/               홈 화면 (현재 프로필 기준 오늘 요약 + 업로드 진입점)
/upload         사진 업로드 및 인식 화면
/result         한끼 결과 + 목표 달성률 + 운동량 환산
/history        식사 히스토리 + 추세 그래프
/settings       프로필 수정, 데이터 백업/복원
```

### 7.2 주요 컴포넌트

- `<ProfileSetup />` — 최초 프로필 생성 폼
- `<ProfileSelector />` — 다중 프로필 선택 UI
- `<ImageUploader />` — 사진 선택 및 미리보기
- `<PredictionResult />` — 인식 결과 + 칼로리/탄단지 표시 + 확인/수정 UI
- `<HintSelector />` — 카테고리 선택 힌트 UI
- `<MealSummary />` — 총 칼로리 + 한끼 탄단지 총합 + 운동량 환산
- `<NutritionProgress />` — 일일 탄단지 목표 대비 진행 바
- `<MacroDonutChart />` — 탄단지 비율 도넛 차트 (P1)
- `<HistoryChart />` — Recharts 기반 추세 그래프
- `<DataBackup />` — JSON 내보내기/불러오기 UI

### 7.3 상태 관리
- React Context로 현재 활성 프로필 + 오늘 섭취 요약 전역 공유
- localStorage는 앱 시작 시 1회 로드 → 메모리 상태로 관리
- 식사 저장 시 메모리 + localStorage 동시 업데이트

---

## 8. 배포 계획

### 8.1 Frontend
- **Vercel**
- GitHub 연동 자동 배포
- 환경변수: `VITE_API_URL` (백엔드 URL)

### 8.2 Backend
- **Railway** (또는 로컬 실행)
- Docker 컨테이너 기반 배포
- 환경변수: `MODEL_PATH`, `NUTRITION_DB_PATH`
- 백엔드는 순수 AI 추론 서버이므로 재배포 시에도 사용자 데이터 손실 없음 (모든 사용자 데이터는 클라이언트 localStorage에 있음)

### 8.3 모델 파일
- 학습 완료된 `.h5` 또는 `.keras` 모델 파일 백엔드에 포함
- 모델 크기 최적화 필요 시 TensorFlow Lite 변환 고려

---

## 9. 개발 일정 (4월 22일 ~ 4월 29일)

| 날짜 | 작업 내용 |
|---|---|
| 4/22 (화) | PRD/TRD 제출, 데이터셋 확보, 학습 환경 세팅 |
| 4/23 (수) | CNN 모델 학습 1차 (Food-101 기반) |
| 4/24 (목) | 모델 튜닝 + FastAPI 백엔드 기본 구조 |
| 4/25 (금) | `/api/predict` 연동, 칼로리 DB 구축 |
| 4/26 (토) | React Frontend 기본 UI 구현 |
| 4/27 (일) | 힌트 모드 구현, 운동량 환산 로직 |
| 4/28 (월) | 히스토리 기능, 배포, 버그 수정 |
| 4/29 (화) | 유튜브 영상 제작 및 제출 |

---

## 10. 리스크 및 대응 방안

| 리스크 | 가능성 | 대응 방안 |
|---|---|---|
| CNN 정확도가 목표치 미달 | 중 | 힌트 모드로 보완, 클래스 수 축소 |
| 학습 시간 부족 | 중 | Colab GPU 활용, Epoch 축소 |
| 백엔드 배포 문제 | 낮음 | 로컬 실행으로 대체 (데모 영상은 로컬로 촬영) |
| 모델 파일 크기 과대 | 낮음 | MobileNet 사용으로 기본적으로 경량, 필요시 TFLite 변환 |
| 사용자 localStorage 삭제로 데이터 유실 | 낮음 | JSON 백업/복원 기능 제공 (P1) |
| localStorage 용량 초과 (5~10MB) | 매우 낮음 | 이미지는 저장하지 않고 메타데이터만 저장하므로 여유 충분 |

---

## 11. 수업 내용 활용 기술 매핑

| 수업 기술 | 구현 위치 |
|---|---|
| 선형 회귀 (Week 1-2) | 히스토리 주간 추세선 계산 (클라이언트 측 구현) |
| 커브 피팅 (Week 2) | 개인 맞춤 권장량 계산 공식 적용 |
| MLP (Week 3) | 칼로리 회귀 예측 모델 (P1 옵션) |
| 역전파 (Week 3) | CNN 학습 과정 전반 |
| Overfitting 방지 (Week 4) | Dropout, Early Stopping, Data Augmentation |
| CNN (Week 5) | 음식 이미지 분류 메인 모델 |
| Dropout (Week 5) | Custom Head에 적용 |
| Transfer Learning (Week 5) | MobileNetV2 사전학습 가중치 활용 |

---

## 12. GitHub Repository 구조 (예정)

```
meal-calorie-tracker/
├── README.md
├── PRD.md
├── TRD.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── model.py
│   │   └── nutrition_db.json
│   ├── pyproject.toml
│   └── Dockerfile
├── ml/
│   ├── train.ipynb
│   ├── data_prep.py
│   └── models/
└── docs/
    └── architecture.png
```
