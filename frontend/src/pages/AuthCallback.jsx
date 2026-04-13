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
