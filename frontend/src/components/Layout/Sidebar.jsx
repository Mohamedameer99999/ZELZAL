import { NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiHome, FiShield, FiCpu, FiFolder, FiBarChart2, FiUsers, FiSettings, FiShieldOff,
} from 'react-icons/fi'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'

export default function Sidebar({ open, onClose }) {
  const { lang } = useLanguage()
  const t = translations[lang]
  const isRTL = lang === 'ar'

  const navItems = [
    { path: '/dashboard', label: t.dashboard, icon: FiHome },
    { path: '/security', label: t.security_center, icon: FiShield },
    { path: '/ai-assistant', label: t.ai_assistant, icon: FiCpu },
    { path: '/projects', label: t.projects, icon: FiFolder },
    { path: '/analytics', label: t.analytics, icon: FiBarChart2 },
    { path: '/users', label: t.users, icon: FiUsers },
    { path: '/settings', label: t.settings, icon: FiSettings },
  ]

  const sidebarClass = (isActive) =>
    `flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all ${
      isActive
        ? 'bg-neon-green/10 text-neon-green border border-neon-green/30 shadow-neon-sm'
        : 'text-gray-400 hover:text-neon-green hover:bg-cyber-gray border border-transparent'
    }`

  const sidebarContent = (
    <>
      <div className="p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onClose}
            className={({ isActive }) => sidebarClass(isActive)}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="glass rounded-lg p-4 border border-cyber-border">
          <div className="flex items-center gap-2 mb-2">
            <FiShieldOff size={14} className="text-neon-green" />
            <span className="text-xs text-neon-green">SYSTEM STATUS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-neon-green rounded-full shadow-neon-sm animate-pulse" />
            <span className="text-xs text-gray-500">{t.all_systems_secure}</span>
          </div>
        </div>
      </div>
    </>
  )

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <AnimatePresence>
        {open && (
          <motion.aside
            initial={{ x: isRTL ? 280 : -280 }}
            animate={{ x: 0 }}
            exit={{ x: isRTL ? 280 : -280 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className={`fixed top-16 ${isRTL ? 'right-0' : 'left-0'} bottom-0 w-64 z-30 glass ${isRTL ? 'border-l' : 'border-r'} border-cyber-border overflow-y-auto lg:translate-x-0 lg:static lg:z-auto`}
          >
            {sidebarContent}
          </motion.aside>
        )}
      </AnimatePresence>

      <aside className={`hidden lg:block w-64 flex-shrink-0`}>
        <div className={`fixed top-16 ${isRTL ? 'right-0' : 'left-0'} bottom-0 w-64 glass ${isRTL ? 'border-l' : 'border-r'} border-cyber-border overflow-y-auto`}>
          <div className="p-4 space-y-1 pt-4">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => sidebarClass(isActive)}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
          <div className="absolute bottom-4 left-4 right-4">{/* status */}</div>
        </div>
      </aside>
    </>
  )
}
