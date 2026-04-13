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
