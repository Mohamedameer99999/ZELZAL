import { motion } from 'framer-motion'

export default function NeonText({ children, as: Tag = 'span', className = '', size = 'lg', animate = true }) {
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-2xl md:text-3xl',
    xl: 'text-3xl md:text-5xl',
    xxl: 'text-4xl md:text-7xl',
  }

  const base = `font-cyber font-bold text-neon-green ${sizeClasses[size]} ${className}`

  if (!animate) return <Tag className={base}>{children}</Tag>

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <Tag className={`${base} animate-glow`}>
        {children}
      </Tag>
    </motion.div>
  )
}
