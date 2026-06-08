import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import MatrixRain from '../Common/MatrixRain'
import ParticleBackground from '../Common/ParticleBackground'
import { NotificationProvider } from '../Common/Notification'
import { useLanguage } from '../../hooks/useLanguage'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { lang } = useLanguage()
  const isRTL = lang === 'ar'

  return (
    <NotificationProvider>
      <div className="min-h-screen bg-cyber-black" dir={isRTL ? 'rtl' : 'ltr'}>
        <MatrixRain opacity={0.08} />
        <ParticleBackground count={40} />
        <Navbar
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />
        <div className="flex pt-16 relative z-10">
          <Sidebar
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
          <motion.main
            initial={{ opacity: 0, x: isRTL ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
            className="flex-1 p-4 md:p-6 lg:p-8 min-h-[calc(100vh-4rem)] overflow-x-hidden"
          >
            <Outlet />
          </motion.main>
        </div>
      </div>
    </NotificationProvider>
  )
}
