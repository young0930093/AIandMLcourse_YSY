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
