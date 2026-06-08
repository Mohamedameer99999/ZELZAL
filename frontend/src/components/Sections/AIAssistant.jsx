import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiCpu, FiSend, FiTrash2, FiClock, FiMessageSquare, FiZap,
  FiShield, FiBarChart2, FiFolder, FiAlertCircle,
} from 'react-icons/fi'
import GlassCard from '../Common/GlassCard'
import NeonText from '../Common/NeonText'
import { aiAPI } from '../../api'

const quickActions = [
  { label: 'Security Audit', icon: FiShield, prompt: 'Run a full security audit of my system' },
  { label: 'Performance Check', icon: FiBarChart2, prompt: 'Check system performance metrics' },
  { label: 'Threat Analysis', icon: FiAlertCircle, prompt: 'Analyze recent threat patterns' },
  { label: 'Project Status', icon: FiFolder, prompt: 'Give me a summary of my projects' },
]

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to ZELZAL AI Security Assistant. I am monitoring your systems 24/7. How can I help secure your infrastructure today?', timestamp: new Date().toISOString() },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [conversations, setConversations] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    aiAPI.conversations().then(({ data }) => setConversations(data.conversations)).catch(() => {})
    aiAPI.recommendations().then(({ data }) => {}).catch(() => {})
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMsg, timestamp: new Date().toISOString() }])
    setLoading(true)
    try {
      const { data } = await aiAPI.chat(userMsg, conversationId)
      setConversationId(data.conversation_id)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response, timestamp: new Date().toISOString() }])
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Connection error. AI systems temporarily unavailable.', timestamp: new Date().toISOString() }])
    } finally {
      setLoading(false)
    }
  }

  const handleQuickAction = async (prompt) => {
    setInput(prompt)
  }

  const handleNewChat = () => {
    setMessages([{ role: 'assistant', content: 'Welcome to ZELZAL AI Security Assistant. I am monitoring your systems 24/7. How can I help secure your infrastructure today?', timestamp: new Date().toISOString() }])
    setConversationId(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <NeonText size="xl">AI SECURITY ASSISTANT</NeonText>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 px-3 py-2 text-xs font-mono text-gray-400 glass rounded-lg border border-cyber-border hover:text-neon-green transition-colors"
          >
            <FiClock size={14} />
            HISTORY
          </button>
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-2 text-xs font-mono text-neon-green glass rounded-lg border border-neon-green/20 hover:bg-neon-green/10 transition-colors"
          >
            <FiMessageSquare size={14} />
            NEW CHAT
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <GlassCard className="lg:col-span-3 flex flex-col" delay={0.2}>
          <div className="flex-1 min-h-[400px] max-h-[500px] overflow-y-auto space-y-4 pr-2 mb-4">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-neon-dark flex items-center justify-center flex-shrink-0 border border-neon-green/30">
                      <FiCpu size={14} className="text-neon-green" />
                    </div>
                  )}
                  <div className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-neon-green/10 border border-neon-green/20'
                      : 'glass border border-cyber-border'
                  }`}>
                    <p className="text-sm text-gray-200 font-mono whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-[10px] text-gray-600 font-mono mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 border border-blue-500/30">
                      <span className="text-xs text-blue-500 font-mono">U</span>
                    </div>
                  )}
                </motion.div>
              ))}
              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-neon-dark flex items-center justify-center border border-neon-green/30">
                    <FiCpu size={14} className="text-neon-green" />
                  </div>
                  <div className="glass border border-cyber-border rounded-lg p-4">
                    <div className="flex gap-1">
                      {[...Array(3)].map((_, i) => (
                        <motion.span
                          key={i}
                          className="w-2 h-2 bg-neon-green rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your security query..."
              className="flex-1 cyber-input rounded-lg px-4 py-3 text-sm"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="cyber-btn px-4 rounded-lg disabled:opacity-50"
            >
              <FiSend size={18} />
            </button>
          </div>
        </GlassCard>

        <div className="space-y-4">
          <GlassCard delay={0.3}>
            <div className="flex items-center gap-2 mb-4">
              <FiZap className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">QUICK ACTIONS</h3>
            </div>
            <div className="space-y-2">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.prompt)}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-xs font-mono text-gray-400 glass rounded-lg border border-cyber-border hover:border-neon-green/30 hover:text-neon-green transition-all"
                >
                  <action.icon size={14} />
                  {action.label}
                </button>
              ))}
            </div>
          </GlassCard>

          <GlassCard delay={0.4}>
            <div className="flex items-center gap-2 mb-4">
              <FiClock className="text-neon-green" />
              <h3 className="text-sm font-mono text-neon-green tracking-wider">SMART RECOMMENDATIONS</h3>
            </div>
            <div className="space-y-2">
              {[
                { title: 'Enable 2FA', priority: 'high' },
                { title: 'Review Active Sessions', priority: 'high' },
                { title: 'Update Firewall Rules', priority: 'medium' },
                { title: 'Run Weekly Scan', priority: 'medium' },
              ].map((rec) => (
                <div key={rec.title} className="flex items-center gap-2 p-2 rounded-lg hover:bg-cyber-gray/50 transition-colors">
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    rec.priority === 'high' ? 'bg-red-500' : 'bg-yellow-500'
                  }`} />
                  <span className="text-xs font-mono text-gray-400">{rec.title}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
