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
