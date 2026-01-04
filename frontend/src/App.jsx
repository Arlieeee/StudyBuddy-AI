import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import './App.css'
import ImagePreviewModal from './ImagePreviewModal'

// API Base URL
const API_BASE = 'http://localhost:8001'

// Icons as SVG components
const Icons = {
  Upload: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  ),
  Send: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  ),
  File: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  ),
  Trash: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  ),
  Edit: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  ),
  Check: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ),
  Image: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </svg>
  ),
  Chat: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  Sparkles: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  ),
  ChevronLeft: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  ),
  ChevronRight: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  ),
  Menu: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  ),
}

// Loading Overlay Component with Animation
function LoadingOverlay({ message = '正在处理...' }) {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-animation">
          <div className="loading-book">📚</div>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        <p className="loading-message">{message}</p>
        <p className="loading-hint">AI正在分析您的文档内容...</p>
      </div>
    </div>
  )
}

// Toast Component
function Toast({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
    </div>
  )
}

// File Upload Component
function FileUpload({ onUpload, isUploading }) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => setIsDragging(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFiles = (files) => {
    files.forEach(file => {
      const ext = file.name.split('.').pop().toLowerCase()
      if (['pdf', 'pptx', 'docx', 'txt'].includes(ext)) {
        onUpload(file)
      }
    })
  }

  return (
    <div
      className={`upload-area ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <div className="upload-icon">📁</div>
      <p className="upload-text">
        {isUploading ? '正在上传...' : '拖拽文件到这里'}
      </p>
      <p className="upload-hint">PDF, PPTX, DOCX, TXT</p>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.pptx,.docx,.txt"
        multiple
        onChange={(e) => handleFiles(Array.from(e.target.files))}
        style={{ display: 'none' }}
      />
    </div>
  )
}

// Document List Component with Rename Feature
function DocumentList({ documents, displayNames, onDelete, onRename }) {
  const [editingId, setEditingId] = useState(null)
  const [editValue, setEditValue] = useState('')

  const getFileIcon = (type) => {
    const icons = { pdf: '📕', pptx: '📙', docx: '📘', txt: '📝' }
    return icons[type] || '📄'
  }

  const startEdit = (doc) => {
    setEditingId(doc.id)
    setEditValue(displayNames[doc.id] || doc.filename)
  }

  const saveEdit = (docId) => {
    if (editValue.trim()) {
      onRename(docId, editValue.trim())
    }
    setEditingId(null)
  }

  const handleKeyPress = (e, docId) => {
    if (e.key === 'Enter') {
      saveEdit(docId)
    } else if (e.key === 'Escape') {
      setEditingId(null)
    }
  }

  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📚</div>
        <p>还没有上传任何文档</p>
      </div>
    )
  }

  return (
    <div className="document-list">
      {documents.map((doc) => (
        <div key={doc.id} className="document-item">
          <div className="document-icon">{getFileIcon(doc.file_type)}</div>
          <div className="document-info">
            {editingId === doc.id ? (
              <input
                type="text"
                className="document-name-input"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyDown={(e) => handleKeyPress(e, doc.id)}
                onBlur={() => saveEdit(doc.id)}
                autoFocus
              />
            ) : (
              <div className="document-name" title={doc.filename}>
                {displayNames[doc.id] || doc.filename}
              </div>
            )}
            <div className="document-meta">
              {doc.chunk_count} 个片段 · {doc.file_type.toUpperCase()}
            </div>
          </div>
          <div className="document-actions">
            {editingId === doc.id ? (
              <button className="document-action-btn" onClick={() => saveEdit(doc.id)}>
                <Icons.Check />
              </button>
            ) : (
              <button className="document-action-btn" onClick={() => startEdit(doc)}>
                <Icons.Edit />
              </button>
            )}
            <button className="document-delete" onClick={() => onDelete(doc.id)}>
              <Icons.Trash />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

// Chat Message Component with Markdown, LaTeX, Image support and Quick Actions
function ChatMessage({ message, displayNames, onImageClick, onGenerateFromContent }) {
  const isUser = message.role === 'user'

  const getDisplayName = (source) => {
    return displayNames[source.document_id] || source.document_name
  }

  // 复制内容到剪贴板
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
  }

  // 根据此消息生成图解
  const handleGenerateImage = () => {
    if (onGenerateFromContent) {
      onGenerateFromContent(message.content)
    }
  }

  return (
    <div className={`message message-${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-text markdown-content">
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* 图像显示 - 作为消息的一部分 */}
        {message.imageBase64 && (
          <div
            className="message-image-card"
            onClick={() => onImageClick && onImageClick(message.imageBase64)}
          >
            <img
              src={`data:image/png;base64,${message.imageBase64}`}
              alt="知识图解"
            />
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <div className="source-title">📚 参考来源</div>
            {message.sources.map((source, idx) => (
              <div key={idx} className="source-item">
                <Icons.File />
                <span>{getDisplayName(source)}</span>
                <span className="badge">
                  {Math.min(100, Math.round(source.relevance_score * 100))}%
                </span>
              </div>
            ))}
          </div>
        )}

        {/* AI回复快捷按钮 */}
        {!isUser && (
          <div className="message-actions">
            <button
              className="message-action-btn"
              onClick={handleCopy}
              data-tooltip="复制回复内容"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
              </svg>
            </button>
            <button
              className="message-action-btn"
              onClick={handleGenerateImage}
              data-tooltip="根据此回复生成知识图解"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// Welcome Screen Component
function WelcomeScreen({ onSuggestionClick }) {
  const suggestions = [
    '这份文档的主要内容是什么？',
    '帮我总结一下关键知识点',
    '解释一下这个概念',
    '生成复习问题',
  ]

  return (
    <div className="welcome-screen">
      <div className="welcome-icon">🎓</div>
      <h2 className="welcome-title">欢迎使用 StudyBuddy AI</h2>
      <p className="welcome-desc">
        上传你的学习资料<br></br>让我帮助你理解内容、回答问题、生成知识图解
      </p>
      <div className="suggestions">
        {suggestions.map((s, i) => (
          <button
            key={i}
            className="suggestion-btn"
            onClick={() => onSuggestionClick(s)}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}

// Main App Component
function App() {
  // 移除activeTab，使用inputMode替代
  const [inputMode, setInputMode] = useState('chat') // 'chat' or 'image'
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [toasts, setToasts] = useState([])
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [displayNames, setDisplayNames] = useState({})
  // 新增：图像预览Modal状态
  const [previewImage, setPreviewImage] = useState(null)
  // 新增：图解类型
  const [imageStyle, setImageStyle] = useState('mindmap')
  // 新增：图像历史
  const [imageHistory, setImageHistory] = useState([])
  // 新增：推荐弹窗状态
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Load documents and display names on mount
  useEffect(() => {
    fetchDocuments()
    // Load display names from localStorage
    const savedNames = localStorage.getItem('studybuddy_display_names')
    if (savedNames) {
      setDisplayNames(JSON.parse(savedNames))
    }
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Save display names to localStorage when changed
  useEffect(() => {
    localStorage.setItem('studybuddy_display_names', JSON.stringify(displayNames))
  }, [displayNames])

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = inputRef.current
    if (!textarea) return

    // 创建一个隐藏的克隆元素来测量高度，避免抖动
    const clone = document.createElement('textarea')
    clone.style.cssText = window.getComputedStyle(textarea).cssText
    clone.style.height = 'auto'
    clone.style.position = 'absolute'
    clone.style.visibility = 'hidden'
    clone.style.pointerEvents = 'none'
    clone.value = textarea.value

    document.body.appendChild(clone)
    const newHeight = Math.min(Math.max(clone.scrollHeight, 52), 200)
    document.body.removeChild(clone)

    // 只在高度变化时更新
    const currentHeight = parseInt(textarea.style.height) || 52
    if (newHeight !== currentHeight) {
      textarea.style.height = newHeight + 'px'
    }
  }, [inputValue])

  const showToast = (message, type = 'success') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/upload/`)
      if (res.ok) {
        const data = await res.json()
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
  }

  const handleUpload = async (file) => {
    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/upload/`, {
        method: 'POST',
        body: formData,
      })

      if (res.ok) {
        const doc = await res.json()
        setDocuments(prev => [...prev, doc])
        // Set initial display name to original filename
        setDisplayNames(prev => ({
          ...prev,
          [doc.id]: file.name
        }))
        showToast(`文档 "${file.name}" 上传成功！`, 'success')
      } else {
        const error = await res.json()
        showToast(error.detail || '上传失败', 'error')
      }
    } catch (error) {
      showToast('上传失败，请检查网络连接', 'error')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDelete = async (docId) => {
    try {
      const res = await fetch(`${API_BASE}/upload/${docId}`, {
        method: 'DELETE',
      })

      if (res.ok) {
        setDocuments(prev => prev.filter(d => d.id !== docId))
        // Remove display name
        setDisplayNames(prev => {
          const newNames = { ...prev }
          delete newNames[docId]
          return newNames
        })
        showToast('文档已删除', 'success')
      }
    } catch (error) {
      showToast('删除失败', 'error')
    }
  }

  const handleRename = (docId, newName) => {
    setDisplayNames(prev => ({
      ...prev,
      [docId]: newName
    }))
    showToast('名称已更新', 'success')
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = { role: 'user', content: inputValue }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const res = await fetch(`${API_BASE}/qa/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: inputValue }),
      })

      if (res.ok) {
        const data = await res.json()
        const assistantMessage = {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        const error = await res.json()
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `抱歉，处理请求时出错：${error.detail || '未知错误'}`,
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '连接服务器失败，请检查后端是否启动',
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // 图像生成 - 将图像添加到消息中
  const handleGenerateImage = async (customPrompt = null) => {
    const prompt = customPrompt || inputValue
    if (!prompt.trim() || isLoading) return

    // 添加用户消息
    const userMessage = {
      role: 'user',
      content: inputMode === 'image' ? `🎨 生成图解：${prompt}` : prompt
    }
    setMessages(prev => [...prev, userMessage])
    if (!customPrompt) setInputValue('')
    setIsLoading(true)

    try {
      // 获取对话历史作为上下文
      const conversationHistory = messages
        .slice(-6)
        .map(m => `${m.role}: ${m.content}`)
        .join('\n')

      const res = await fetch(`${API_BASE}/generate/visualization`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          style: imageStyle,
          conversation_history: conversationHistory,
          aspect_ratio: '16:9',
        }),
      })

      if (res.ok) {
        const data = await res.json()
        // 将图像作为AI消息的一部分添加
        const assistantMessage = {
          role: 'assistant',
          content: data.description || `已为「${prompt}」生成知识图解`,
          imageBase64: data.image_base64,
        }
        setMessages(prev => [...prev, assistantMessage])
        // 保存到图像历史
        setImageHistory(prev => [...prev, {
          id: Date.now(),
          prompt: prompt,
          imageBase64: data.image_base64,
          createdAt: new Date().toISOString(),
        }])
        showToast('图像生成成功！', 'success')
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '抱歉，图像生成失败。请稍后重试。',
        }])
        showToast('图像生成失败', 'error')
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '连接服务器失败，请检查后端是否启动',
      }])
      showToast('连接服务器失败', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  // 根据当前模式处理提交
  const handleSubmit = () => {
    if (inputMode === 'chat') {
      handleSend()
    } else {
      handleGenerateImage()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // 获取智能推荐
  const handleShowRecommendations = async () => {
    // 如果没有文档，直接显示弹窗（会显示暂无推荐提示）
    if (documents.length === 0) {
      setRecommendations([])
      setShowRecommendations(true)
      return
    }

    setIsLoadingRecommendations(true)
    setShowRecommendations(true)

    try {
      const endpoint = inputMode === 'chat' ? '/recommendations/chat' : '/recommendations/visualization'
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_ids: documents.map(d => d.id),
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      })

      if (!response.ok) throw new Error('Failed to get recommendations')

      const data = await response.json()
      setRecommendations(data.topics || [])
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      setRecommendations([])
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  // 选择推荐主题
  const handleSelectRecommendation = (rec) => {
    setInputValue(rec.prompt)
    setShowRecommendations(false)
  }

  return (
    <div className="app">
      {/* Loading Overlay */}
      {isUploading && <LoadingOverlay message="正在处理文档..." />}

      {/* Image Preview Modal */}
      {previewImage && (
        <ImagePreviewModal
          imageBase64={previewImage}
          onClose={() => setPreviewImage(null)}
        />
      )}

      {/* Header - 移除Tab切换 */}
      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <button
              className="sidebar-toggle"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              title={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
            >
              {sidebarCollapsed ? <Icons.Menu /> : <Icons.ChevronLeft />}
            </button>
            <div className="logo-icon">🎓</div>
            <span className="logo-text">StudyBuddy AI</span>
          </div>
          {/* 模型徽章 */}
          <div className="nav">
            <span className="badge badge-success">Powered by Gemini 3.0</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container main-content">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-inner">
            <div className="sidebar-section">
              <h3 className="sidebar-title">📤 上传文档</h3>
              <FileUpload onUpload={handleUpload} isUploading={isUploading} />
            </div>
            <div className="sidebar-section">
              <h3 className="sidebar-title">📚 知识库 ({documents.length})</h3>
              <DocumentList
                documents={documents}
                displayNames={displayNames}
                onDelete={handleDelete}
                onRename={handleRename}
              />
            </div>
          </div>
        </aside>

        {/* 统一的对话面板 */}
        <div className={`chat-panel ${sidebarCollapsed ? 'expanded' : ''}`}>
          <div className="chat-container">
            <div className="chat-header">
              <h2 className="chat-title">💬 智能学习助手</h2>
              <span className="badge">{inputMode === 'chat' ? '对话模式' : '图解模式'}</span>
            </div>

            {/* 对话消息区域 */}
            <div className="chat-messages">
              {messages.length === 0 ? (
                <WelcomeScreen onSuggestionClick={(s) => setInputValue(s)} />
              ) : (
                messages.map((msg, idx) => (
                  <ChatMessage
                    key={idx}
                    message={msg}
                    displayNames={displayNames}
                    onImageClick={(img) => setPreviewImage(img)}
                    onGenerateFromContent={(content) => {
                      // 提取内容生成图解，避免token消耗过快，截断到2000字符
                      const summary = content.substring(0, 2000)
                      handleGenerateImage(`根据以下内容生成知识图解：${summary}`)
                    }}
                  />
                ))
              )}
              {isLoading && (
                <div className="message message-assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="spinner"></div>
                    <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)' }}>
                      {inputMode === 'image' ? '正在生成知识图解...' : '正在思考...'}
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区域 */}
            <div className="chat-input-container">
              {/* 模式切换按钮和类型选择 - 内联布局 */}
              <div className="input-mode-toggle">
                <button
                  className={`mode-btn ${inputMode === 'chat' ? 'active' : ''}`}
                  onClick={() => setInputMode('chat')}
                >
                  💬 对话
                </button>
                <button
                  className={`mode-btn ${inputMode === 'image' ? 'active' : ''}`}
                  onClick={() => setInputMode('image')}
                >
                  🎨 生成图解
                </button>
                {/* 图解模式下内联显示类型选择 */}
                {inputMode === 'image' && (
                  <>
                    <span className="mode-divider">|</span>
                    <div className="style-selector">
                      <button
                        className={`style-btn ${imageStyle === 'mindmap' ? 'active' : ''}`}
                        onClick={() => setImageStyle('mindmap')}
                      >
                        🗺️ 思维导图
                      </button>
                      <button
                        className={`style-btn ${imageStyle === 'diagram' ? 'active' : ''}`}
                        onClick={() => setImageStyle('diagram')}
                      >
                        📊 流程图
                      </button>
                      <button
                        className={`style-btn ${imageStyle === 'educational' ? 'active' : ''}`}
                        onClick={() => setImageStyle('educational')}
                      >
                        📖 知识图谱
                      </button>
                    </div>
                  </>
                )}
              </div>

              <div className="chat-input-wrapper">
                {/* 显示推荐按钮 (图片或对话模式) */}
                {(inputMode === 'image' || inputMode === 'chat') && (
                  <button
                    className="recommend-btn"
                    onClick={handleShowRecommendations}
                    disabled={isLoadingRecommendations}
                    title="智能推荐"
                  >
                    {isLoadingRecommendations ? '⏳' : '💡'}
                  </button>
                )}
                <textarea
                  ref={inputRef}
                  className={`chat-input ${(inputMode === 'image' || inputMode === 'chat') ? 'with-recommend-btn' : ''}`}
                  placeholder={inputMode === 'chat'
                    ? '输入你的问题...'
                    : '输入要总结的知识点范围，如：第三章机器学习概念...'
                  }
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows={1}
                />
                <button
                  className="send-btn"
                  onClick={handleSubmit}
                  disabled={!inputValue.trim() || isLoading}
                >
                  {inputMode === 'chat' ? <Icons.Send /> : <Icons.Sparkles />}
                </button>

                {/* 推荐弹窗 */}
                {showRecommendations && (
                  <div className="recommendations-popup">
                    <div className="recommendations-header">
                      <span>💡 智能推荐主题</span>
                      <button
                        className="close-recommendations"
                        onClick={() => setShowRecommendations(false)}
                      >
                        ✕
                      </button>
                    </div>
                    <div className="recommendations-list">
                      {isLoadingRecommendations ? (
                        <div className="recommendation-loading">
                          <div className="recommendation-spinner"></div>
                          <span>正在分析文档生成推荐...</span>
                        </div>
                      ) : recommendations.length === 0 ? (
                        <div className="no-recommendations">暂无推荐，请先上传学习资料</div>
                      ) : (
                        recommendations.map((rec, index) => (
                          <button
                            key={index}
                            className={`recommendation-item recommendation-${rec.type}`}
                            onClick={() => handleSelectRecommendation(rec)}
                          >
                            <span className="rec-icon">
                              {rec.type === 'overview' ? '🌐' :
                                rec.type === 'chapter' ? '📑' :
                                  rec.type === 'summary' ? '📝' :
                                    rec.type === 'qa' ? '❓' :
                                      rec.type === 'review' ? '🎓' : '🔍'}
                            </span>
                            <div className="rec-content">
                              <span className="rec-title">{rec.title}</span>
                              <span className="rec-desc">{rec.description}</span>
                            </div>
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>


            </div>
          </div>
        </div>
      </main>

      {/* Toast Container */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </div>
  )
}

export default App
