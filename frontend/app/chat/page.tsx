'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated, clearAuth } from '@/lib/auth'
import { getChatSessions, createChatSession, deleteChatSession } from '@/lib/api'
import { ChatSession } from '@/lib/api'
import { Sidebar } from '@/components/sidebar'
import { Menu } from 'lucide-react'

export default function ChatPage() {
  const router = useRouter()
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }

    loadSessions()
  }, [router])

  const loadSessions = async () => {
    try {
      setIsLoading(true)
      const data = await getChatSessions()
      setSessions(data)
    } catch (error) {
      console.error('[v0] Failed to load sessions:', error)
    } finally {
      setIsLoading(false)
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
    } catch (error) {
      console.error('[v0] Failed to delete session:', error)
    }
  }

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
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
            <h1 className="text-lg font-semibold text-foreground">
              Assistant Juridique Tunisien
            </h1>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col items-center justify-center overflow-hidden">
          {isLoading ? (
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-accent/20 border-t-accent rounded-full animate-spin" />
              <p className="text-muted-foreground">Chargement des conversations...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center max-w-md">
              <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚖</span>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Bienvenue !
              </h2>
              <p className="text-muted-foreground mb-6">
                Cliquez sur &quot;Nouvelle conversation&quot; pour commencer à poser vos questions juridiques.
              </p>
              <button
                onClick={handleNewChat}
                className="px-6 py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-medium transition-colors"
              >
                Nouvelle conversation
              </button>
            </div>
          ) : (
            <div className="text-center max-w-md">
              <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">💬</span>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Sélectionnez une conversation
              </h2>
              <p className="text-muted-foreground">
                Choisissez une conversation dans la barre latérale ou créez-en une nouvelle.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
