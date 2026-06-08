import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiUsers, FiUser, FiShield, FiTrash2, FiEdit2, FiStar,
  FiShieldOff, FiMail, FiCalendar,
} from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'
import { useAuth } from '../../hooks/useAuth'

const roles = [
  { label: 'Admin', value: 'admin', color: 'text-red-500', bg: 'bg-red-500/10' },
  { label: 'User', value: 'user', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { label: 'Viewer', value: 'viewer', color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  { label: 'Analyst', value: 'analyst', color: 'text-purple-500', bg: 'bg-purple-500/10' },
]

const initialUsers = [
  { id: 1, username: 'admin', email: 'admin@zelzal.io', role: 'admin', status: 'active', created: '2026-01-15', bio: 'System administrator' },
  { id: 2, username: 'cyber_agent', email: 'agent@zelzal.io', role: 'analyst', status: 'active', created: '2026-02-20', bio: 'Security analyst' },
  { id: 3, username: 'netwatch', email: 'watch@zelzal.io', role: 'user', status: 'active', created: '2026-03-10', bio: 'Network engineer' },
  { id: 4, username: 'shadowsilk', email: 'shadow@zelzal.io', role: 'viewer', status: 'inactive', created: '2026-04-05', bio: 'External auditor' },
  { id: 5, username: 'firewall_fox', email: 'fox@zelzal.io', role: 'user', status: 'active', created: '2026-05-01', bio: 'Security researcher' },
]

export default function UserManagement() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState(initialUsers)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({ username: '', email: '', bio: '' })
  const [showProfile, setShowProfile] = useState(false)

  const isAdmin = currentUser?.role === 'admin'

  const handleRoleChange = (userId, newRole) => {
    setUsers(users.map((u) => (u.id === userId ? { ...u, role: newRole } : u)))
  }

  const handleDeleteUser = (userId) => {
    setUsers(users.filter((u) => u.id !== userId))
  }

  const handleEdit = (u) => {
    setEditingId(u.id)
    setEditForm({ username: u.username, email: u.email, bio: u.bio })
  }

  const handleSave = (userId) => {
    setUsers(users.map((u) => (u.id === userId ? { ...u, ...editForm } : u)))
    setEditingId(null)
  }

  const getRoleStyle = (role) => {
    const r = roles.find((r) => r.value === role)
    return r ? `${r.color} ${r.bg}` : 'text-gray-500'
  }

  return (
    <div className="space-y-6">
      <NeonText size="xl">USER MANAGEMENT</NeonText>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {users.map((u, i) => (
            <GlassCard key={u.id} delay={i * 0.05}>
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 ${
                  u.role === 'admin' ? 'border-red-500/50 bg-red-500/10' : 'border-cyber-border bg-cyber-gray'
                }`}>
                  {u.role === 'admin' ? (
                    <FiShield size={20} className="text-red-500" />
                  ) : (
                    <FiUser size={20} className="text-neon-green" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  {editingId === u.id ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={editForm.username}
                        onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                        className="cyber-input rounded px-3 py-1.5 text-sm w-full"
                      />
                      <input
                        type="email"
                        value={editForm.email}
                        onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                        className="cyber-input rounded px-3 py-1.5 text-sm w-full"
                      />
                      <input
                        type="text"
                        value={editForm.bio}
                        onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                        className="cyber-input rounded px-3 py-1.5 text-sm w-full"
                      />
                      <div className="flex gap-2">
                        <button onClick={() => handleSave(u.id)} className="cyber-btn px-3 py-1 text-xs rounded">
                          SAVE
                        </button>
                        <button onClick={() => setEditingId(null)} className="text-xs text-gray-500 hover:text-white px-3 py-1">
                          CANCEL
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-mono text-gray-200">{u.username}</h3>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${getRoleStyle(u.role)}`}>
                          {u.role.toUpperCase()}
                        </span>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                          u.status === 'active' ? 'bg-neon-green/10 text-neon-green' : 'bg-gray-500/10 text-gray-500'
                        }`}>
                          {u.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 font-mono mt-0.5">{u.email}</p>
                      {u.bio && <p className="text-xs text-gray-600 font-mono mt-1">{u.bio}</p>}
                      <div className="flex items-center gap-3 mt-2 text-[10px] font-mono text-gray-600">
                        <FiCalendar size={10} />
                        Joined {u.created}
                      </div>
                    </>
                  )}
                </div>

                {isAdmin && editingId !== u.id && (
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleEdit(u)}
                      className="p-2 text-gray-500 hover:text-neon-green transition-colors"
                    >
                      <FiEdit2 size={14} />
                    </button>
                    <div className="relative group">
                      <button className="p-2 text-gray-500 hover:text-neon-green transition-colors">
                        <FiShieldOff size={14} />
                      </button>
                      <div className="absolute right-0 top-full mt-1 glass rounded-lg border border-cyber-border p-1 hidden group-hover:block z-10 min-w-[120px]">
                        {roles.map((r) => (
                          <button
                            key={r.value}
                            onClick={() => handleRoleChange(u.id, r.value)}
                            className={`w-full text-left px-3 py-1.5 text-xs font-mono rounded ${getRoleStyle(r.value)} hover:bg-cyber-gray transition-colors`}
                          >
                            {r.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    {u.id !== currentUser?.id && (
                      <button
                        onClick={() => handleDeleteUser(u.id)}
                        className="p-2 text-gray-500 hover:text-red-500 transition-colors"
                      >
                        <FiTrash2 size={14} />
                      </button>
                    )}
                  </div>
                )}
              </div>
            </GlassCard>
          ))}
        </div>

        <div className="space-y-4">
          <GlassCard delay={0.3}>
            <div className="flex items-center gap-2 mb-4">
              <FiStar className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">ROLES</h3>
            </div>
            {roles.map((r) => (
              <div key={r.value} className="flex items-center justify-between py-2 border-b border-cyber-border last:border-0">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${r.bg}`} style={{ backgroundColor: r.color.replace('text-', '') }} />
                  <span className="text-xs font-mono text-gray-400">{r.label}</span>
                </div>
                <span className="text-xs font-mono text-gray-500">
                  {users.filter((u) => u.role === r.value).length}
                </span>
              </div>
            ))}
          </GlassCard>

          <GlassCard delay={0.35}>
            <div className="flex items-center gap-2 mb-4">
              <FiUsers className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">STATISTICS</h3>
            </div>
            {[
              { label: 'Total Users', value: users.length },
              { label: 'Active', value: users.filter((u) => u.status === 'active').length },
              { label: 'Inactive', value: users.filter((u) => u.status === 'inactive').length },
              { label: 'Admins', value: users.filter((u) => u.role === 'admin').length },
            ].map((s) => (
              <div key={s.label} className="flex justify-between py-2 border-b border-cyber-border last:border-0">
                <span className="text-xs font-mono text-gray-500">{s.label}</span>
                <span className="text-sm font-mono text-neon-green">{s.value}</span>
              </div>
            ))}
            {!isAdmin && (
              <div className="mt-4 p-3 glass rounded-lg border border-yellow-500/20">
                <p className="text-[10px] font-mono text-yellow-500 text-center">
                  Admin access required for user management
                </p>
              </div>
            )}
          </GlassCard>

          <GlassCard delay={0.4}>
            <div className="flex items-center gap-2 mb-4">
              <FiMail className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">PROFILE</h3>
            </div>
            {currentUser && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <FiUser size={14} className="text-gray-500" />
                  <span className="text-xs font-mono text-gray-300">{currentUser.username}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiMail size={14} className="text-gray-500" />
                  <span className="text-xs font-mono text-gray-300">{currentUser.email}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiShield size={14} className="text-gray-500" />
                  <span className="text-xs font-mono text-gray-300">{currentUser.role?.toUpperCase()}</span>
                </div>
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
