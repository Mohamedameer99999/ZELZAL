import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiFolder, FiPlus, FiMoreVertical, FiClock, FiCheckCircle,
  FiAlertCircle, FiTrendingUp, FiTrash2, FiEdit2,
} from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'

const initialProjects = [
  {
    id: 1, name: 'Firewall Configuration', description: 'Configure and deploy new firewall rules across all network segments',
    status: 'active', progress: 75, priority: 'high', tasks: [
      { id: 1, title: 'Define rule sets', status: 'done' },
      { id: 2, title: 'Test rule conflicts', status: 'done' },
      { id: 3, title: 'Deploy to production', status: 'in_progress' },
      { id: 4, title: 'Verify deployment', status: 'todo' },
    ], dueDate: '2026-06-20',
  },
  {
    id: 2, name: 'Penetration Testing', description: 'Comprehensive security assessment of internal systems',
    status: 'active', progress: 45, priority: 'high', tasks: [
      { id: 5, title: 'Reconnaissance phase', status: 'done' },
      { id: 6, title: 'Vulnerability scanning', status: 'in_progress' },
      { id: 7, title: 'Exploitation testing', status: 'todo' },
      { id: 8, title: 'Report generation', status: 'todo' },
    ], dueDate: '2026-07-05',
  },
  {
    id: 3, name: 'Security Audit Q2', description: 'Quarterly security audit and compliance check',
    status: 'active', progress: 20, priority: 'medium', tasks: [
      { id: 9, title: 'Gather access logs', status: 'done' },
      { id: 10, title: 'Review permissions', status: 'todo' },
      { id: 11, title: 'Check compliance', status: 'todo' },
    ], dueDate: '2026-06-30',
  },
  {
    id: 4, name: 'Incident Response Plan', description: 'Develop and document incident response procedures',
    status: 'planning', progress: 10, priority: 'medium', tasks: [
      { id: 12, title: 'Draft procedures', status: 'in_progress' },
      { id: 13, title: 'Review with team', status: 'todo' },
    ], dueDate: '2026-07-15',
  },
  {
    id: 5, name: 'Network Monitoring Setup', description: 'Deploy network monitoring across all critical infrastructure',
    status: 'planning', progress: 0, priority: 'low', tasks: [
      { id: 14, title: 'Select monitoring tools', status: 'todo' },
    ], dueDate: '2026-08-01',
  },
]

export default function ProjectsManager() {
  const [projects, setProjects] = useState(initialProjects)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showNew, setShowNew] = useState(false)
  const [newProject, setNewProject] = useState({ name: '', description: '', priority: 'medium' })

  const handleCreateProject = () => {
    if (!newProject.name.trim()) return
    const project = {
      id: Date.now(),
      ...newProject,
      status: 'planning',
      progress: 0,
      tasks: [],
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    }
    setProjects([project, ...projects])
    setShowNew(false)
    setNewProject({ name: '', description: '', priority: 'medium' })
  }

  const handleDeleteProject = (id) => {
    setProjects(projects.filter((p) => p.id !== id))
    if (selectedProject?.id === id) setSelectedProject(null)
  }

  const handleToggleTask = (projectId, taskId) => {
    setProjects(projects.map((p) => {
      if (p.id !== projectId) return p
      const tasks = p.tasks.map((t) => {
        if (t.id !== taskId) return t
        const newStatus = t.status === 'done' ? 'todo' : t.status === 'in_progress' ? 'done' : 'in_progress'
        return { ...t, status: newStatus }
      })
      const done = tasks.filter((t) => t.status === 'done').length
      const progress = Math.round((done / tasks.length) * 100)
      return { ...p, tasks, progress }
    }))
  }

  const getPriorityColor = (p) => {
    if (p === 'high') return 'text-red-500 border-red-500/30 bg-red-500/10'
    if (p === 'medium') return 'text-yellow-500 border-yellow-500/30 bg-yellow-500/10'
    return 'text-blue-500 border-blue-500/30 bg-blue-500/10'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <NeonText size="xl">PROJECTS</NeonText>
        <button
          onClick={() => setShowNew(!showNew)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-mono cyber-btn rounded-lg"
        >
          <FiPlus size={16} />
          NEW PROJECT
        </button>
      </div>

      <AnimatePresence>
        {showNew && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-xl p-6 border border-neon-green/20"
          >
            <h3 className="text-sm font-mono text-neon-green mb-4">CREATE NEW PROJECT</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="Project name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                className="cyber-input rounded-lg px-4 py-2.5 text-sm"
              />
              <input
                type="text"
                placeholder="Description"
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                className="cyber-input rounded-lg px-4 py-2.5 text-sm"
              />
              <div className="flex gap-2">
                <select
                  value={newProject.priority}
                  onChange={(e) => setNewProject({ ...newProject, priority: e.target.value })}
                  className="cyber-input rounded-lg px-4 py-2.5 text-sm flex-1"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <button onClick={handleCreateProject} className="cyber-btn px-6 rounded-lg text-sm font-mono">
                  CREATE
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {projects.map((project, i) => (
            <GlassCard key={project.id} delay={i * 0.05}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <FiFolder className="text-neon-green" size={18} />
                    <h3 className="text-sm font-mono text-gray-200">{project.name}</h3>
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${getPriorityColor(project.priority)}`}>
                      {project.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 font-mono mt-1">{project.description}</p>

                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex-1">
                      <div className="flex justify-between text-[10px] font-mono mb-1">
                        <span className="text-gray-500">Progress</span>
                        <span className="text-neon-green">{project.progress}%</span>
                      </div>
                      <div className="h-1.5 bg-cyber-dark rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${project.progress}%` }}
                          transition={{ duration: 0.8 }}
                          className="h-full bg-gradient-to-r from-neon-dark to-neon-green rounded-full"
                        />
                      </div>
                    </div>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      project.status === 'active' ? 'bg-neon-green/10 text-neon-green' : 'bg-blue-500/10 text-blue-500'
                    }`}>
                      {project.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 mt-2 text-[10px] font-mono text-gray-600">
                    <span className="flex items-center gap-1">
                      <FiCheckCircle size={10} className="text-neon-green" />
                      {project.tasks.filter((t) => t.status === 'done').length}/{project.tasks.length} tasks
                    </span>
                    <span className="flex items-center gap-1">
                      <FiClock size={10} />
                      Due: {project.dueDate}
                    </span>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {project.tasks.map((task) => (
                      <button
                        key={task.id}
                        onClick={() => handleToggleTask(project.id, task.id)}
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full border transition-colors ${
                          task.status === 'done'
                            ? 'bg-neon-green/10 border-neon-green/30 text-neon-green line-through'
                            : task.status === 'in_progress'
                            ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500'
                            : 'bg-cyber-gray border-cyber-border text-gray-500 hover:border-neon-green/30'
                        }`}
                      >
                        {task.title}
                      </button>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteProject(project.id)}
                  className="text-gray-600 hover:text-red-500 transition-colors ml-2"
                >
                  <FiTrash2 size={14} />
                </button>
              </div>
            </GlassCard>
          ))}
        </div>

        <div className="space-y-4">
          <GlassCard delay={0.3}>
            <div className="flex items-center gap-2 mb-4">
              <FiTrendingUp className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">OVERVIEW</h3>
            </div>
            {[
              { label: 'Total Projects', value: projects.length },
              { label: 'Active', value: projects.filter((p) => p.status === 'active').length },
              { label: 'Completed Tasks', value: projects.reduce((a, p) => a + p.tasks.filter((t) => t.status === 'done').length, 0) },
              { label: 'Pending Tasks', value: projects.reduce((a, p) => a + p.tasks.filter((t) => t.status === 'todo').length, 0) },
            ].map((item) => (
              <div key={item.label} className="flex justify-between items-center py-2 border-b border-cyber-border last:border-0">
                <span className="text-xs font-mono text-gray-500">{item.label}</span>
                <span className="text-sm font-mono text-neon-green">{item.value}</span>
              </div>
            ))}
          </GlassCard>

          <GlassCard delay={0.4}>
            <div className="flex items-center gap-2 mb-4">
              <FiAlertCircle className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">UPCOMING DEADLINES</h3>
            </div>
            {projects
              .filter((p) => p.status !== 'completed')
              .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
              .slice(0, 3)
              .map((p) => (
                <div key={p.id} className="flex items-center gap-2 py-2 border-b border-cyber-border last:border-0">
                  <FiClock size={12} className="text-yellow-500" />
                  <span className="text-xs font-mono text-gray-400">{p.name}</span>
                  <span className="text-xs font-mono text-gray-600 ml-auto">{p.dueDate}</span>
                </div>
              ))}
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
