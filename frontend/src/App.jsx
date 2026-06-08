import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/Layout/Layout'
import Login from './components/Common/Login'
import LoadingScreen from './components/Common/LoadingScreen'
import CustomCursor from './components/Common/CustomCursor'
import { useAuth } from './hooks/useAuth'
import Dashboard from './components/Sections/Dashboard'
import SecurityCenter from './components/Sections/SecurityCenter'
import AIAssistant from './components/Sections/AIAssistant'
import ProjectsManager from './components/Sections/ProjectsManager'
import Analytics from './components/Sections/Analytics'
import UserManagement from './components/Sections/UserManagement'
import Settings from './components/Sections/Settings'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (user) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const [appLoading, setAppLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setAppLoading(false), 2500)
    return () => clearTimeout(timer)
  }, [])

  if (appLoading) return <LoadingScreen />

  return (
    <>
      <CustomCursor />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="security" element={<SecurityCenter />} />
            <Route path="ai-assistant" element={<AIAssistant />} />
            <Route path="projects" element={<ProjectsManager />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AnimatePresence>
    </>
  )
}
