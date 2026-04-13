import { Link } from 'react-router-dom'

export default function CourseCard({ course }) {
  return (
    <Link to={`/course/${course.id}`} className="block">
      <div className="bg-white rounded-2xl border border-pink-100 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 p-6 h-full">
        <div className="flex items-start justify-between mb-3">
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
            course.is_free
              ? 'bg-green-100 text-green-600'
              : 'bg-pink-100 text-pink-600'
          }`}>
            {course.is_free ? '무료 미리보기' : '구독 전용'}
          </span>
          <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full">{course.level}</span>
        </div>
        <h3 className="font-bold text-gray-800 text-lg mb-2 leading-snug line-clamp-2">{course.title}</h3>
        <p className="text-gray-500 text-sm mb-4 line-clamp-2">{course.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {course.duration}
          </span>
          <span className="text-pink-500 text-sm font-medium">수강하기 →</span>
        </div>
      </div>
    </Link>
  )
}
