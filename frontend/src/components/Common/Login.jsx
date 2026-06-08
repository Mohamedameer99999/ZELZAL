import { useState } from 'react'
import { motion } from 'framer-motion'
import { FiGlobe } from 'react-icons/fi'
import { useAuth } from '../../hooks/useAuth'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'
import MatrixRain from './MatrixRain'
import ParticleBackground from './ParticleBackground'
import ZelzalLogo from './ZelzalLogo'

export default function Login() {
  const { login, register } = useAuth()
  const { lang, toggleLang } = useLanguage()
  const t = translations[lang]
  const [isLogin, setIsLogin] = useState(true)
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isLogin) {
        await login(form.username, form.password)
      } else {
        await register(form.username, form.email, form.password)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-cyber-black relative overflow-hidden p-4" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <MatrixRain opacity={0.2} />
      <ParticleBackground count={40} />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="glass rounded-2xl p-8 md:p-10 border border-neon-green/20">
          <div className="flex justify-between items-center mb-6">
            <div />
            <ZelzalLogo size="lg" />
            <button
              onClick={toggleLang}
              className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-neon-green border border-cyber-border rounded-lg hover:border-neon-green/30 transition-all"
            >
              <FiGlobe size={12} />
              {lang === 'en' ? 'AR' : 'EN'}
            </button>
          </div>

          <div className="flex mb-8 bg-cyber-dark rounded-lg p-1">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 text-sm rounded-md transition-all ${
                isLogin ? 'bg-neon-green text-cyber-black shadow-neon-sm' : 'text-gray-500 hover:text-neon-green'
              }`}
            >
              {t.login.toUpperCase()}
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 text-sm rounded-md transition-all ${
                !isLogin ? 'bg-neon-green text-cyber-black shadow-neon-sm' : 'text-gray-500 hover:text-neon-green'
              }`}
            >
              {t.register.toUpperCase()}
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1 tracking-wider">{t.username.toUpperCase()}</label>
              <input
                type="text"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                className="w-full cyber-input rounded-lg px-4 py-3 text-sm"
                placeholder={t.username}
                required
              />
            </div>

            {!isLogin && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
              >
                <label className="block text-xs text-gray-500 mb-1 tracking-wider">{t.email.toUpperCase()}</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full cyber-input rounded-lg px-4 py-3 text-sm"
                  placeholder={t.email}
                  required
                />
              </motion.div>
            )}

            <div>
              <label className="block text-xs text-gray-500 mb-1 tracking-wider">{t.password.toUpperCase()}</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full cyber-input rounded-lg px-4 py-3 text-sm"
                placeholder={t.password}
                required
                minLength={6}
              />
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-red-500 text-xs text-center"
              >
                {error}
              </motion.p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full cyber-btn rounded-lg py-3 text-sm font-bold tracking-wider disabled:opacity-50"
            >
              {loading ? t.authenticating : isLogin ? t.login.toUpperCase() : t.register.toUpperCase()}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-cyber-border">
            <p className="text-center text-xs text-gray-600">
              {t.secured_by}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
