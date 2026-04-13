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
