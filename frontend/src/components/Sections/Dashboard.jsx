import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  FiUsers, FiShield, FiFolder, FiActivity, FiAlertTriangle, FiCheckCircle,
  FiClock, FiServer,
} from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'
import { useLanguage } from '../../hooks/useLanguage'
import { translations } from '../../i18n/translations'
import { dashboardAPI } from '../../api'

const activityIcons = {
  security: <FiShield size={14} className="text-red-500" />,
  project: <FiFolder size={14} className="text-purple-500" />,
  user: <FiUsers size={14} className="text-blue-500" />,
  ai: <FiActivity size={14} className="text-neon-green" />,
  system: <FiActivity size={14} className="text-neon-green" />,
}

export default function Dashboard() {
  const { lang } = useLanguage()
  const t = translations[lang]
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await dashboardAPI.stats()
        setStats(data)
      } catch {
        setStats({
          total_users: 1284, active_projects: 47, security_events: 23,
          task_completion_rate: 78.5, total_tasks: 342, completed_tasks: 268,
          critical_events: 3, today_activities: 156, active_users: 892,
        })
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const statCards = [
    { key: 'total_users', label: t.total_users, icon: FiUsers, color: 'text-blue-500' },
    { key: 'active_projects', label: t.active_projects, icon: FiFolder, color: 'text-purple-500' },
    { key: 'security_events', label: t.security_events, icon: FiShield, color: 'text-red-500' },
    { key: 'task_completion_rate', label: t.completion_rate, icon: FiCheckCircle, color: 'text-neon-green', suffix: '%' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <NeonText size="xl">{t.dashboard.toUpperCase()}</NeonText>
        <motion.span
          className="flex items-center gap-2 px-3 py-1.5 glass rounded-full text-xs text-neon-green border border-neon-green/20"
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <FiServer size={12} />
          LIVE
        </motion.span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <GlassCard key={card.key} delay={i * 0.1} glow>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-gray-500 mb-1 tracking-wider">{card.label}</p>
                {loading ? (
                  <div className="h-8 w-20 bg-cyber-gray rounded animate-pulse" />
                ) : (
                  <p className={`text-2xl md:text-3xl font-bold font-cyber ${card.color}`}>
                    {stats ? stats[card.key] || 0 : 0}{card.suffix || ''}
                  </p>
                )}
              </div>
              <card.icon size={24} className={`${card.color} opacity-50`} />
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2" delay={0.4}>
          <div className="flex items-center gap-2 mb-4">
            <FiActivity className="text-neon-green" />
            <h3 className="text-sm text-neon-green tracking-wider">{t.activity_timeline.toUpperCase()}</h3>
          </div>
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: lang === 'ar' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-cyber-gray/50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-neon-dark flex items-center justify-center flex-shrink-0">
                  {activityIcons[['security', 'user', 'project', 'security', 'ai', 'system', 'security', 'system'][i]]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200">{['System scan completed', 'New user registered', 'Project updated', 'Security alert resolved', 'AI analysis complete', 'Backup completed', 'Threat intelligence update', 'Performance optimization'][i]}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{[...Array(8)].map((_, j) => `${j * 5 + 2} min ago`)[i]}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </GlassCard>

        <GlassCard delay={0.5}>
          <div className="flex items-center gap-2 mb-4">
            <FiClock className="text-neon-green" />
            <h3 className="text-sm text-neon-green tracking-wider">{t.system_health.toUpperCase()}</h3>
          </div>
          <div className="space-y-4">
            {[
              { label: t.cpu, value: 45, color: 'bg-neon-green' },
              { label: t.memory, value: 62, color: 'bg-blue-500' },
              { label: t.storage, value: 34, color: 'bg-purple-500' },
              { label: t.network, value: 28, color: 'bg-yellow-500' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">{item.label}</span>
                  <span className="text-gray-300">{item.value}%</span>
                </div>
                <div className="h-2 bg-cyber-dark rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.value}%` }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className={`h-full rounded-full ${item.color}`}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 glass rounded-lg border border-neon-green/10">
            <div className="flex items-center gap-2 mb-2">
              <FiAlertTriangle size={14} className="text-yellow-500" />
              <span className="text-xs text-yellow-500">{t.active_threats.toUpperCase()}</span>
            </div>
            <p className="text-2xl font-bold font-cyber text-red-500">3</p>
            <p className="text-xs text-gray-500 mt-1">2 critical, 1 high priority</p>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
