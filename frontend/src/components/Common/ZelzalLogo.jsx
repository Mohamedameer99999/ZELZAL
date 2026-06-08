import { motion } from 'framer-motion'
import { FiShield } from 'react-icons/fi'

export default function ZelzalLogo({ size = 'md', showText = true, animate = true }) {
  const sizes = {
    sm: { icon: 20, text: 'text-lg', spacing: 'gap-1.5' },
    md: { icon: 28, text: 'text-2xl', spacing: 'gap-2' },
    lg: { icon: 36, text: 'text-3xl md:text-4xl', spacing: 'gap-3' },
    xl: { icon: 48, text: 'text-4xl md:text-6xl', spacing: 'gap-4' },
  }

  const s = sizes[size]

  const content = (
    <div className={`flex items-center ${s.spacing}`}>
      <div className="relative">
        <FiShield size={s.icon} className="text-neon-green" />
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={animate ? { opacity: [0, 1, 0], scale: [1, 1.5, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="w-1 h-1 bg-neon-green rounded-full shadow-neon-sm" />
        </motion.div>
      </div>
      {showText && (
        <span className={`font-cyber font-bold text-neon-green ${s.text} tracking-wider animate-glow`}>
          ZELZAL
        </span>
      )}
    </div>
  )

  if (!animate) return content

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      {content}
    </motion.div>
  )
}
