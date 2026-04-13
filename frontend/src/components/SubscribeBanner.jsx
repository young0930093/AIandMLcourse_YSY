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
