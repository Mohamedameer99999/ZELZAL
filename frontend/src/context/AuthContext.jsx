import { createContext, useState, useEffect, useCallback } from 'react'
import { authAPI } from '../api'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('zelzal_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const { data } = await authAPI.me()
      setUser(data.user)
    } catch {
      localStorage.removeItem('zelzal_token')
      localStorage.removeItem('zelzal_refresh')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = async (username, password) => {
    const { data } = await authAPI.login(username, password)
    localStorage.setItem('zelzal_token', data.access_token)
    localStorage.setItem('zelzal_refresh', data.refresh_token)
    setUser(data.user)
    return data
  }

  const register = async (username, email, password) => {
    const { data } = await authAPI.register(username, email, password)
    localStorage.setItem('zelzal_token', data.access_token)
    localStorage.setItem('zelzal_refresh', data.refresh_token)
    setUser(data.user)
    return data
  }

  const logout = () => {
    localStorage.removeItem('zelzal_token')
    localStorage.removeItem('zelzal_refresh')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, loadUser }}>
      {children}
    </AuthContext.Provider>
  )
}
