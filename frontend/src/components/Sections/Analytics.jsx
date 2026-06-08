import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  FiBarChart2, FiTrendingUp, FiActivity, FiClock, FiServer,
  FiDownload, FiCalendar,
} from 'react-icons/fi'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'

const dailyData = [
  { day: 'Mon', events: 45, threats: 12, users: 120 },
  { day: 'Tue', events: 52, threats: 18, users: 145 },
  { day: 'Wed', events: 38, threats: 8, users: 132 },
  { day: 'Thu', events: 65, threats: 22, users: 158 },
  { day: 'Fri', events: 48, threats: 15, users: 140 },
  { day: 'Sat', events: 25, threats: 5, users: 98 },
  { day: 'Sun', events: 20, threats: 3, users: 85 },
]

const threatDistribution = [
  { name: 'Brute Force', value: 35, color: '#ff4444' },
  { name: 'Malware', value: 25, color: '#ff8800' },
  { name: 'Phishing', value: 20, color: '#ffcc00' },
  { name: 'DDoS', value: 12, color: '#aa66ff' },
  { name: 'Other', value: 8, color: '#00ccff' },
]

const performanceData = [
  { time: '00:00', cpu: 23, memory: 45, network: 12 },
  { time: '04:00', cpu: 18, memory: 40, network: 8 },
  { time: '08:00', cpu: 45, memory: 62, network: 35 },
  { time: '12:00', cpu: 62, memory: 75, network: 55 },
  { time: '16:00', cpu: 55, memory: 68, network: 48 },
  { time: '20:00', cpu: 35, memory: 50, network: 25 },
]

const metrics = [
  { label: 'TOTAL EVENTS', value: '2,847', change: '+12.5%', positive: true },
  { label: 'THREATS BLOCKED', value: '1,234', change: '+8.3%', positive: true },
  { label: 'ACTIVE USERS', value: '892', change: '+5.1%', positive: true },
  { label: 'RESPONSE TIME', value: '234ms', change: '-3.2%', positive: false },
  { label: 'UPTIME', value: '99.97%', change: '+0.02%', positive: true },
  { label: 'ERROR RATE', value: '0.02%', change: '-0.01%', positive: true },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass rounded-lg p-3 border border-neon-green/30 text-xs font-mono">
        <p className="text-gray-400 mb-1">{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
        ))}
      </div>
    )
  }
  return null
}

export default function Analytics() {
  const [period, setPeriod] = useState('7d')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <NeonText size="xl">ANALYTICS</NeonText>
        <div className="flex items-center gap-2">
          {['7d', '30d', '90d'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-colors ${
                period === p ? 'bg-neon-green text-cyber-black' : 'text-gray-500 glass hover:text-neon-green'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {metrics.map((m, i) => (
          <GlassCard key={m.label} delay={i * 0.05}>
            <p className="text-[10px] font-mono text-gray-500 tracking-wider">{m.label}</p>
            <p className="text-lg md:text-xl font-bold font-cyber text-neon-green mt-1">{m.value}</p>
            <span className={`text-[10px] font-mono ${m.positive ? 'text-neon-green' : 'text-red-500'}`}>
              {m.change}
            </span>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard delay={0.3}>
          <div className="flex items-center gap-2 mb-4">
            <FiTrendingUp className="text-neon-green" />
            <h3 className="text-sm font-mono text-neon-green tracking-wider">EVENTS OVERVIEW</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={dailyData}>
              <defs>
                <linearGradient id="eventGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00ff41" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00ff41" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="threatGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ff4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="day" stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <YAxis stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="events" stroke="#00ff41" fill="url(#eventGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="threats" stroke="#ff4444" fill="url(#threatGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard delay={0.35}>
          <div className="flex items-center gap-2 mb-4">
            <FiActivity className="text-neon-green" />
            <h3 className="text-sm font-mono text-neon-green tracking-wider">THREAT DISTRIBUTION</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={threatDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
              >
                {threatDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {threatDistribution.map((t) => (
              <div key={t.name} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: t.color }} />
                <span className="text-[10px] font-mono text-gray-500">{t.name}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard delay={0.4}>
          <div className="flex items-center gap-2 mb-4">
            <FiServer className="text-neon-green" />
            <h3 className="text-sm font-mono text-neon-green tracking-wider">SYSTEM PERFORMANCE</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="time" stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <YAxis stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="cpu" stroke="#00ff41" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory" stroke="#ff8800" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="network" stroke="#00ccff" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {[{ label: 'CPU', color: '#00ff41' }, { label: 'Memory', color: '#ff8800' }, { label: 'Network', color: '#00ccff' }].map((l) => (
              <div key={l.label} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: l.color }} />
                <span className="text-[10px] font-mono text-gray-500">{l.label}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard delay={0.45}>
          <div className="flex items-center gap-2 mb-4">
            <FiBarChart2 className="text-neon-green" />
            <h3 className="text-sm font-mono text-neon-green tracking-wider">USER ACTIVITY</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="day" stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <YAxis stroke="#30363d" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="users" fill="#00ff41" radius={[4, 4, 0, 0]} opacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>
    </div>
  )
}
