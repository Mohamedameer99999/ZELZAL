import { motion } from 'framer-motion'
import MatrixRain from './MatrixRain'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'

export default function LoadingScreen() {
  const { lang } = useLanguage()
  const t = translations[lang]

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-cyber-black">
      <MatrixRain />
      <div className="relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <h1 className="font-cyber text-6xl md:text-8xl font-bold text-neon-green animate-glow mb-4">
            ZELZAL
          </h1>
          <div className="flex items-center justify-center gap-1 mb-8">
            {[...Array(3)].map((_, i) => (
              <motion.span
                key={i}
                className="w-3 h-3 bg-neon-green rounded-full"
                animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
              />
            ))}
          </div>
          <motion.p
            className="font-mono text-sm text-neon-green/60 tracking-[0.3em]"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {t.loading.toUpperCase()}
          </motion.p>
          <div className="mt-6 w-64 mx-auto h-1 bg-cyber-gray rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-neon-green"
              initial={{ width: '0%' }}
              animate={{ width: '100%' }}
              transition={{ duration: 2, ease: 'easeInOut' }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  )
}
