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
