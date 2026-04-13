# Deep Learning Lecture Subscription Platform — Design Spec

**Date:** 2026-04-13
**Project:** Week5 딥러닝 강의 구독 플랫폼

---

## Overview

Week5 딥러닝 학습 내용(Regularization, Overfitting, Data Augmentation, Transfer Learning, CNN)을 강의로 제공하는 구독 플랫폼. 비로그인 유저는 강의 목록과 무료 미리보기만 가능, Google OAuth2 로그인 후 polar.sh로 결제하면 전체 강의 열람 가능.

---

## Architecture

```
[Browser]
    │
    ├── React SPA (Vercel)
    │       ├── /              강의 목록 (공개)
    │       ├── /course/:id    강의 상세 (구독 여부로 분기)
    │       ├── /login         Google OAuth 시작
    │       └── /subscribe     polar.sh 결제
    │
    └── FastAPI (Railway/Render)
            ├── GET  /api/courses
            ├── GET  /api/courses/:id
            ├── GET  /auth/google
            ├── GET  /auth/google/callback
            ├── GET  /auth/me
            ├── POST /api/subscribe/create
            └── POST /webhooks/polar
                    │
                    └── SQLite (users, subscriptions)
```

### Auth Flow
1. 프론트 `/auth/google` 요청 → Google 로그인 → callback → JWT 발급 → 프론트 redirect
2. 모든 인증 API에 `Authorization: Bearer <token>` 헤더 사용

### Payment Flow
1. 로그인 유저 구독 버튼 → `/api/subscribe/create` → polar.sh checkout URL → 리다이렉트
2. 결제 완료 → polar.sh webhook → DB 구독 활성화

---

## Data Model

```sql
users
  id INTEGER PRIMARY KEY
  google_id TEXT UNIQUE NOT NULL
  email TEXT NOT NULL
  name TEXT
  picture TEXT
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP

subscriptions
  id INTEGER PRIMARY KEY
  user_id INTEGER REFERENCES users(id)
  polar_subscription_id TEXT
  status TEXT  -- 'active' | 'cancelled'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  expires_at DATETIME
```

---

## Course Content (Hardcoded)

| # | Title | Free |
|---|-------|------|
| 1 | Regularization — L1/L2, Dropout, Batch Normalization | ✅ |
| 2 | Overfitting vs Underfitting — 모델 복잡도와 성능 | ❌ |
| 3 | Data Augmentation — 이미지 데이터 증강 | ❌ |
| 4 | Transfer Learning — MobileNetV2로 분류기 만들기 | ❌ |
| 5 | CNN 실습 — MNIST 손글씨 인식 모델 구현 | ❌ |

각 강의 콘텐츠: 개념 설명 + 핵심 코드 예시(Python) + 요약 포인트 (실제 교육 콘텐츠)

---

## UI Design

- **테마**: 라이트 (배경 `#FFFAFA`, 카드 `#FFF0F5`)
- **포인트 색**: 연핑크 계열 (`#FFB6C1`, `#FF69B4`)
- **강의 목록**: 카드 그리드, 무료/유료 뱃지
- **강의 상세**: 사이드바 목차 + 콘텐츠, 코드 하이라이팅
- **잠긴 강의**: 블러 + 핑크 오버레이 + 구독 유도 배너
- **헤더**: 로그인 전 Google 버튼 / 로그인 후 프로필 + 구독 상태

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.11 |
| Auth | Google OAuth2 + python-jose JWT |
| Payment | polar.sh sandbox |
| DB | SQLite (aiosqlite) |
| Deploy | Vercel (FE) + Railway or Render (BE) |

---

## Project Structure

```
week5_HW/
├── frontend/
│   ├── src/
│   │   ├── pages/       Home, Course, Login, Subscribe
│   │   ├── components/  Header, CourseCard, LectureContent, SubscribeBanner
│   │   └── api/         axios client
│   ├── index.html
│   └── vite.config.js
├── backend/
│   ├── main.py
│   ├── auth.py          Google OAuth + JWT
│   ├── courses.py       강의 데이터 + API
│   ├── payment.py       polar.sh integration
│   ├── database.py      SQLite setup
│   └── requirements.txt
├── .env.example
├── PRD.md
├── TRD.md
├── README.md
└── vercel.json
```

---

## Environment Variables

```
# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=

# JWT
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256

# polar.sh
POLAR_ACCESS_TOKEN=
POLAR_PRODUCT_ID=
POLAR_WEBHOOK_SECRET=

# App
BACKEND_URL=
FRONTEND_URL=
```
