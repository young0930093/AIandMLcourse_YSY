import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import CoursePage from './pages/CoursePage'
import AuthCallback from './pages/AuthCallback'
import Subscribe from './pages/Subscribe'
import SubscribeSuccess from './pages/SubscribeSuccess'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/course/:id" element={<CoursePage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/subscribe" element={<Subscribe />} />
          <Route path="/subscribe/success" element={<SubscribeSuccess />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
