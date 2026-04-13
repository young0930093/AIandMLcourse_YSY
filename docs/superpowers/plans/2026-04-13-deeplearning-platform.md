# Deep Learning Lecture Subscription Platform — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Week5 딥러닝 강의 구독 플랫폼 — Google OAuth2 로그인, polar.sh 결제, 구독자 전용 콘텐츠

**Architecture:** FastAPI 백엔드(Railway/Render) + React SPA(Vercel) 완전 분리. SQLite로 유저/구독 상태 저장. Google OAuth2로 인증 후 JWT 발급, polar.sh sandbox로 월 구독 결제.

**Tech Stack:** React 18 + Vite + Tailwind CSS / FastAPI + aiosqlite + python-jose / Google OAuth2 / polar.sh

---

## Task 1: 프로젝트 스캐폴딩 & 설정 파일

**Files:**
- Create: `backend/requirements.txt`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `.env.example`
- Create: `vercel.json`

- [ ] **Step 1: backend/requirements.txt 생성**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
httpx==0.27.0
python-jose[cryptography]==3.3.0
aiosqlite==0.20.0
pydantic[email]==2.7.1
python-multipart==0.0.9
```

- [ ] **Step 2: frontend/package.json 생성**

```json
{
  "name": "deeplearning-platform",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "react-syntax-highlighter": "^15.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.2.11",
    "tailwindcss": "^3.4.3",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38"
  }
}
```

- [ ] **Step 3: frontend/vite.config.js 생성**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/webhooks': 'http://localhost:8000',
    }
  }
})
```

- [ ] **Step 4: frontend/tailwind.config.js 생성**

```js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        pink: {
          light: '#FFB6C1',
          DEFAULT: '#FF69B4',
          dark: '#FF1493',
        }
      }
    }
  },
  plugins: []
}
```

- [ ] **Step 5: frontend/postcss.config.js 생성**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
```

- [ ] **Step 6: frontend/index.html 생성**

```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DeepLearn — 딥러닝 강의 플랫폼</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 7: .env.example 생성**

```
# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT
JWT_SECRET_KEY=your_very_long_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# polar.sh
POLAR_ACCESS_TOKEN=your_polar_access_token
POLAR_PRODUCT_ID=your_polar_product_id
POLAR_WEBHOOK_SECRET=your_polar_webhook_secret

# App URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

- [ ] **Step 8: vercel.json 생성**

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
```

- [ ] **Step 9: 의존성 설치**

```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

---

## Task 2: Backend — Database

**Files:**
- Create: `backend/database.py`

- [ ] **Step 1: backend/database.py 생성**

```python
import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "deeplearn.db")

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    picture TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_SUBSCRIPTIONS = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    polar_subscription_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
)
"""

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_SUBSCRIPTIONS)
        await db.commit()
```

---

## Task 3: Backend — Models

**Files:**
- Create: `backend/models.py`

- [ ] **Step 1: backend/models.py 생성**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]
    picture: Optional[str]
    is_subscribed: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CoursePreview(BaseModel):
    id: int
    title: str
    description: str
    is_free: bool
    duration: str
    level: str

class CourseDetail(BaseModel):
    id: int
    title: str
    description: str
    is_free: bool
    duration: str
    level: str
    content: Optional[dict] = None  # None if locked

class CheckoutResponse(BaseModel):
    checkout_url: str

class SubscriptionStatus(BaseModel):
    is_subscribed: bool
    expires_at: Optional[datetime] = None
```

---

## Task 4: Backend — Auth (Google OAuth2 + JWT)

**Files:**
- Create: `backend/auth.py`

- [ ] **Step 1: backend/auth.py 생성**

```python
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
import aiosqlite
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        return None


@router.get("/google")
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(code: str, db: aiosqlite.Connection = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo = userinfo_resp.json()

    google_id = userinfo["sub"]
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")
    picture = userinfo.get("picture", "")

    cursor = await db.execute(
        "SELECT id FROM users WHERE google_id = ?", (google_id,)
    )
    row = await cursor.fetchone()

    if row:
        user_id = row["id"]
        await db.execute(
            "UPDATE users SET name=?, picture=? WHERE id=?",
            (name, picture, user_id)
        )
    else:
        cursor = await db.execute(
            "INSERT INTO users (google_id, email, name, picture) VALUES (?,?,?,?)",
            (google_id, email, name, picture)
        )
        user_id = cursor.lastrowid

    await db.commit()
    jwt_token = create_access_token(user_id)
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={jwt_token}")


@router.get("/me")
async def get_me(token: str, db: aiosqlite.Connection = Depends(get_db)):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sub_cursor = await db.execute(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    subscription = await sub_cursor.fetchone()

    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
        "is_subscribed": subscription is not None,
    }
```

---

## Task 5: Backend — Courses (콘텐츠 포함)

**Files:**
- Create: `backend/courses.py`

- [ ] **Step 1: backend/courses.py 생성**

```python
import os
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from auth import decode_token
import aiosqlite
from database import DB_PATH

router = APIRouter(prefix="/api/courses", tags=["courses"])

COURSES = [
    {
        "id": 1,
        "title": "Regularization — L1/L2, Dropout, Batch Normalization",
        "description": "과적합을 막는 세 가지 핵심 기법을 이론과 코드로 배웁니다.",
        "is_free": True,
        "duration": "45분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "왜 Regularization이 필요한가?",
                    "body": """모델이 훈련 데이터에 지나치게 맞춰지면 새로운 데이터에서 성능이 떨어집니다.
이를 **과적합(Overfitting)** 이라 하며, Regularization은 모델의 복잡도를 제한해 일반화 성능을 높입니다."""
                },
                {
                    "title": "L1 Regularization (Lasso)",
                    "body": """가중치의 절댓값 합을 손실에 더합니다: `Loss = Loss_original + λ Σ|w|`

- 일부 가중치를 **정확히 0**으로 만들어 희소(Sparse) 모델을 생성
- 불필요한 특성을 자동으로 제거하는 효과""",
                    "code": """import tensorflow as tf
from tensorflow.keras import regularizers

model = tf.keras.Sequential([
    tf.keras.layers.Dense(
        128,
        activation='relu',
        kernel_regularizer=regularizers.l1(0.01)  # λ=0.01
    ),
    tf.keras.layers.Dense(10, activation='softmax')
])"""
                },
                {
                    "title": "L2 Regularization (Ridge / Weight Decay)",
                    "body": """가중치의 제곱합을 손실에 더합니다: `Loss = Loss_original + λ Σw²`

- 가중치를 0에 가깝게 만들지만 **완전히 0으로 만들지는 않음**
- 딥러닝에서 가장 널리 사용되는 정규화 방법""",
                    "code": """model = tf.keras.Sequential([
    tf.keras.layers.Dense(
        128,
        activation='relu',
        kernel_regularizer=regularizers.l2(0.01)  # λ=0.01
    ),
    tf.keras.layers.Dense(10, activation='softmax')
])

# L1 + L2 동시 사용 (Elastic Net)
regularizers.l1_l2(l1=0.01, l2=0.01)"""
                },
                {
                    "title": "Dropout",
                    "body": """훈련 중 무작위로 뉴런을 **비활성화**합니다 (p 확률로 출력을 0으로).

- 추론(Inference) 시에는 모든 뉴런 사용 (출력에 p 곱함)
- 앙상블 효과: 매 배치마다 다른 서브네트워크를 학습
- 일반적으로 p=0.2~0.5 사용""",
                    "code": """model = tf.keras.Sequential([
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.5),   # 50% 뉴런 비활성화
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.3),   # 30% 뉴런 비활성화
    tf.keras.layers.Dense(10, activation='softmax')
])"""
                },
                {
                    "title": "Batch Normalization",
                    "body": """각 배치의 활성화값을 **정규화**합니다: `x̂ = (x - μ_B) / √(σ²_B + ε)`

- 학습 속도 향상: Learning Rate를 크게 설정 가능
- 가중치 초기화에 덜 민감
- 약한 Regularization 효과 (Dropout과 함께 사용 가능)
- Conv Layer 뒤에 자주 배치: `Conv → BN → ReLU`""",
                    "code": """model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), use_bias=False),
    tf.keras.layers.BatchNormalization(),   # BN은 bias 불필요
    tf.keras.layers.Activation('relu'),

    tf.keras.layers.Conv2D(64, (3,3), use_bias=False),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Activation('relu'),

    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(10, activation='softmax')
])"""
                },
                {
                    "title": "핵심 요약",
                    "body": """| 기법 | 동작 원리 | 주요 효과 |
|------|-----------|-----------|
| L1 | |w| 패널티 | 희소 모델, 특성 선택 |
| L2 | w² 패널티 | 작은 가중치 유지 |
| Dropout | 랜덤 뉴런 비활성화 | 앙상블 효과 |
| Batch Norm | 활성화값 정규화 | 학습 안정화, 빠른 수렴 |"""
                }
            ]
        }
    },
    {
        "id": 2,
        "title": "Overfitting vs Underfitting — 모델 복잡도와 성능",
        "description": "편향-분산 트레이드오프를 이해하고 최적의 모델 복잡도를 찾는 방법을 배웁니다.",
        "is_free": False,
        "duration": "40분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "편향-분산 트레이드오프 (Bias-Variance Tradeoff)",
                    "body": """모델 오차는 세 가지로 분해됩니다:
`Total Error = Bias² + Variance + Irreducible Noise`

- **High Bias (Underfitting)**: 모델이 너무 단순 → 훈련/테스트 모두 성능 낮음
- **High Variance (Overfitting)**: 모델이 너무 복잡 → 훈련 성능 높지만 테스트 성능 낮음
- **목표**: Bias와 Variance를 동시에 낮추는 균형점 찾기"""
                },
                {
                    "title": "Overfitting 진단 — 학습 곡선",
                    "body": """훈련 손실(loss)과 검증 손실을 함께 플롯해 과적합을 진단합니다.""",
                    "code": """import matplotlib.pyplot as plt

history = model.fit(X_train, y_train,
                    validation_split=0.2,
                    epochs=100)

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss Curve')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Train Acc')
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.title('Accuracy Curve')
plt.legend()
plt.show()

# Overfitting 신호:
# val_loss 증가하는데 train_loss는 계속 감소"""
                },
                {
                    "title": "Early Stopping으로 Overfitting 방지",
                    "body": """검증 손실이 개선되지 않으면 학습을 자동으로 중단합니다.""",
                    "code": """early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,          # 10 epoch 동안 개선 없으면 중단
    restore_best_weights=True  # 최적 가중치 복원
)

model.fit(X_train, y_train,
          validation_split=0.2,
          epochs=200,
          callbacks=[early_stop])

print(f"실제 학습 epoch: {early_stop.stopped_epoch}")"""
                },
                {
                    "title": "Underfitting 해결 방법",
                    "body": """Underfitting은 모델 용량(capacity)이 부족할 때 발생합니다.""",
                    "code": """# 1. 모델 복잡도 증가
model_larger = tf.keras.Sequential([
    tf.keras.layers.Dense(512, activation='relu'),  # 128 → 512
    tf.keras.layers.Dense(256, activation='relu'),  # 레이어 추가
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# 2. 더 많은 epoch 학습
model.fit(X_train, y_train, epochs=200)  # epoch 늘리기

# 3. Learning Rate 조정
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)"""
                },
                {
                    "title": "모델 복잡도 비교 실험",
                    "body": """동일 데이터에 복잡도가 다른 모델 세 개를 비교합니다.""",
                    "code": """def build_model(units, layers):
    model = tf.keras.Sequential()
    for _ in range(layers):
        model.add(tf.keras.layers.Dense(units, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# 세 모델 비교
underfit = build_model(units=4, layers=1)    # 너무 단순
good_fit = build_model(units=64, layers=2)   # 적절
overfit  = build_model(units=512, layers=5)  # 너무 복잡"""
                },
                {
                    "title": "핵심 요약",
                    "body": """| 상태 | Train Loss | Val Loss | 해결책 |
|------|-----------|---------|--------|
| Underfitting | 높음 | 높음 | 모델 복잡도 ↑, epoch ↑ |
| Good Fit | 낮음 | 낮음 | 유지 |
| Overfitting | 낮음 | 높음 | Regularization, Dropout, Early Stopping |"""
                }
            ]
        }
    },
    {
        "id": 3,
        "title": "Data Augmentation — 이미지 데이터 증강으로 모델 강화하기",
        "description": "적은 데이터로도 강력한 모델을 만드는 데이터 증강 기법을 실습합니다.",
        "is_free": False,
        "duration": "50분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "Data Augmentation이란?",
                    "body": """기존 훈련 데이터를 변형해 **인위적으로 데이터셋을 확장**하는 기법입니다.

- 데이터 수집 비용 없이 훈련 샘플 증가
- 모델이 다양한 변형에 강인(Robust)해짐
- 특히 의료 이미지, 위성 이미지처럼 데이터가 부족한 분야에서 필수"""
                },
                {
                    "title": "Keras ImageDataGenerator",
                    "body": """Keras의 내장 증강 도구로 실시간 변환을 적용합니다.""",
                    "code": """from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt

datagen = ImageDataGenerator(
    rotation_range=30,        # ±30도 회전
    width_shift_range=0.2,    # 수평 이동 20%
    height_shift_range=0.2,   # 수직 이동 20%
    shear_range=0.2,          # 전단 변환
    zoom_range=0.2,           # 20% 줌인/아웃
    horizontal_flip=True,     # 좌우 반전
    fill_mode='nearest'       # 빈 공간 채우기
)

# 모델 학습에 적용
model.fit(
    datagen.flow(X_train, y_train, batch_size=32),
    epochs=50,
    validation_data=(X_val, y_val)
)"""
                },
                {
                    "title": "TensorFlow tf.data 파이프라인 증강",
                    "body": """최신 방법: tf.keras.layers로 증강 레이어를 모델에 포함시킵니다.""",
                    "code": """import tensorflow as tf

# 증강 레이어를 모델 입력부에 포함
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1),
])

# 모델 구성
inputs = tf.keras.Input(shape=(224, 224, 3))
x = data_augmentation(inputs)       # 증강 (훈련 시에만 적용)
x = tf.keras.applications.MobileNetV2(include_top=False)(x)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
outputs = tf.keras.layers.Dense(10, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)"""
                },
                {
                    "title": "Albumentations — 고급 증강 라이브러리",
                    "body": """Albumentations는 80+ 변환을 지원하는 고성능 증강 라이브러리입니다.""",
                    "code": """# pip install albumentations
import albumentations as A
import cv2
import numpy as np

transform = A.Compose([
    A.RandomCrop(width=224, height=224),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.GaussNoise(p=0.1),
    A.Blur(blur_limit=3, p=0.1),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=15, p=0.5),
])

# 이미지에 적용
image = cv2.imread("cat.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
augmented = transform(image=image)
augmented_image = augmented['image']"""
                },
                {
                    "title": "핵심 요약",
                    "body": """| 기법 | 효과 | 주의사항 |
|------|------|---------|
| Flip | 방향 불변성 | 텍스트/숫자엔 부적합 |
| Rotation | 각도 불변성 | 큰 각도는 정보 손실 |
| Zoom | 스케일 불변성 | 과도하면 객체 잘림 |
| Color Jitter | 조명 강인성 | 색상이 중요한 경우 주의 |
| Cutout/Mixup | 일반화 성능 ↑ | 레이블 smoothing 필요 |"""
                }
            ]
        }
    },
    {
        "id": 4,
        "title": "Transfer Learning — MobileNetV2로 나만의 분류기 만들기",
        "description": "ImageNet으로 사전학습된 MobileNetV2를 활용해 커스텀 이미지 분류기를 만듭니다.",
        "is_free": False,
        "duration": "60분",
        "level": "고급",
        "content": {
            "sections": [
                {
                    "title": "Transfer Learning이란?",
                    "body": """대규모 데이터셋에서 학습된 모델의 **지식을 새로운 태스크에 전이**하는 기법입니다.

- ImageNet(1.2M 이미지, 1000 클래스)으로 학습된 모델의 특성 추출기를 재사용
- 적은 데이터와 짧은 학습 시간으로 높은 성능 달성
- 두 단계: Feature Extraction → Fine-Tuning"""
                },
                {
                    "title": "MobileNetV2 아키텍처",
                    "body": """MobileNetV2는 모바일/임베디드용으로 설계된 경량 CNN입니다.

- **Inverted Residual Block**: 확장(Expand) → Depthwise Conv → 축소(Project)
- **Linear Bottleneck**: 마지막 레이어에 비선형 활성화 없음
- ImageNet Top-5 정확도: 91.3% (파라미터 수: 3.4M)"""
                },
                {
                    "title": "1단계: Feature Extraction (기반 레이어 동결)",
                    "body": """기반 모델의 가중치를 동결하고, 최상단 분류기만 학습합니다.""",
                    "code": """import tensorflow as tf

# 1. 기반 모델 로드 (분류 헤드 제외)
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,          # ImageNet 분류 헤드 제외
    weights='imagenet'          # 사전학습 가중치
)

# 2. 기반 모델 동결
base_model.trainable = False

# 3. 커스텀 분류 헤드 추가
inputs = tf.keras.Input(shape=(224, 224, 3))
x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
x = base_model(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(5, activation='softmax')(x)  # 5개 클래스

model = tf.keras.Model(inputs, outputs)

# 4. 분류 헤드만 학습
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(train_dataset, epochs=10, validation_data=val_dataset)"""
                },
                {
                    "title": "2단계: Fine-Tuning (상위 레이어 해동)",
                    "body": """기반 모델 상위 레이어를 해동해 낮은 학습률로 미세 조정합니다.""",
                    "code": """# 기반 모델의 상위 30개 레이어 해동
base_model.trainable = True
fine_tune_at = len(base_model.layers) - 30

for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

print(f"전체 레이어: {len(base_model.layers)}")
print(f"학습 가능 레이어: {sum(1 for l in base_model.layers if l.trainable)}")

# 낮은 Learning Rate로 재컴파일 (중요!)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),  # 10배 낮춤
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_dataset,
    epochs=20,
    validation_data=val_dataset,
    callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)]
)"""
                },
                {
                    "title": "커스텀 데이터셋으로 꽃 분류기 만들기",
                    "body": """TensorFlow Flowers 데이터셋(5 클래스)으로 전체 파이프라인을 실행합니다.""",
                    "code": """import tensorflow_datasets as tfds

# 데이터 로드
(train_ds, val_ds), info = tfds.load(
    'tf_flowers',
    split=['train[:80%]', 'train[80%:]'],
    as_supervised=True,
    with_info=True
)

IMG_SIZE = 224
BATCH_SIZE = 32

def preprocess(image, label):
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])
    return image, tf.one_hot(label, 5)

train_ds = train_ds.map(preprocess).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.map(preprocess).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# 위 모델로 학습 후 평가
loss, acc = model.evaluate(val_ds)
print(f"Validation Accuracy: {acc:.2%}")"""
                },
                {
                    "title": "핵심 요약",
                    "body": """| 단계 | 동결 레이어 | Learning Rate | 목적 |
|------|------------|---------------|------|
| Feature Extraction | 전체 기반 모델 | 0.001 | 분류기 헤드 학습 |
| Fine-Tuning | 하위 레이어만 | 0.00001 | 상위 특성 미세 조정 |

**언제 각 방법을 사용할까?**
- 데이터가 적고 기반 모델과 유사 → Feature Extraction만
- 데이터가 중간 → Feature Extraction 후 Fine-Tuning
- 데이터가 많고 다른 도메인 → 처음부터 학습"""
                }
            ]
        }
    },
    {
        "id": 5,
        "title": "CNN 실습 — MNIST 손글씨 인식 모델 구현",
        "description": "CNN의 핵심 구성 요소를 이해하고 MNIST 데이터셋으로 99% 정확도 모델을 만듭니다.",
        "is_free": False,
        "duration": "55분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "CNN 핵심 구성 요소",
                    "body": """CNN(Convolutional Neural Network)은 이미지 처리를 위해 설계된 신경망입니다.

**Conv2D**: 작은 필터(커널)로 이미지를 슬라이딩하며 특성 추출
- 파라미터 공유로 일반 Dense 대비 파라미터 수 대폭 감소
- 위치 불변성(Translation Invariance) 확보

**MaxPooling2D**: 공간 해상도를 줄이며 주요 특성 보존
- 계산량 감소, 약한 위치 불변성 추가

**Flatten → Dense**: 추출된 특성을 벡터화 후 분류"""
                },
                {
                    "title": "MNIST 데이터 준비",
                    "body": """MNIST: 28×28 흑백 손글씨 숫자 이미지 70,000장 (0~9)""",
                    "code": """import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# 데이터 로드
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()

print(f"훈련 데이터: {X_train.shape}")   # (60000, 28, 28)
print(f"테스트 데이터: {X_test.shape}")  # (10000, 28, 28)

# 전처리
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
X_test  = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test  = tf.keras.utils.to_categorical(y_test, 10)

# 샘플 시각화
fig, axes = plt.subplots(2, 5, figsize=(12, 5))
for i, ax in enumerate(axes.flat):
    ax.imshow(X_train[i].reshape(28, 28), cmap='gray')
    ax.set_title(f"Label: {y_train[i].argmax()}")
    ax.axis('off')
plt.show()"""
                },
                {
                    "title": "CNN 모델 구현",
                    "body": """두 개의 Conv 블록과 완전연결층으로 구성된 MNIST 분류기입니다.""",
                    "code": """model = tf.keras.Sequential([
    # Block 1
    tf.keras.layers.Conv2D(32, (3,3), padding='same', input_shape=(28,28,1)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Conv2D(32, (3,3), padding='same'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Dropout(0.25),

    # Block 2
    tf.keras.layers.Conv2D(64, (3,3), padding='same'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Conv2D(64, (3,3), padding='same'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Dropout(0.25),

    # Classifier
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.summary()
# Total params: ~1.2M"""
                },
                {
                    "title": "학습 및 평가",
                    "body": """Learning Rate Scheduler와 Early Stopping을 사용해 최적 성능을 달성합니다.""",
                    "code": """model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=5, restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6
    )
]

history = model.fit(
    X_train, y_train,
    batch_size=128,
    epochs=50,
    validation_split=0.1,
    callbacks=callbacks
)

test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"테스트 정확도: {test_acc:.4f}")  # 목표: 99%+"""
                },
                {
                    "title": "오분류 분석",
                    "body": """모델이 틀린 예측을 시각화해 약점을 파악합니다.""",
                    "code": """y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true_classes = np.argmax(y_test, axis=1)

# 오분류 인덱스
wrong_idx = np.where(y_pred_classes != y_true_classes)[0]
print(f"오분류 수: {len(wrong_idx)} / {len(y_test)}")

# Confusion Matrix
from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(y_true_classes, y_pred_classes)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='RdPu')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()"""
                },
                {
                    "title": "핵심 요약",
                    "body": """**MNIST CNN 아키텍처 요약:**
```
Input (28×28×1)
  → Conv(32) → BN → ReLU → Conv(32) → BN → ReLU → MaxPool → Dropout
  → Conv(64) → BN → ReLU → Conv(64) → BN → ReLU → MaxPool → Dropout
  → Flatten → Dense(512) → BN → Dropout → Dense(10, softmax)
```

**성능 목표:**
- 기본 Dense: ~98%
- CNN (위 구조): ~99.3%
- 데이터 증강 추가: ~99.5%+"""
                }
            ]
        }
    }
]


async def get_user_subscription(user_id: int) -> bool:
    if not user_id:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM subscriptions WHERE user_id=? AND status='active' LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row is not None


def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    return decode_token(token)


@router.get("")
async def list_courses():
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "is_free": c["is_free"],
            "duration": c["duration"],
            "level": c["level"],
        }
        for c in COURSES
    ]


@router.get("/{course_id}")
async def get_course(
    course_id: int,
    authorization: Optional[str] = Header(None)
):
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        user_id = decode_token(token)

    is_subscribed = await get_user_subscription(user_id) if user_id else False
    can_view = course["is_free"] or is_subscribed

    return {
        "id": course["id"],
        "title": course["title"],
        "description": course["description"],
        "is_free": course["is_free"],
        "duration": course["duration"],
        "level": course["level"],
        "content": course["content"] if can_view else None,
        "locked": not can_view,
    }
```

---

## Task 6: Backend — Payment (polar.sh)

**Files:**
- Create: `backend/payment.py`

- [ ] **Step 1: backend/payment.py 생성**

```python
import os
import hmac
import hashlib
import json
import httpx
import aiosqlite
from fastapi import APIRouter, Header, HTTPException, Request, Depends
from datetime import datetime, timedelta
from auth import decode_token
from database import get_db

router = APIRouter(tags=["payment"])

POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN")
POLAR_PRODUCT_ID = os.getenv("POLAR_PRODUCT_ID")
POLAR_WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

POLAR_API_BASE = "https://sandbox-api.polar.sh"


@router.post("/api/subscribe/create")
async def create_checkout(
    authorization: str = Header(...),
    db: aiosqlite.Connection = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = await db.execute("SELECT email FROM users WHERE id=?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{POLAR_API_BASE}/v1/checkouts",
            headers={
                "Authorization": f"Bearer {POLAR_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "product_id": POLAR_PRODUCT_ID,
                "success_url": f"{FRONTEND_URL}/subscribe/success",
                "customer_email": user["email"],
                "metadata": {"user_id": str(user_id)},
            }
        )

    if resp.status_code != 201:
        raise HTTPException(status_code=502, detail="polar.sh checkout 생성 실패")

    data = resp.json()
    return {"checkout_url": data["url"]}


@router.post("/webhooks/polar")
async def polar_webhook(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db)
):
    body = await request.body()
    signature = request.headers.get("webhook-signature", "")

    if POLAR_WEBHOOK_SECRET:
        expected = hmac.new(
            POLAR_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = json.loads(body)
    event_type = payload.get("type")

    if event_type == "subscription.created":
        subscription_data = payload.get("data", {})
        user_id = subscription_data.get("metadata", {}).get("user_id")
        polar_sub_id = subscription_data.get("id")

        if user_id:
            expires_at = datetime.utcnow() + timedelta(days=30)
            await db.execute(
                """INSERT INTO subscriptions (user_id, polar_subscription_id, status, expires_at)
                   VALUES (?, ?, 'active', ?)""",
                (int(user_id), polar_sub_id, expires_at)
            )
            await db.commit()

    elif event_type == "subscription.cancelled":
        subscription_data = payload.get("data", {})
        polar_sub_id = subscription_data.get("id")
        await db.execute(
            "UPDATE subscriptions SET status='cancelled' WHERE polar_subscription_id=?",
            (polar_sub_id,)
        )
        await db.commit()

    return {"status": "ok"}
```

---

## Task 7: Backend — main.py

**Files:**
- Create: `backend/main.py`
- Create: `backend/.env` (로컬 테스트용, .gitignore에 추가)

- [ ] **Step 1: backend/main.py 생성**

```python
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
import auth
import courses
import payment


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="DeepLearn API", lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(payment.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: 백엔드 로컬 실행 테스트**

```bash
cd backend
cp ../.env.example .env
# .env 파일에 실제 값 입력 후:
uvicorn main:app --reload --port 8000
```

Expected: `http://localhost:8000/docs` 에서 Swagger UI 접근 가능, `/health` → `{"status":"ok"}`

---

## Task 8: Frontend — 진입점 & 라우터

**Files:**
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/index.css`

- [ ] **Step 1: frontend/src/index.css 생성**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', sans-serif;
  background-color: #FFFAFA;
}
```

- [ ] **Step 2: frontend/src/main.jsx 생성**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 3: frontend/src/App.jsx 생성**

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import CoursePage from './pages/CoursePage'
import AuthCallback from './pages/AuthCallback'
import Subscribe from './pages/Subscribe'
import SubscribeSuccess from './pages/SubscribeSuccess'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/course/:id" element={<CoursePage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/subscribe" element={<Subscribe />} />
          <Route path="/subscribe/success" element={<SubscribeSuccess />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
```

---

## Task 9: Frontend — API Client & AuthContext

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/context/AuthContext.jsx`

- [ ] **Step 1: frontend/src/api/client.js 생성**

```js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({ baseURL: API_BASE })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client
```

- [ ] **Step 2: frontend/src/context/AuthContext.jsx 생성**

```jsx
import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      client.get(`/auth/me?token=${token}`)
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = () => {
    window.location.href = `${import.meta.env.VITE_API_URL || ''}/auth/google`
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

---

## Task 10: Frontend — Header & CourseCard

**Files:**
- Create: `frontend/src/components/Header.jsx`
- Create: `frontend/src/components/CourseCard.jsx`

- [ ] **Step 1: frontend/src/components/Header.jsx 생성**

```jsx
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Header() {
  const { user, login, logout } = useAuth()

  return (
    <header className="bg-white border-b border-pink-100 shadow-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <span className="font-bold text-xl text-gray-800">DeepLearn</span>
          <span className="text-xs bg-pink-100 text-pink-600 px-2 py-0.5 rounded-full font-medium">Week5</span>
        </Link>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              {user.is_subscribed ? (
                <span className="text-xs bg-gradient-to-r from-pink-400 to-pink-600 text-white px-3 py-1 rounded-full font-medium">
                  ✨ 구독 중
                </span>
              ) : (
                <Link
                  to="/subscribe"
                  className="text-sm bg-gradient-to-r from-pink-300 to-pink-500 text-white px-4 py-1.5 rounded-full font-medium hover:opacity-90 transition"
                >
                  구독하기
                </Link>
              )}
              <div className="flex items-center gap-2">
                {user.picture && (
                  <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full border-2 border-pink-200" />
                )}
                <span className="text-sm text-gray-700 hidden sm:block">{user.name}</span>
                <button
                  onClick={logout}
                  className="text-sm text-gray-400 hover:text-gray-600 transition"
                >
                  로그아웃
                </button>
              </div>
            </>
          ) : (
            <button
              onClick={login}
              className="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition shadow-sm"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google로 로그인
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
```

- [ ] **Step 2: frontend/src/components/CourseCard.jsx 생성**

```jsx
import { Link } from 'react-router-dom'

export default function CourseCard({ course }) {
  return (
    <Link to={`/course/${course.id}`} className="block">
      <div className="bg-white rounded-2xl border border-pink-100 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 p-6 h-full">
        <div className="flex items-start justify-between mb-3">
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
            course.is_free
              ? 'bg-green-100 text-green-600'
              : 'bg-pink-100 text-pink-600'
          }`}>
            {course.is_free ? '무료 미리보기' : '구독 전용'}
          </span>
          <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full">{course.level}</span>
        </div>
        <h3 className="font-bold text-gray-800 text-lg mb-2 leading-snug line-clamp-2">{course.title}</h3>
        <p className="text-gray-500 text-sm mb-4 line-clamp-2">{course.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {course.duration}
          </span>
          <span className="text-pink-500 text-sm font-medium">수강하기 →</span>
        </div>
      </div>
    </Link>
  )
}
```

---

## Task 11: Frontend — Home 페이지

**Files:**
- Create: `frontend/src/pages/Home.jsx`

- [ ] **Step 1: frontend/src/pages/Home.jsx 생성**

```jsx
import { useEffect, useState } from 'react'
import Header from '../components/Header'
import CourseCard from '../components/CourseCard'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'
import { Link } from 'react-router-dom'

export default function Home() {
  const { user, login } = useAuth()
  const [courses, setCourses] = useState([])

  useEffect(() => {
    client.get('/api/courses').then(res => setCourses(res.data))
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      <Header />

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 pt-16 pb-12 text-center">
        <div className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <span>✨</span> Week5 딥러닝 심화 강의
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          딥러닝의 핵심을<br />
          <span className="bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent">
            완벽하게 이해하세요
          </span>
        </h1>
        <p className="text-gray-500 text-lg mb-8 max-w-xl mx-auto">
          Regularization부터 CNN 실습까지 — 이론과 코드를 함께 배우는 5개 강의
        </p>
        {!user && (
          <button
            onClick={login}
            className="bg-gradient-to-r from-pink-400 to-pink-600 text-white px-8 py-3 rounded-full font-semibold text-lg hover:opacity-90 transition shadow-lg shadow-pink-200"
          >
            무료로 시작하기
          </button>
        )}
        {user && !user.is_subscribed && (
          <Link
            to="/subscribe"
            className="bg-gradient-to-r from-pink-400 to-pink-600 text-white px-8 py-3 rounded-full font-semibold text-lg hover:opacity-90 transition shadow-lg shadow-pink-200"
          >
            전체 강의 구독하기 →
          </Link>
        )}
      </section>

      {/* Stats */}
      <section className="max-w-6xl mx-auto px-4 pb-12">
        <div className="grid grid-cols-3 gap-4 max-w-lg mx-auto">
          {[
            { value: '5', label: '강의' },
            { value: '4+', label: '시간' },
            { value: '100%', label: '실습 코드' },
          ].map(stat => (
            <div key={stat.label} className="text-center bg-white rounded-2xl border border-pink-100 py-4 shadow-sm">
              <div className="text-2xl font-bold text-pink-500">{stat.value}</div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Course Grid */}
      <section className="max-w-6xl mx-auto px-4 pb-20">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">강의 목록</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {courses.map(course => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      </section>
    </div>
  )
}
```

---

## Task 12: Frontend — LectureContent & SubscribeBanner

**Files:**
- Create: `frontend/src/components/LectureContent.jsx`
- Create: `frontend/src/components/SubscribeBanner.jsx`

- [ ] **Step 1: frontend/src/components/LectureContent.jsx 생성**

```jsx
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

function renderText(text) {
  if (!text) return null
  return text.split('\n').map((line, i) => {
    const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/)
    return (
      <span key={i}>
        {parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>
          }
          if (part.startsWith('`') && part.endsWith('`')) {
            return <code key={j} className="bg-pink-50 text-pink-700 px-1 py-0.5 rounded text-sm font-mono">{part.slice(1, -1)}</code>
          }
          return part
        })}
        {i < text.split('\n').length - 1 && <br />}
      </span>
    )
  })
}

function renderBody(body) {
  if (!body) return null
  const lines = body.split('\n')
  const elements = []
  let tableLines = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.startsWith('|')) {
      tableLines.push(line)
    } else {
      if (tableLines.length > 0) {
        elements.push(<TableRenderer key={i} lines={tableLines} />)
        tableLines = []
      }
      if (line.startsWith('- ')) {
        elements.push(
          <li key={i} className="text-gray-600 text-sm leading-relaxed ml-4 list-disc">
            {renderText(line.slice(2))}
          </li>
        )
      } else if (line.trim()) {
        elements.push(
          <p key={i} className="text-gray-600 text-sm leading-relaxed">
            {renderText(line)}
          </p>
        )
      } else {
        elements.push(<div key={i} className="h-2" />)
      }
    }
  }
  if (tableLines.length > 0) {
    elements.push(<TableRenderer key="table-end" lines={tableLines} />)
  }
  return elements
}

function TableRenderer({ lines }) {
  const rows = lines.filter(l => !l.match(/^\|[-| :]+\|$/))
  const headers = rows[0]?.split('|').filter(Boolean).map(h => h.trim())
  const body = rows.slice(1)
  return (
    <div className="overflow-x-auto my-3">
      <table className="min-w-full text-sm border-collapse">
        <thead>
          <tr className="bg-pink-50">
            {headers?.map((h, i) => (
              <th key={i} className="border border-pink-200 px-3 py-2 text-left text-pink-700 font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-pink-50/30'}>
              {row.split('|').filter(Boolean).map((cell, j) => (
                <td key={j} className="border border-pink-100 px-3 py-2 text-gray-600">{renderText(cell.trim())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function LectureContent({ content }) {
  if (!content) return null
  const { sections } = content

  return (
    <div className="space-y-8">
      {sections.map((section, idx) => (
        <div key={idx} className="bg-white rounded-2xl border border-pink-100 p-6 shadow-sm">
          <h3 className="font-bold text-gray-800 text-lg mb-4 flex items-center gap-2">
            <span className="w-7 h-7 bg-gradient-to-br from-pink-300 to-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              {idx + 1}
            </span>
            {section.title}
          </h3>
          {section.body && (
            <div className="mb-4 space-y-1">{renderBody(section.body)}</div>
          )}
          {section.code && (
            <div className="rounded-xl overflow-hidden border border-pink-100">
              <div className="bg-pink-50 px-4 py-2 flex items-center gap-2 border-b border-pink-100">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <span className="text-xs text-pink-400 font-medium">Python</span>
              </div>
              <SyntaxHighlighter
                language="python"
                style={oneLight}
                customStyle={{ margin: 0, borderRadius: 0, fontSize: '0.8rem', background: '#fff' }}
              >
                {section.code}
              </SyntaxHighlighter>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: frontend/src/components/SubscribeBanner.jsx 생성**

```jsx
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function SubscribeBanner() {
  const { user, login } = useAuth()

  return (
    <div className="relative">
      {/* 블러 미리보기 */}
      <div className="blur-sm pointer-events-none select-none bg-white rounded-2xl border border-pink-100 p-6 shadow-sm">
        <div className="h-4 bg-pink-100 rounded w-3/4 mb-3" />
        <div className="h-4 bg-pink-100 rounded w-1/2 mb-6" />
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="h-3 bg-gray-200 rounded w-full mb-2" />
          <div className="h-3 bg-gray-200 rounded w-5/6 mb-2" />
          <div className="h-3 bg-gray-200 rounded w-4/6" />
        </div>
      </div>

      {/* 오버레이 */}
      <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-pink-50/80 to-white/95 rounded-2xl">
        <div className="text-center px-6">
          <div className="text-4xl mb-3">🔒</div>
          <h3 className="font-bold text-gray-800 text-xl mb-2">구독 전용 강의입니다</h3>
          <p className="text-gray-500 text-sm mb-5">
            월 구독권으로 모든 강의를 무제한 수강하세요
          </p>
          {user ? (
            <Link
              to="/subscribe"
              className="bg-gradient-to-r from-pink-400 to-pink-600 text-white px-6 py-3 rounded-full font-semibold hover:opacity-90 transition shadow-lg shadow-pink-200 inline-block"
            >
              지금 구독하기 →
            </Link>
          ) : (
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={login}
                className="bg-white border border-gray-300 text-gray-700 px-5 py-2.5 rounded-full font-medium hover:bg-gray-50 transition text-sm"
              >
                Google로 로그인
              </button>
              <Link
                to="/subscribe"
                className="bg-gradient-to-r from-pink-400 to-pink-600 text-white px-5 py-2.5 rounded-full font-medium hover:opacity-90 transition text-sm"
              >
                구독하기
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

---

## Task 13: Frontend — CoursePage, AuthCallback, Subscribe, SubscribeSuccess

**Files:**
- Create: `frontend/src/pages/CoursePage.jsx`
- Create: `frontend/src/pages/AuthCallback.jsx`
- Create: `frontend/src/pages/Subscribe.jsx`
- Create: `frontend/src/pages/SubscribeSuccess.jsx`

- [ ] **Step 1: frontend/src/pages/AuthCallback.jsx 생성**

```jsx
import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

export default function AuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const token = params.get('token')
    if (token) {
      localStorage.setItem('token', token)
    }
    navigate('/')
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-pink-50">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-pink-300 border-t-pink-600 rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-500">로그인 중...</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: frontend/src/pages/CoursePage.jsx 생성**

```jsx
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Header from '../components/Header'
import LectureContent from '../components/LectureContent'
import SubscribeBanner from '../components/SubscribeBanner'
import client from '../api/client'

export default function CoursePage() {
  const { id } = useParams()
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client.get(`/api/courses/${id}`)
      .then(res => setCourse(res.data))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-pink-50">
      <div className="w-10 h-10 border-4 border-pink-300 border-t-pink-600 rounded-full animate-spin" />
    </div>
  )

  if (!course) return (
    <div className="min-h-screen bg-pink-50">
      <Header />
      <div className="text-center pt-20 text-gray-500">강의를 찾을 수 없습니다.</div>
    </div>
  )

  const levelColors = { '초급': 'bg-green-100 text-green-600', '중급': 'bg-yellow-100 text-yellow-600', '고급': 'bg-red-100 text-red-600' }

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <Link to="/" className="text-pink-400 hover:text-pink-600 text-sm mb-4 inline-flex items-center gap-1">
          ← 강의 목록
        </Link>

        {/* Course Header */}
        <div className="bg-white rounded-2xl border border-pink-100 shadow-sm p-8 mb-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${course.is_free ? 'bg-green-100 text-green-600' : 'bg-pink-100 text-pink-600'}`}>
              {course.is_free ? '무료 미리보기' : '구독 전용'}
            </span>
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${levelColors[course.level] || 'bg-gray-100 text-gray-600'}`}>
              {course.level}
            </span>
            <span className="text-xs text-gray-400 bg-gray-50 px-2.5 py-1 rounded-full">⏱ {course.duration}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">{course.title}</h1>
          <p className="text-gray-500">{course.description}</p>
        </div>

        {/* Content or Lock */}
        {course.locked ? (
          <SubscribeBanner />
        ) : (
          <LectureContent content={course.content} />
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: frontend/src/pages/Subscribe.jsx 생성**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

export default function Subscribe() {
  const { user, login } = useAuth()
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubscribe = async () => {
    if (!user) { login(); return }
    setLoading(true)
    try {
      const res = await client.post('/api/subscribe/create')
      window.location.href = res.data.checkout_url
    } catch (e) {
      alert('결제 페이지를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      <Header />
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-3xl border border-pink-100 shadow-sm p-10">
          <div className="text-5xl mb-4">✨</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">전체 강의 구독</h1>
          <p className="text-gray-500 mb-8">5개 딥러닝 강의 무제한 수강</p>

          <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-2xl p-6 mb-8">
            <div className="text-4xl font-bold text-pink-600 mb-1">₩9,900</div>
            <div className="text-pink-400 text-sm">/ 월</div>
          </div>

          <ul className="text-left space-y-3 mb-8">
            {[
              'Regularization (무료 미리보기 포함)',
              'Overfitting vs Underfitting',
              'Data Augmentation',
              'Transfer Learning (MobileNetV2)',
              'CNN 실습 (MNIST)',
            ].map((item, i) => (
              <li key={i} className="flex items-center gap-3 text-gray-600 text-sm">
                <span className="w-5 h-5 bg-pink-100 text-pink-500 rounded-full flex items-center justify-center text-xs flex-shrink-0">✓</span>
                {item}
              </li>
            ))}
          </ul>

          <button
            onClick={handleSubscribe}
            disabled={loading}
            className="w-full bg-gradient-to-r from-pink-400 to-pink-600 text-white py-4 rounded-2xl font-bold text-lg hover:opacity-90 transition disabled:opacity-60 shadow-lg shadow-pink-200"
          >
            {loading ? '처리 중...' : user ? '구독 시작하기' : 'Google 로그인 후 구독하기'}
          </button>
          <p className="text-xs text-gray-400 mt-3">polar.sh 샌드박스 결제 (실제 청구 없음)</p>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: frontend/src/pages/SubscribeSuccess.jsx 생성**

```jsx
import { Link } from 'react-router-dom'
import Header from '../components/Header'

export default function SubscribeSuccess() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      <Header />
      <div className="max-w-lg mx-auto px-4 py-24 text-center">
        <div className="text-6xl mb-6">🎉</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">구독 완료!</h1>
        <p className="text-gray-500 mb-8">이제 모든 딥러닝 강의를 수강할 수 있습니다.</p>
        <Link
          to="/"
          className="bg-gradient-to-r from-pink-400 to-pink-600 text-white px-8 py-3 rounded-full font-semibold hover:opacity-90 transition shadow-lg shadow-pink-200 inline-block"
        >
          강의 시작하기 →
        </Link>
      </div>
    </div>
  )
}
```

---

## Task 14: 문서 작성 (PRD, TRD, README)

**Files:**
- Create: `PRD.md`
- Create: `TRD.md`
- Create: `README.md`

- [ ] **Step 1: PRD.md 생성**

```markdown
# 제품 요구사항 문서 (PRD)

## 제품 개요
Week5 딥러닝 강의 구독 플랫폼. Regularization, Overfitting, Data Augmentation, Transfer Learning, CNN 내용을 강의로 제공하며 구독 기반 수익 모델을 채택한다.

## 목표 사용자
- 딥러닝을 공부하는 대학생 / 취준생
- Week5 수업 내용을 복습하고 싶은 학습자

## 핵심 기능

### F1. 강의 목록 (비로그인 접근 가능)
- 5개 강의 카드 표시
- 각 카드: 제목, 설명, 난이도, 수강 시간, 무료/유료 뱃지
- 강의 클릭 시 상세 페이지 이동

### F2. Google OAuth2 로그인
- 헤더의 "Google로 로그인" 버튼 클릭
- Google 계정 선택 후 자동 회원가입/로그인
- JWT 토큰 발급 후 로컬 스토리지 저장

### F3. 강의 상세 페이지
- 무료 강의(#1): 비로그인도 전체 내용 열람
- 유료 강의(#2~5): 비구독자에게 블러 처리 + 구독 유도 배너

### F4. polar.sh 구독 결제
- 월 ₩9,900 구독권 구매
- polar.sh 샌드박스 환경에서 테스트
- 결제 완료 후 webhook으로 구독 상태 자동 업데이트

### F5. 구독자 전용 콘텐츠
- 결제 완료 유저만 유료 강의 열람 가능
- 강의 내용: 개념 설명 + Python 코드 예시 + 핵심 요약

## 비기능 요구사항
- 응답 시간: API 200ms 이내
- UI: 라이트 테마, 연핑크 포인트 색상, 모바일 반응형
- 보안: JWT 인증, polar.sh webhook 서명 검증
```

- [ ] **Step 2: TRD.md 생성**

```markdown
# 기술 요구사항 문서 (TRD)

## 시스템 아키텍처

```
[React SPA: Vercel]  ←→  [FastAPI: Railway/Render]  ←→  [SQLite]
                                    ↕
                            [Google OAuth2 API]
                            [polar.sh API]
```

## 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| Frontend | React + Vite | 18.x / 5.x |
| 스타일 | Tailwind CSS | 3.x |
| 라우팅 | React Router | 6.x |
| HTTP | Axios | 1.x |
| Backend | FastAPI | 0.111 |
| 런타임 | Python | 3.11 |
| DB | SQLite (aiosqlite) | 0.20 |
| 인증 | python-jose (JWT) | 3.3 |
| 배포(FE) | Vercel | - |
| 배포(BE) | Railway 또는 Render | - |

## API 명세

### 인증
- `GET /auth/google` — Google OAuth 시작, Google 로그인 페이지로 리다이렉트
- `GET /auth/google/callback?code=` — OAuth 콜백, JWT 발급 후 프론트로 리다이렉트
- `GET /auth/me?token=` — 현재 유저 정보 + 구독 상태 반환

### 강의
- `GET /api/courses` — 강의 목록 (공개, 콘텐츠 제외)
- `GET /api/courses/:id` — 강의 상세 (구독 여부에 따라 content 필드 포함 여부 결정)

### 결제
- `POST /api/subscribe/create` — polar.sh checkout URL 생성 (JWT 필요)
- `POST /webhooks/polar` — polar.sh 결제 완료 webhook 수신

## 데이터베이스 스키마

```sql
users (id, google_id, email, name, picture, created_at)
subscriptions (id, user_id, polar_subscription_id, status, created_at, expires_at)
```

## 인증 플로우
1. 프론트 → `/auth/google` 요청
2. FastAPI → Google 로그인 URL로 리다이렉트
3. Google → `/auth/google/callback?code=xxx` 호출
4. FastAPI → Google Token API로 액세스 토큰 교환
5. FastAPI → Google UserInfo API로 사용자 정보 조회
6. FastAPI → DB에 유저 upsert, JWT 발급
7. FastAPI → 프론트 `/auth/callback?token=xxx`로 리다이렉트
8. 프론트 → 토큰 localStorage 저장, 홈으로 이동

## 환경변수

```
GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
POLAR_ACCESS_TOKEN, POLAR_PRODUCT_ID, POLAR_WEBHOOK_SECRET
BACKEND_URL, FRONTEND_URL
```

## 배포 설정
- **Vercel**: `vercel.json`의 rewrites로 SPA 라우팅 처리
- **Railway/Render**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- CORS: 프로덕션 프론트 URL 화이트리스트 등록 필요
```

- [ ] **Step 3: README.md 생성**

```markdown
# DeepLearn — Week5 딥러닝 강의 구독 플랫폼

Week5 딥러닝 내용(Regularization, Overfitting, Data Augmentation, Transfer Learning, CNN)을 제공하는 구독 기반 강의 플랫폼입니다.

## 로컬 실행 방법

### 사전 준비
- Python 3.11+
- Node.js 18+
- Google Cloud Console에서 OAuth2 클라이언트 생성
- polar.sh 계정 및 샌드박스 상품 생성

### 1. 저장소 클론 및 환경변수 설정

```bash
git clone <repo-url>
cd week5_HW
cp .env.example backend/.env
```

`backend/.env` 파일을 열어 아래 값을 입력하세요:

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
JWT_SECRET_KEY=랜덤_긴_문자열_입력
POLAR_ACCESS_TOKEN=...
POLAR_PRODUCT_ID=...
POLAR_WEBHOOK_SECRET=...
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### 3. 프론트엔드 실행

새 터미널을 열고:

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

http://localhost:5173 에서 확인

### 4. Google OAuth 설정
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 → API 및 서비스 → 사용자 인증 정보
3. OAuth 2.0 클라이언트 ID 생성 (웹 애플리케이션)
4. 승인된 리디렉션 URI에 `http://localhost:8000/auth/google/callback` 추가
5. 클라이언트 ID/시크릿을 `.env`에 입력

### 5. polar.sh 샌드박스 설정
1. [polar.sh](https://polar.sh) 가입 후 조직 생성
2. 샌드박스 모드에서 구독 상품 생성 (월 ₩9,900)
3. Access Token 발급 → `.env`에 입력
4. Webhook 설정: `http://localhost:8000/webhooks/polar` (개발 시 ngrok 필요)

## 배포

### 백엔드 (Railway)
1. Railway에서 새 프로젝트 → GitHub 연결
2. `backend/` 디렉토리를 루트로 설정
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 환경변수 설정 (`.env.example` 참고)

### 프론트엔드 (Vercel)
1. Vercel에서 새 프로젝트 → GitHub 연결
2. Framework: Vite
3. Root Directory: `frontend`
4. 환경변수: `VITE_API_URL=https://your-backend.railway.app`
5. 배포 후 Google OAuth 리디렉션 URI에 프로덕션 URL 추가

## 기능
- 강의 목록 페이지 (비로그인 접근 가능)
- Google OAuth2 로그인/회원가입
- polar.sh 샌드박스 결제 (월 구독)
- 구독자 전용 강의 콘텐츠 열람
- 라이트 핑크 테마 모던 UI
```

---

## Task 15: 최종 검증 & 실행

- [ ] **Step 1: 전체 파일 구조 확인**

```bash
find week5_HW -type f | grep -v node_modules | grep -v __pycache__ | sort
```

- [ ] **Step 2: 백엔드 실행 및 엔드포인트 테스트**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

다른 터미널에서:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:8000/api/courses
# Expected: 5개 강의 목록 JSON 배열

curl http://localhost:8000/api/courses/1
# Expected: id=1 강의 (content 포함, 무료)

curl http://localhost:8000/api/courses/2
# Expected: id=2 강의 (locked=true, content=null)
```

- [ ] **Step 3: 프론트엔드 빌드 확인**

```bash
cd frontend
npm run build
# Expected: dist/ 폴더 생성, 에러 없음
```

- [ ] **Step 4: 로컬 전체 동작 확인 체크리스트**

- [ ] 홈 페이지 강의 목록 5개 표시됨
- [ ] 강의 #1 클릭 시 전체 콘텐츠 표시됨 (무료)
- [ ] 강의 #2 클릭 시 블러 + 구독 유도 배너 표시됨
- [ ] "Google로 로그인" 버튼 클릭 시 Google 로그인 페이지로 이동
- [ ] 로그인 후 헤더에 프로필 사진 + 이름 표시
- [ ] 구독 페이지에서 결제 버튼 클릭 시 polar.sh로 이동
