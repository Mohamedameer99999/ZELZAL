import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  FiShield, FiAlertTriangle, FiCheckCircle, FiActivity, FiGlobe,
  FiTrendingUp, FiDownload, FiFilter, FiMoreVertical,
} from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'
import { securityAPI } from '../../api'

const recentEvents = [
  { type: 'Brute Force Attack', severity: 'critical', ip: '192.168.1.105', status: 'active', time: '2 min ago', desc: 'Multiple failed SSH attempts detected' },
  { type: 'Malware Detected', severity: 'high', ip: '10.0.0.45', status: 'active', time: '15 min ago', desc: 'Suspicious file hash matched known malware' },
  { type: 'Unauthorized Access', severity: 'critical', ip: '203.0.113.50', status: 'active', time: '1 hour ago', desc: 'Attempted admin panel access without credentials' },
  { type: 'Port Scan', severity: 'medium', ip: '198.51.100.22', status: 'resolved', time: '3 hours ago', desc: 'Sequential port scan detected from external IP' },
  { type: 'DNS Spoofing', severity: 'high', ip: '192.0.2.77', status: 'resolved', time: '5 hours ago', desc: 'DNS cache poisoning attempt blocked' },
  { type: 'SQL Injection', severity: 'medium', ip: '203.0.113.88', status: 'resolved', time: '8 hours ago', desc: 'SQL injection attempt on login endpoint' },
]

const severities = [
  { label: 'CRITICAL', count: 2, color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/30' },
  { label: 'HIGH', count: 4, color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/30' },
  { label: 'MEDIUM', count: 7, color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
  { label: 'LOW', count: 12, color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
]

const threatTypes = [
  { label: 'Brute Force', value: 35, color: 'bg-red-500' },
  { label: 'Malware', value: 25, color: 'bg-orange-500' },
  { label: 'Phishing', value: 20, color: 'bg-yellow-500' },
  { label: 'DDoS', value: 12, color: 'bg-purple-500' },
  { label: 'Injection', value: 8, color: 'bg-blue-500' },
]

export default function SecurityCenter() {
  const [filter, setFilter] = useState('all')
  const [events, setEvents] = useState(recentEvents)

  const filtered = filter === 'all' ? events : events.filter(e => e.severity === filter)

  return (
    <div className="space-y-6">
      <NeonText size="xl">SECURITY CENTER</NeonText>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {severities.map((sev, i) => (
          <GlassCard key={sev.label} delay={i * 0.1}>
            <div className={`flex items-center justify-between ${sev.color}`}>
              <span className="text-xs font-mono tracking-wider">{sev.label}</span>
              <FiShield size={16} />
            </div>
            <p className={`text-2xl md:text-3xl font-bold font-cyber mt-2 ${sev.color}`}>{sev.count}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2" delay={0.4}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FiActivity className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">SECURITY EVENTS</h3>
            </div>
            <div className="flex gap-1">
              {['all', 'critical', 'high', 'medium', 'low'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-2 py-1 text-xs font-mono rounded transition-colors ${
                    filter === f ? 'bg-neon-green text-cyber-black' : 'text-gray-500 hover:text-neon-green'
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {filtered.map((event, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                  event.severity === 'critical'
                    ? 'bg-red-500/5 border-red-500/20'
                    : event.severity === 'high'
                    ? 'bg-orange-500/5 border-orange-500/20'
                    : 'bg-cyber-gray/30 border-transparent'
                } hover:bg-cyber-gray/50`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  event.status === 'active' ? 'bg-red-500/20' : 'bg-neon-dark'
                }`}>
                  {event.status === 'active'
                    ? <FiAlertTriangle size={14} className="text-red-500" />
                    : <FiCheckCircle size={14} className="text-neon-green" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-gray-200 font-mono">{event.type}</p>
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      event.severity === 'critical' ? 'bg-red-500/20 text-red-500' :
                      event.severity === 'high' ? 'bg-orange-500/20 text-orange-500' :
                      event.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                      'bg-blue-500/20 text-blue-500'
                    }`}>
                      {event.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{event.desc}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-[11px] text-gray-600 font-mono">IP: {event.ip}</span>
                    <span className="text-[11px] text-gray-600 font-mono">{event.time}</span>
                  </div>
                </div>
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  event.status === 'active' ? 'bg-red-500/10 text-red-500' : 'bg-neon-dark text-neon-green'
                }`}>
                  {event.status.toUpperCase()}
                </span>
              </motion.div>
            ))}
          </div>
        </GlassCard>

        <GlassCard delay={0.5}>
          <div className="flex items-center gap-2 mb-4">
            <FiGlobe className="text-neon-green" />
            <h3 className="text-sm font-mono text-neon-green tracking-wider">THREAT DISTRIBUTION</h3>
          </div>

          <div className="space-y-4">
            {threatTypes.map((t) => (
              <div key={t.label}>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-gray-400">{t.label}</span>
                  <span className="text-gray-300">{t.value}%</span>
                </div>
                <div className="h-2 bg-cyber-dark rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${t.value}%` }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className={`h-full rounded-full ${t.color}`}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 space-y-3">
            <h4 className="text-xs font-mono text-gray-500 tracking-wider">QUICK ACTIONS</h4>
            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs font-mono text-neon-green glass rounded-lg border border-neon-green/20 hover:bg-neon-green/10 transition-colors">
              <FiDownload size={14} />
              EXPORT SECURITY REPORT
            </button>
            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs font-mono text-neon-green glass rounded-lg border border-neon-green/20 hover:bg-neon-green/10 transition-colors">
              <FiTrendingUp size={14} />
              RUN FULL SCAN
            </button>
          </div>

          <div className="mt-4 p-4 glass rounded-lg border border-neon-green/10">
            <p className="text-xs font-mono text-gray-500">SECURITY SCORE</p>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="text-3xl font-bold font-cyber text-neon-green">85</span>
              <span className="text-sm text-gray-500">/100</span>
            </div>
            <div className="mt-2 h-1.5 bg-cyber-dark rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: '85%' }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-neon-green rounded-full"
              />
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
