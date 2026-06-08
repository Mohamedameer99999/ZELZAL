import { useState } from 'react'
import { motion } from 'framer-motion'
import { FiSave, FiGlobe, FiSun, FiMoon, FiBell, FiUser, FiMail } from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'
import { useAuth } from '../../hooks/useAuth'

export default function Settings() {
  const { lang, setLang } = useLanguage()
  const t = translations[lang]
  const { user } = useAuth()
  const [theme, setTheme] = useState('dark')
  const [notifEnabled, setNotifEnabled] = useState(true)
  const [profile, setProfile] = useState({
    username: user?.username || '',
    email: user?.email || '',
    bio: user?.bio || '',
  })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6">
      <NeonText size="xl">{t.settings_title.toUpperCase()}</NeonText>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard delay={0.1}>
          <div className="flex items-center gap-2 mb-6">
            <FiUser className="text-neon-green" />
            <h3 className="text-sm text-neon-green tracking-wider">{t.profile_settings.toUpperCase()}</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">{t.username.toUpperCase()}</label>
              <input
                type="text"
                value={profile.username}
                onChange={(e) => setProfile({ ...profile, username: e.target.value })}
                className="w-full cyber-input rounded-lg px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">{t.email.toUpperCase()}</label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full cyber-input rounded-lg px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">{t.description.toUpperCase()}</label>
              <textarea
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                className="w-full cyber-input rounded-lg px-4 py-2.5 text-sm resize-none h-24"
              />
            </div>
            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={handleSave}
              className="flex items-center gap-2 px-6 py-2.5 cyber-btn rounded-lg text-sm"
            >
              <FiSave size={16} />
              {saved ? `${t.success}!` : t.save}
            </motion.button>
          </div>
        </GlassCard>

        <div className="space-y-6">
          <GlassCard delay={0.2}>
            <div className="flex items-center gap-2 mb-6">
              <FiGlobe className="text-neon-green" />
              <h3 className="text-sm text-neon-green tracking-wider">{t.language.toUpperCase()}</h3>
            </div>
            <div className="flex gap-3">
              {['en', 'ar'].map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`flex-1 py-3 rounded-lg text-sm font-bold transition-all border ${
                    lang === l
                      ? 'bg-neon-green text-cyber-black shadow-neon-sm border-neon-green'
                      : 'bg-cyber-dark text-gray-400 border-cyber-border hover:border-neon-green/30'
                  }`}
                >
                  {l === 'en' ? 'ENGLISH' : 'العربية'}
                </button>
              ))}
            </div>
          </GlassCard>

          <GlassCard delay={0.3}>
            <div className="flex items-center gap-2 mb-6">
              <FiBell className="text-neon-green" />
              <h3 className="text-sm text-neon-green tracking-wider">{t.notifications.toUpperCase()}</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">{t.notifications}</span>
                <button
                  onClick={() => setNotifEnabled(!notifEnabled)}
                  className={`w-12 h-6 rounded-full transition-all ${
                    notifEnabled ? 'bg-neon-green' : 'bg-cyber-light'
                  }`}
                >
                  <motion.div
                    animate={{ x: notifEnabled ? 24 : 2 }}
                    className="w-5 h-5 bg-cyber-black rounded-full mt-0.5 mx-0.5"
                  />
                </button>
              </div>
            </div>
          </GlassCard>

          <GlassCard delay={0.4}>
            <div className="flex items-center gap-2 mb-6">
              <FiSun className="text-neon-green" />
              <h3 className="text-sm text-neon-green tracking-wider">{t.theme.toUpperCase()}</h3>
            </div>
            <div className="flex gap-3">
              {[
                { key: 'dark', icon: FiMoon, label: t.dark_mode },
                { key: 'light', icon: FiSun, label: t.light_mode },
              ].map(({ key, icon: Icon, label }) => (
                <button
                  key={key}
                  onClick={() => setTheme(key)}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm transition-all border ${
                    theme === key
                      ? 'bg-neon-green text-cyber-black shadow-neon-sm border-neon-green'
                      : 'bg-cyber-dark text-gray-400 border-cyber-border hover:border-neon-green/30'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </button>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
