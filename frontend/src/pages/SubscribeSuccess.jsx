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
