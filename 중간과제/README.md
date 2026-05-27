# 🍱 Meal Calorie Tracker

> Snap a photo of your meal — AI identifies the dish and breaks down the nutrition instantly.

**Meal Calorie Tracker** is a full-stack web application that uses a fine-tuned **MobileNetV2** CNN to recognize food from photos and automatically retrieves calorie and macronutrient (carbs / protein / fat) data. Beyond simple calorie counting, it computes personalized daily goals from your body metrics and shows you exactly how much exercise it would take to burn off what you just ate.

**Live Demo**
- 🌐 Frontend (Vercel): https://frontend-two-chi-98.vercel.app
- 🔧 Backend API docs (Railway): https://meal-calorie-tracker-backend-production.up.railway.app/docs
- 📦 GitHub: https://github.com/young0930093/meal-calorie-tracker

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [AI Model](#ai-model)
4. [Getting Started](#getting-started)
5. [API Reference](#api-reference)
6. [Recognizable Foods (101 classes)](#recognizable-foods-101-classes)
7. [Project Structure](#project-structure)
8. [Roadmap](#roadmap)
9. [Known Limitations](#known-limitations)

---

## Features

### 🤖 AI Food Recognition — 5-Stage Upload Flow

```
① ready      →  Take / select a photo
② predicting →  MobileNetV2 inference (server-side)
③ confirm    →  Review result — ✓ Correct  /  ✗ Wrong
④ hint       →  Pick a food category → model re-classifies within that subset
⑤ manual     →  Search / select manually if AI keeps missing
```

### 🧮 Nutrition Analysis
- Per-dish: **kcal / carbs / protein / fat (g)**
- Meal-level totals (breakfast / lunch / dinner / snack)
- Daily cumulative progress against your personal targets
- Macro ratio donut chart

### 👤 Multi-Profile Support
- Create profiles for family members (name, gender, age, height, weight, activity level)
- **BMR** via Mifflin-St Jeor formula:
  - Male: `(10 × weight) + (6.25 × height) - (5 × age) + 5`
  - Female: `(10 × weight) + (6.25 × height) - (5 × age) - 161`
- **TDEE** = BMR × activity factor (1.2 – 1.9)
- Switch between profiles at any time

### 🏃 Exercise Equivalents
Converts total meal calories to approximate workout duration using body-weight-adjusted estimates: jogging, walking, swimming, cycling, jump rope.

### 📊 History
- Date-based meal log
- Daily calorie ring chart and macro breakdown
- Breakfast / lunch / dinner / snack separation

### 🔐 Google OAuth Login
Sign in with your Google account — no separate registration needed. Mock login also available for development.

### 💳 In-App Purchase (Stripe)
Buy additional profile slots (₩2,900) via Stripe Test Mode.

---

## Tech Stack

### Frontend
| Technology | Role |
|---|---|
| React 19 | UI component framework |
| Vite 8 | Build tool & dev server |
| Tailwind CSS v4 | Utility-first styling |
| React Router v7 | Client-side routing |
| `@react-oauth/google` | Google OAuth 2.0 |
| `@stripe/stripe-js` | Stripe payment UI |
| Context API | Global state (profiles, meal history) |
| localStorage | Client-side data persistence |

### Backend
| Technology | Role |
|---|---|
| Python 3.12 | Server language |
| FastAPI | High-performance REST API framework |
| uv | Ultra-fast Python package manager |
| uvicorn | ASGI server |
| python-multipart | File upload handling |
| python-dotenv | Environment variable management |
| Stripe SDK | Payment processing |

### AI / ML
| Technology | Role |
|---|---|
| TensorFlow 2.16 | Deep learning framework |
| Keras | Model API |
| MobileNetV2 | Pre-trained image classification backbone |
| Transfer Learning | ImageNet → Food-101 knowledge transfer |
| Mixed Precision (float16) | GPU memory savings & faster training |
| Data Augmentation | Generalization (flip, brightness, contrast, saturation, hue) |
| Pillow / NumPy | Image preprocessing |
| Food-101 Dataset | 101 food classes, 101,000 training images |

### Infrastructure
| Technology | Role |
|---|---|
| Vercel | Frontend CDN deployment |
| Railway | Backend cloud deployment (Nixpacks build) |
| GitHub | Source control & CI trigger |
| Kaggle (P100 GPU) | Model training environment |

---

## AI Model

### Dataset — Food-101

| Item | Details |
|---|---|
| Classes | 101 food categories |
| Total images | 101,000 |
| Training set | 75,750 images (750 / class) |
| Test set | 25,250 images (250 / class) |
| Input size | Resized to **128 × 128** during training |

### Architecture — MobileNetV2 + Custom Head

```
Input (128 × 128 × 3)
    ↓
MobileNetV2 Backbone  (ImageNet pre-trained, fully frozen)
    ↓
GlobalAveragePooling2D
    ↓
Dense(256, relu)
    ↓
Dropout(0.5)          ← prevents overfitting
    ↓
Dense(101, dtype='float32')
    ↓
Softmax (101-class probability distribution)
```

**Why MobileNetV2?**
- Lightweight (~13 MB saved model) — low memory footprint on Railway
- Depthwise Separable Convolution cuts FLOPs dramatically
- Generalizes well on CPU-only inference servers
- ImageNet pre-training already encodes rich visual features (edges, textures, shapes)

### Training Configuration

| Hyperparameter | Value | Reason |
|---|---|---|
| `IMG_SIZE` | 128 × 128 | Fit within Kaggle P100 16 GB VRAM |
| `BATCH_SIZE` | 16 | Avoid `ResourceExhaustedError` |
| Optimizer | Adam (lr = 1e-3) | Fast convergence |
| Loss | Sparse Categorical Crossentropy | Integer-label multi-class |
| Max Epochs | 10 (EarlyStopping patience = 3) | Auto-stop when val_accuracy plateaus |
| Mixed Precision | float16 compute + float32 output | GPU speed + numerical stability |
| Data Augmentation | flip, brightness, contrast, saturation, hue | Improved generalization |
| LR Schedule | `ReduceLROnPlateau` (× 0.5 on stall) | Fine-grained convergence |
| Checkpoint | `ModelCheckpoint` on `val_accuracy` | Only best weights saved |

### Inference Pipeline

```python
image_bytes
  → Pillow.open()  → RGB convert  → resize(128, 128)
  → np.array(float32)
  → MobileNetV2.preprocess_input()   # scales [0,255] → [-1, 1]
  → np.expand_dims(axis=0)           # add batch dim: (1, 128, 128, 3)
  → model.predict()                  # 101-class softmax probabilities
  → np.argmax()  →  class_indices.json  →  food name
  →  nutrition_db.json               # kcal / carbs / protein / fat
```

---

## Getting Started

### Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv)

### 1. Clone

```bash
git clone https://github.com/young0930093/meal-calorie-tracker.git
cd meal-calorie-tracker
```

### 2. Backend

```bash
cd backend

cp .env.example .env
# Fill in STRIPE_SECRET_KEY and any other secrets

uv sync
uv run uvicorn app.main:app --reload
# API docs → http://localhost:8000/docs
```

**Backend environment variables** (`.env`):

```env
STRIPE_SECRET_KEY=sk_test_...
MODEL_PATH=app/food_classifier.h5
CLASS_INDICES_PATH=app/class_indices.json
NUTRITION_DB_PATH=app/nutrition_db.json
```

> **Note:** The trained model file (`food_classifier.h5`, ~13 MB) and `class_indices.json` are included in the repo.  
> If the model is missing, the server falls back to a mock inference mode automatically.

### 3. Frontend

```bash
cd frontend

cp .env.example .env
# Set VITE_API_URL and Google / Stripe keys

npm install
npm run dev
# App → http://localhost:5173
```

**Frontend environment variables** (`.env`):

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 4. Train the Model (Optional)

1. Open `ml/train.ipynb` on Kaggle and add the `CryBread/food101` dataset.
2. Run all cells in order.
3. Download `/kaggle/working/food_classifier.h5` and `class_indices.json`.
4. Copy both files to `backend/app/` and restart the server.

---

## API Reference

All user data (profiles, meal history) is stored in the browser's localStorage — the backend is a pure AI inference server with no user database.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Server health check + ML model load status |
| `GET` | `/api/categories` | List of food category hints |
| `GET` | `/api/foods` | Full food list (filterable by category) |
| `GET` | `/api/nutrition/{food_class}` | Calorie & macro info for a specific food class |
| `POST` | `/api/predict` | Image → AI food classification |
| `POST` | `/api/predict-with-hint` | Re-classify within a selected category |
| `POST` | `/api/payment/create-intent` | Create a Stripe PaymentIntent |

### `POST /api/predict`

**Request:** `multipart/form-data` — `image` field (JPEG / PNG)

**Response:**
```json
{
  "predicted_class": "ramen",
  "predicted_name_ko": "라멘",
  "confidence": 0.83,
  "is_confident": true,
  "nutrition": {
    "calorie": 500,
    "carbs_g": 68,
    "protein_g": 20,
    "fat_g": 17
  },
  "top3": [
    { "class": "ramen",      "score": 0.83 },
    { "class": "pho",        "score": 0.09 },
    { "class": "udon",       "score": 0.05 }
  ]
}
```

### `POST /api/predict-with-hint`

Same as `/api/predict`, with an additional `category` form field.  
The model filters its output to the chosen category's classes and re-normalizes, boosting accuracy without needing a separate per-category model.

---

## Recognizable Foods (101 Classes)

| # | Class | Korean | Category | Calories |
|---|---|---|---|---|
| 1 | apple_pie | 애플 파이 | Dessert | 296 kcal |
| 2 | baby_back_ribs | 베이비 백 립 | Meat | 490 kcal |
| 3 | baklava | 바클라바 | Dessert | 330 kcal |
| 4 | beef_carpaccio | 비프 카르파초 | Meat | 150 kcal |
| 5 | beef_tartare | 비프 타르타르 | Meat | 220 kcal |
| 6 | beet_salad | 비트 샐러드 | Salad/Veggie | 120 kcal |
| 7 | beignets | 베녜 | Dessert | 320 kcal |
| 8 | bibimbap | 비빔밥 | Rice/Noodles | 560 kcal |
| 9 | bread_pudding | 브레드 푸딩 | Dessert | 350 kcal |
| 10 | breakfast_burrito | 브렉퍼스트 부리토 | Bread/Sandwich | 410 kcal |
| 11 | bruschetta | 브루스케타 | Bread/Sandwich | 190 kcal |
| 12 | caesar_salad | 시저 샐러드 | Salad/Veggie | 360 kcal |
| 13 | cannoli | 카놀리 | Dessert | 380 kcal |
| 14 | caprese_salad | 카프레제 샐러드 | Salad/Veggie | 210 kcal |
| 15 | carrot_cake | 당근 케이크 | Dessert | 415 kcal |
| 16 | ceviche | 세비체 | Seafood | 130 kcal |
| 17 | cheese_plate | 치즈 플레이트 | Snack | 400 kcal |
| 18 | cheesecake | 치즈케이크 | Dessert | 400 kcal |
| 19 | chicken_curry | 치킨 카레 | Meat | 350 kcal |
| 20 | chicken_quesadilla | 치킨 케사디아 | Bread/Sandwich | 430 kcal |
| 21 | chicken_wings | 치킨 윙 | Meat | 430 kcal |
| 22 | chocolate_cake | 초콜릿 케이크 | Dessert | 380 kcal |
| 23 | chocolate_mousse | 초콜릿 무스 | Dessert | 290 kcal |
| 24 | churros | 추로스 | Snack | 340 kcal |
| 25 | clam_chowder | 클램 차우더 | Soup | 230 kcal |
| 26 | club_sandwich | 클럽 샌드위치 | Bread/Sandwich | 450 kcal |
| 27 | crab_cakes | 크랩 케이크 | Seafood | 250 kcal |
| 28 | creme_brulee | 크렘 브륄레 | Dessert | 320 kcal |
| 29 | croque_madame | 크로크 마담 | Bread/Sandwich | 480 kcal |
| 30 | cup_cakes | 컵케이크 | Dessert | 310 kcal |
| 31 | deviled_eggs | 데빌드 에그 | Egg | 200 kcal |
| 32 | donuts | 도넛 | Dessert | 300 kcal |
| 33 | dumplings | 만두 | Snack | 280 kcal |
| 34 | edamame | 에다마메 | Salad/Veggie | 120 kcal |
| 35 | eggs_benedict | 에그 베네딕트 | Egg | 450 kcal |
| 36 | escargots | 에스카르고 | Snack | 180 kcal |
| 37 | falafel | 팔라펠 | Salad/Veggie | 330 kcal |
| 38 | filet_mignon | 필레 미뇽 | Meat | 320 kcal |
| 39 | fish_and_chips | 피시 앤 칩스 | Seafood | 550 kcal |
| 40 | foie_gras | 푸아그라 | Meat | 380 kcal |
| 41 | french_fries | 프렌치 프라이 | Snack | 370 kcal |
| 42 | french_onion_soup | 프렌치 어니언 수프 | Soup | 260 kcal |
| 43 | french_toast | 프렌치 토스트 | Egg | 380 kcal |
| 44 | fried_calamari | 튀긴 오징어 | Seafood | 280 kcal |
| 45 | fried_rice | 볶음밥 | Rice/Noodles | 490 kcal |
| 46 | frozen_yogurt | 프로즌 요거트 | Dessert | 230 kcal |
| 47 | garlic_bread | 갈릭 브레드 | Bread/Sandwich | 290 kcal |
| 48 | gnocchi | 뇨키 | Rice/Noodles | 350 kcal |
| 49 | greek_salad | 그릭 샐러드 | Salad/Veggie | 190 kcal |
| 50 | grilled_cheese_sandwich | 그릴드 치즈 샌드위치 | Bread/Sandwich | 400 kcal |
| 51 | grilled_salmon | 연어 구이 | Seafood | 280 kcal |
| 52 | guacamole | 과카몰리 | Salad/Veggie | 150 kcal |
| 53 | gyoza | 교자 | Snack | 280 kcal |
| 54 | hamburger | 햄버거 | Meat | 540 kcal |
| 55 | hot_and_sour_soup | 쏸라탕 | Soup | 130 kcal |
| 56 | hot_dog | 핫도그 | Bread/Sandwich | 290 kcal |
| 57 | huevos_rancheros | 우에보스 란체로스 | Egg | 380 kcal |
| 58 | hummus | 후무스 | Salad/Veggie | 170 kcal |
| 59 | ice_cream | 아이스크림 | Dessert | 270 kcal |
| 60 | lasagna | 라자냐 | Rice/Noodles | 380 kcal |
| 61 | lobster_bisque | 랍스터 비스크 | Soup | 280 kcal |
| 62 | lobster_roll_sandwich | 랍스터 롤 | Seafood | 360 kcal |
| 63 | macaroni_and_cheese | 맥 앤 치즈 | Rice/Noodles | 380 kcal |
| 64 | macarons | 마카롱 | Dessert | 230 kcal |
| 65 | miso_soup | 미소 수프 | Soup | 40 kcal |
| 66 | mussels | 홍합 | Seafood | 190 kcal |
| 67 | nachos | 나초 | Snack | 480 kcal |
| 68 | omelette | 오믈렛 | Egg | 210 kcal |
| 69 | onion_rings | 어니언 링 | Snack | 380 kcal |
| 70 | oysters | 굴 | Seafood | 80 kcal |
| 71 | pad_thai | 팟타이 | Rice/Noodles | 430 kcal |
| 72 | paella | 파에야 | Rice/Noodles | 450 kcal |
| 73 | pancakes | 팬케이크 | Dessert | 350 kcal |
| 74 | panna_cotta | 판나 코타 | Dessert | 280 kcal |
| 75 | peking_duck | 베이징 덕 | Meat | 380 kcal |
| 76 | pho | 쌀국수 (포) | Rice/Noodles | 350 kcal |
| 77 | pizza | 피자 | Bread/Sandwich | 480 kcal |
| 78 | pork_chop | 포크 찹 | Meat | 360 kcal |
| 79 | poutine | 푸틴 | Snack | 740 kcal |
| 80 | prime_rib | 프라임 립 | Meat | 540 kcal |
| 81 | pulled_pork_sandwich | 풀드 포크 샌드위치 | Bread/Sandwich | 490 kcal |
| 82 | ramen | 라멘 | Rice/Noodles | 500 kcal |
| 83 | red_velvet_cake | 레드 벨벳 케이크 | Dessert | 420 kcal |
| 84 | risotto | 리소토 | Rice/Noodles | 360 kcal |
| 85 | samosa | 사모사 | Snack | 300 kcal |
| 86 | sashimi | 사시미 | Seafood | 130 kcal |
| 87 | scallops | 가리비 | Seafood | 120 kcal |
| 88 | seaweed_salad | 해초 샐러드 | Salad/Veggie | 70 kcal |
| 89 | shrimp_and_grits | 새우 그리츠 | Seafood | 380 kcal |
| 90 | spaghetti_bolognese | 스파게티 볼로네제 | Rice/Noodles | 520 kcal |
| 91 | spaghetti_carbonara | 스파게티 카르보나라 | Rice/Noodles | 560 kcal |
| 92 | spring_rolls | 스프링 롤 | Snack | 220 kcal |
| 93 | steak | 스테이크 | Meat | 460 kcal |
| 94 | strawberry_shortcake | 딸기 쇼트케이크 | Dessert | 310 kcal |
| 95 | sushi | 초밥 | Seafood | 350 kcal |
| 96 | tacos | 타코 | Bread/Sandwich | 400 kcal |
| 97 | takoyaki | 타코야키 | Snack | 290 kcal |
| 98 | tiramisu | 티라미수 | Dessert | 360 kcal |
| 99 | tuna_tartare | 참치 타르타르 | Seafood | 180 kcal |
| 100 | waffles | 와플 | Dessert | 330 kcal |
| 101 | clam_chowder | 클램 차우더 | Soup | 230 kcal |

---

## Project Structure

```
meal-calorie-tracker/
├── frontend/                        # React 19 + Vite + Tailwind CSS v4
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx        # Google OAuth 2.0 login
│   │   │   ├── ProfilePage.jsx      # Profile creation / selection
│   │   │   ├── HomePage.jsx         # Daily calorie ring chart dashboard
│   │   │   ├── UploadPage.jsx       # 5-stage AI food recognition flow
│   │   │   ├── ResultPage.jsx       # Meal result confirmation & save
│   │   │   ├── HistoryPage.jsx      # Date-based meal history
│   │   │   └── SettingsPage.jsx     # Profile settings & payment
│   │   ├── contexts/
│   │   │   └── AppContext.jsx       # Global state (profiles, meal records)
│   │   ├── components/
│   │   │   └── PaymentModal.jsx     # Stripe payment modal
│   │   └── utils/
│   │       └── calculations.js     # BMR, TDEE, exercise burn calculations
│   ├── vercel.json                  # SPA routing rewrite rules
│   └── package.json
│
├── backend/                         # FastAPI + Python 3.12
│   ├── app/
│   │   ├── main.py                  # FastAPI app, routes, ML inference
│   │   ├── nutrition_db.json        # 101-class calorie & macro database
│   │   ├── food_classifier.h5       # Trained MobileNetV2 model (~13 MB)
│   │   └── class_indices.json       # Model class index ↔ food name mapping
│   ├── railway.toml                 # Railway deployment config
│   └── requirements.txt
│
└── ml/
    └── train.ipynb                  # Kaggle training notebook (Food-101 + MobileNetV2)
```

---

## Roadmap

### Short-term
- [ ] Add Korean foods (김치찌개, 된장찌개, 삼겹살, 불고기…) via additional dataset + model retraining
- [ ] Portion size input ("half a bowl", "1.5 servings")
- [ ] Dynamic category loading from `/api/categories`
- [ ] PWA support (offline mode, home screen install, push notifications)

### Mid-term (requires server-side DB)
- [ ] PostgreSQL + proper auth for cross-device data sync
- [ ] Weekly / monthly nutrition trend reports
- [ ] Goal modes: diet / bulk / maintain — with adjusted macro targets
- [ ] Favourite foods quick-add

### Long-term (AI improvements)
- [ ] Retrain at 224 × 224 with Phase 2 fine-tuning → +5–10% accuracy
- [ ] Korean-food-specific model using AI-Hub dataset
- [ ] Portion weight estimation from image (regression model)
- [ ] LLM-powered meal recommendations based on today's intake
- [ ] React Native iOS / Android app

---

## Known Limitations

- **Model accuracy**: Training at 128 × 128 (down from standard 224 × 224) reduces accuracy. Phase 2 fine-tuning (unfreezing the backbone at a lower LR) was omitted due to GPU memory constraints.
- **Korean food coverage**: Food-101 contains almost no Korean dishes. The model struggles with Korean staples beyond bibimbap.
- **Calorie estimates**: Values represent typical average servings; actual calories vary by portion size and preparation method.
- **Data persistence**: All user data lives in localStorage — clearing browser storage or switching devices loses your history. A server-side DB is on the roadmap.
- **Inference speed**: The Railway free tier runs on CPU only, so prediction may take a few seconds on cold starts.

---

## License

MIT — see [LICENSE](./LICENSE) for details.

Nutrition data sourced from general nutritional references. Exercise calorie estimates are approximations based on body-weight MET values.
