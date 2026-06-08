import { useState } from 'react'
import { motion } from 'framer-motion'
import { FiMenu, FiX, FiBell, FiLogOut, FiUser, FiGlobe } from 'react-icons/fi'
import ZelzalLogo from '../Common/ZelzalLogo'
import { useAuth } from '../../hooks/useAuth'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'

export default function Navbar({ onToggleSidebar, sidebarOpen }) {
  const { user, logout } = useAuth()
  const { lang, toggleLang } = useLanguage()
  const [showProfile, setShowProfile] = useState(false)
  const t = translations[lang]

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 h-16 glass border-b border-cyber-border">
      <div className="flex items-center justify-between h-full px-4 md:px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="text-gray-400 hover:text-neon-green transition-colors lg:hidden"
            aria-label="Toggle menu"
          >
            {sidebarOpen ? <FiX size={22} /> : <FiMenu size={22} />}
          </button>
          <ZelzalLogo size="sm" />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleLang}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono text-gray-400 hover:text-neon-green border border-cyber-border rounded-lg hover:border-neon-green/30 transition-all"
            aria-label="Toggle language"
          >
            <FiGlobe size={14} />
            {lang === 'en' ? 'AR' : 'EN'}
          </button>

          <button className="relative p-2 text-gray-400 hover:text-neon-green transition-colors">
            <FiBell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-neon-green rounded-full shadow-neon-sm" />
          </button>

          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-cyber-gray transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-neon-dark flex items-center justify-center border border-neon-green/30">
                <FiUser size={16} className="text-neon-green" />
              </div>
              <span className="hidden md:block text-sm text-gray-300">
                {user?.username || 'USER'}
              </span>
            </button>

            {showProfile && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute right-0 mt-2 w-48 glass rounded-xl border border-cyber-border overflow-hidden"
              >
                <div className="p-3 border-b border-cyber-border">
                  <p className="text-sm text-neon-green">{user?.username}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-neon-dark text-neon-green rounded border border-neon-green/30">
                    {user?.role?.toUpperCase()}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-gray-400 hover:text-red-500 hover:bg-cyber-gray transition-colors"
                >
                  <FiLogOut size={16} />
                  {t.disconnect}
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
