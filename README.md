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
