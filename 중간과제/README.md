# 🍱 Meal Calorie Tracker

**Snap a photo of your meal — let AI do the math.**

Meal Calorie Tracker is a web application that automatically recognizes Korean and Western dishes from photos using a MobileNetV2-based CNN, then calculates calories and macronutrients (carbs / protein / fat) on the spot. It also converts your total intake into equivalent exercise time and tracks your progress against personalized daily nutrition goals.

---

## ✨ Key Features

### 🤖 AI-Powered Food Recognition
- Upload a photo of a single dish and get instant classification from a fine-tuned **MobileNetV2** model
- Displays top-3 predictions with confidence scores
- **Hint mode**: if confidence is low, select a food category (e.g., 🍚 Rice/Noodles, 🍲 Stew, 🥬 Veggies, 🍖 Meat…) and the model re-classifies within that subset for higher accuracy

| Confidence | Behavior |
|---|---|
| ≥ 70% | Result shown immediately |
| 40–70% | Result shown + "Is this correct?" prompt |
| < 40% | "Unrecognized" → guided into Hint Mode |

### 🧮 Nutrition Analysis
- Per-dish breakdown: **kcal / carbs (g) / protein (g) / fat (g)**
- Meal-level totals for each sitting
- Daily cumulative progress bars against your personalized targets

### 👤 Personalized Daily Goals
- Create a profile (name / gender / age / height / weight / activity level)
- BMR and TDEE computed via the **Harris-Benedict formula**
- Auto-calculates macro targets:
  - Carbs: `TDEE × 55% ÷ 4`
  - Protein: `body weight (kg) × 1.0`
  - Fat: `TDEE × 25% ÷ 9`
- Multiple profiles supported on the same device

### 🏃 Exercise Equivalents
Converts total meal calories into approximate exercise duration using body-weight-adjusted MET estimates:

| Activity | Formula |
|---|---|
| Running | `weight_kg × 1.036` kcal/km |
| Walking | `weight_kg × 0.067` kcal/min |
| Cycling | `weight_kg × 0.133` kcal/min |

### 📊 History & Trends
- Daily / weekly calorie log with a bar chart
- Linear-regression trend line over the past 7 days (rising / falling / stable)
- Macro ratio donut chart per day

### 💾 Client-Side Storage
- All user data (profiles + meal history) lives in **browser localStorage** — no account required, no server-side database
- JSON export / import for cross-device backup and restore

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI (Python 3.11+), `uv` for package management |
| AI / ML | TensorFlow / Keras, MobileNetV2 (Transfer Learning) |
| Storage | Browser localStorage (user data) · JSON file (nutrition DB) |
| Deployment | Vercel (frontend) · Railway (backend) |

---

## 🧠 Model Architecture

The classifier is built on **MobileNetV2** pretrained on ImageNet, with a custom head:

```
MobileNetV2 (frozen backbone)
    └── GlobalAveragePooling2D
    └── Dense(128, relu)
    └── Dropout(0.5)
    └── Dense(N_CLASSES, softmax)
```

**Training config:**
- Optimizer: Adam (lr = 0.001)
- Loss: Categorical Crossentropy
- Batch size: 32 · Epochs: 20 (Early Stopping)
- Data augmentation: random rotation ±20°, brightness ±0.2, horizontal flip

**Hint-mode re-classification** uses the main model's output logits, filters to the selected category's classes, and re-normalizes with softmax — no separate model needed.

**Training data:** Food-101 (subset of 20–30 classes) + supplementary Korean food images from AI Hub.  
Image preprocessing: resize to **224 × 224**, normalize to `[0, 1]`, Train / Val / Test = 70 / 15 / 15 %.

---

## 📁 Repository Structure

```
meal-calorie-tracker/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfileSetup.jsx       # Initial profile creation form
│   │   │   ├── ProfileSelector.jsx    # Multi-profile switcher
│   │   │   ├── ImageUploader.jsx      # Photo upload & preview
│   │   │   ├── PredictionResult.jsx   # Classification result + confirm/edit
│   │   │   ├── HintSelector.jsx       # Category hint UI
│   │   │   ├── MealSummary.jsx        # Totals + exercise equivalents
│   │   │   ├── NutritionProgress.jsx  # Daily macro progress bars
│   │   │   ├── MacroDonutChart.jsx    # Macro ratio donut chart
│   │   │   ├── HistoryChart.jsx       # Recharts trend graph
│   │   │   └── DataBackup.jsx         # JSON export / import
│   │   └── context/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app & routes
│   │   ├── model.py                   # Model loading & inference
│   │   └── nutrition_db.json          # Per-food calorie & macro data
│   ├── pyproject.toml
│   └── Dockerfile
├── ml/
│   ├── train.ipynb                    # Model training notebook
│   ├── data_prep.py
│   └── models/                        # Saved .keras / .h5 files
└── docs/
    └── architecture.png
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ and `npm`
- **Python** 3.11+
- [`uv`](https://github.com/astral-sh/uv) (Python package manager)

### 1. Clone

```bash
git clone https://github.com/your-username/meal-calorie-tracker.git
cd meal-calorie-tracker
```

### 2. Backend

```bash
cd backend
uv sync
# Place your trained model file at the path set in MODEL_PATH (see below)
uv run uvicorn app.main:app --reload --port 8000
```

**Environment variables** (create a `.env` in `backend/`):

```env
MODEL_PATH=./models/food_classifier.keras
NUTRITION_DB_PATH=./app/nutrition_db.json
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

**Environment variables** (create a `.env.local` in `frontend/`):

```env
VITE_API_URL=http://localhost:8000
```

The app will be available at `http://localhost:5173`.

---

## 📡 API Reference

All user data is stored client-side; the backend only handles AI inference and nutrition lookups.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Server health check |
| `GET` | `/api/categories` | List of food category hints |
| `GET` | `/api/nutrition/{food_class}` | Calorie + macro info for a food class |
| `POST` | `/api/predict` | Classify an uploaded food image |
| `POST` | `/api/predict-with-hint` | Re-classify within a selected category |

### `POST /api/predict`

Request: `multipart/form-data` with an `image` field.

```json
{
  "predicted_class": "kimchi_stew",
  "predicted_name_ko": "김치찌개",
  "confidence": 0.87,
  "is_confident": true,
  "nutrition": {
    "calorie": 150,
    "carbs_g": 10,
    "protein_g": 12,
    "fat_g": 8
  },
  "top3": [
    { "class": "kimchi_stew",   "name_ko": "김치찌개",  "score": 0.87 },
    { "class": "soybean_stew",  "name_ko": "된장찌개",  "score": 0.09 },
    { "class": "sundubu",       "name_ko": "순두부찌개", "score": 0.03 }
  ]
}
```

### `POST /api/predict-with-hint`

Same as `/api/predict` but also accepts a `category` form field. Returns the same response schema, re-classified within the given category.

---

## 🗄 Client-Side Data Schema

### localStorage Keys

| Key | Content |
|---|---|
| `meal_tracker:profiles` | Array of all user profiles |
| `meal_tracker:active_profile_id` | Currently selected profile ID |
| `meal_tracker:meals:{profile_id}` | Meal history for a profile |

### Profile Object

```json
{
  "id": "profile_abc123",
  "name": "Youngie",
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

### Meal Record Object

```json
{
  "id": "meal_xyz789",
  "date": "2026-04-22",
  "meal_type": "lunch",
  "items": [
    { "food_class": "rice",         "name_ko": "쌀밥",   "calorie": 300, "carbs_g": 66, "protein_g": 6,  "fat_g": 1 },
    { "food_class": "kimchi_stew",  "name_ko": "김치찌개", "calorie": 150, "carbs_g": 10, "protein_g": 12, "fat_g": 8 }
  ],
  "totals": { "calorie": 450, "carbs_g": 76, "protein_g": 18, "fat_g": 9 },
  "created_at": "2026-04-22T12:30:00Z"
}
```

---

## 🌐 System Architecture

```
┌──────────────────────┐    HTTP / REST   ┌──────────────────────┐
│   React Frontend     │ ───────────────► │   FastAPI Backend    │
│   (Vercel)           │                  │   (Railway)          │
│                      │                  │                      │
│  ┌────────────────┐  │                  │  ┌────────────────┐  │
│  │  localStorage  │  │                  │  │  MobileNetV2   │  │
│  │  - Profiles    │  │                  │  │  Classifier    │  │
│  │  - Meal logs   │  │                  │  └───────┬────────┘  │
│  │  - Daily goals │  │                  │          │           │
│  └────────────────┘  │                  │  ┌───────▼────────┐  │
└──────────────────────┘                  │  │ Nutrition DB   │  │
                                          │  │   (JSON)       │  │
                                          │  └────────────────┘  │
                                          └──────────────────────┘

The backend is a pure AI inference server.
All user data stays in the browser — no server DB needed.
```

---

## 🔮 Planned Features

- Multi-food detection in a single photo (Object Detection)
- Automatic portion-size estimation from images
- LLM-powered meal recommendations
- Cross-device sync via cloud storage
- iOS / Android native app

---

## 📄 License

MIT — see [LICENSE](./LICENSE) for details.

Nutrition data sourced from the Korean Ministry of Food and Drug Safety (MFDS) and [USDA FoodData Central](https://fdc.nal.usda.gov/).
