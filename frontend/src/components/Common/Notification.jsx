import { useState, useEffect, createContext, useContext, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiX, FiCheckCircle, FiAlertTriangle, FiInfo, FiAlertCircle } from 'react-icons/fi'

const NotificationContext = createContext(null)

export function useNotification() {
  return useContext(NotificationContext)
}

const icons = {
  success: <FiCheckCircle className="text-neon-green" />,
  error: <FiAlertCircle className="text-red-500" />,
  warning: <FiAlertTriangle className="text-yellow-500" />,
  info: <FiInfo className="text-blue-500" />,
}

const borders = {
  success: 'border-neon-green/30',
  error: 'border-red-500/30',
  warning: 'border-yellow-500/30',
  info: 'border-blue-500/30',
}

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([])

  const addNotification = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now()
    setNotifications((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id))
    }, duration)
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <div className="fixed top-4 right-4 z-[999] flex flex-col gap-2 max-w-sm w-full">
        <AnimatePresence>
          {notifications.map((n) => (
            <motion.div
              key={n.id}
              initial={{ opacity: 0, x: 100, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.9 }}
              className={`glass border ${borders[n.type]} rounded-lg p-4 flex items-start gap-3`}
            >
              <span className="mt-0.5">{icons[n.type]}</span>
              <p className="flex-1 text-sm text-gray-300">{n.message}</p>
              <button
                onClick={() => removeNotification(n.id)}
                className="text-gray-500 hover:text-white transition-colors"
              >
                <FiX size={16} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </NotificationContext.Provider>
  )
}
