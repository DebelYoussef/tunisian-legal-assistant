'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { isAuthenticated, clearAuth } from '@/lib/auth'
import {
  getChatSessions,
  createChatSession,
  deleteChatSession,
  queryLegalDatabase,
  RagSource,
  ChatSession,
} from '@/lib/api'
import { Sidebar } from '@/components/sidebar'
import { ChatMessage } from '@/components/chat-message'
import { ChatInput } from '@/components/chat-input'
import { SourcesPanel } from '@/components/sources-panel'
import { Menu, Settings } from 'lucide-react'

export default function ChatSessionPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string
  const messagesEndRef = useRef<HTMLDivElement>(null)

  interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: RagSource[]
    createdAt: string
  }

  const [messages, setMessages] = useState<Message[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSending, setIsSending] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sources, setSources] = useState<RagSource[]>([])

  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }

    loadData()
  }, [sessionId, router])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const sess = await getChatSessions()
      setSessions(sess)
      // Messages are loaded from chat history; for now start empty
      setMessages([])
    } catch (error) {
      console.error('[v0] Failed to load data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async (content: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Math.random().toString(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsSending(true)

    try {
      // Query RAG endpoint
      const response = await queryLegalDatabase(content, sessionId)

      // Add assistant response with sources
      const assistantMessage: Message = {
        id: Math.random().toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        createdAt: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Extract sources from response
      if (response.sources) {
        setSources(response.sources)
      }
    } catch (error) {
      console.error('[v0] Failed to send message:', error)
      // Remove user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id))
    } finally {
      setIsSending(false)
    }
  }

  const handleNewChat = async () => {
    try {
      const newSession = await createChatSession('Nouvelle conversation')
      setSessions((prev) => [newSession, ...prev])
      router.push(`/chat/${newSession.id}`)
    } catch (error) {
      console.error('[v0] Failed to create chat:', error)
    }
  }

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteChatSession(id)
      setSessions((prev) => prev.filter((s) => s.id !== id))
      if (id === sessionId) {
        router.push('/chat')
      }
    } catch (error) {
      console.error('[v0] Failed to delete session:', error)
    }
  }

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  const currentSession = sessions.find((s) => s.id === sessionId)

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSessionId={sessionId}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onLogout={handleLogout}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main area */}
      <div className="flex-1 flex flex-col">
        {/* Top bar */}
        <div className="h-16 border-b border-border flex items-center justify-between px-4 bg-background">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden p-2 hover:bg-card rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex-1">
              <h1 className="font-semibold text-foreground text-sm md:text-base truncate">
                {currentSession?.title || 'Conversation'}
              </h1>
              <p className="text-xs text-muted-foreground">
                {messages.length} messages
              </p>
            </div>
          </div>

          <button className="p-2 hover:bg-card rounded-lg transition-colors">
            <Settings className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto flex flex-col">
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-accent/20 border-t-accent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Chargement des messages...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">💬</span>
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Commencez la conversation
                </h2>
                <p className="text-muted-foreground">
                  Posez votre première question juridique pour démarrer.
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="p-4 space-y-4">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {isSending && (
                  <ChatMessage
                    message={{
                      id: 'loading',
                      role: 'assistant',
                      content: '',
                      createdAt: new Date().toISOString(),
                    }}
                    isLoading={true}
                  />
                )}
              </div>
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Sources panel */}
        {sources.length > 0 && (
          <div className="max-h-64 overflow-y-auto border-t border-border">
            <SourcesPanel sources={sources} />
          </div>
        )}

        {/* Input area */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading}
          isLoading={isSending}
          placeholder="Posez votre question juridique..."
        />
      </div>
    </div>
  )
}
