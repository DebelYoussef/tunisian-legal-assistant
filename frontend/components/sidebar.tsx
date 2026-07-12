'use client'

import { ChatSession } from '@/lib/api'
import { Plus, MessageSquare, MoreVertical, Trash2, LogOut } from 'lucide-react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { useState } from 'react'
import { useTheme } from 'next-themes'
import { Sun, Moon } from 'lucide-react'
import Image from 'next/image'

interface SidebarProps {
  sessions: ChatSession[]
  currentSessionId?: string
  onNewChat: () => void
  onDeleteSession: (id: string) => void
  onLogout: () => void
  isOpen?: boolean
  onClose?: () => void
}

export function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onDeleteSession,
  onLogout,
  isOpen = true,
  onClose,
}: SidebarProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)

  const handleSelectSession = (id: string) => {
    router.push(`/chat/${id}`)
    onClose?.()
  }

  const handleDeleteSession = (e: React.MouseEvent, id: string) => {
    e.preventDefault()
    e.stopPropagation()
    if (confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      onDeleteSession(id)
      setOpenMenuId(null)
    }
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static top-0 left-0 h-full w-64 bg-sidebar border-r border-sidebar-border flex flex-col transition-transform z-50 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="p-4 border-b border-sidebar-border">
          {/* Logo */}
          <div className="mb-4 flex justify-center">
            <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-accent/20 flex items-center justify-center bg-card">
              <Image
                src="/logo.png"
                alt="Assistant Juridique Tunisien"
                width={96}
                height={96}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-accent-foreground font-medium transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nouvelle conversation
          </button>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto py-4">
          {sessions.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm text-sidebar-foreground opacity-60">
                Aucune conversation
              </p>
            </div>
          ) : (
            <div className="space-y-2 px-2">
              {sessions.map((session) => (
                <SessionItem
                  key={session.id}
                  session={session}
                  isActive={session.id === currentSessionId}
                  onSelect={() => handleSelectSession(session.id)}
                  onDelete={(e) => handleDeleteSession(e, session.id)}
                  isMenuOpen={openMenuId === session.id}
                  onMenuToggle={(open) => setOpenMenuId(open ? session.id : null)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-sidebar-border space-y-2">
          {/* Theme toggle */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg hover:bg-sidebar-accent transition-colors text-sidebar-foreground"
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-4 h-4" />
                Mode clair
              </>
            ) : (
              <>
                <Moon className="w-4 h-4" />
                Mode sombre
              </>
            )}
          </button>

          {/* Logout button */}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg hover:bg-red-500/10 transition-colors text-sidebar-foreground hover:text-red-500"
          >
            <LogOut className="w-4 h-4" />
            Déconnexion
          </button>
        </div>
      </aside>
    </>
  )
}

/**
 * Individual session item
 */
function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
  isMenuOpen,
  onMenuToggle,
}: {
  session: ChatSession
  isActive: boolean
  onSelect: () => void
  onDelete: (e: React.MouseEvent) => void
  isMenuOpen: boolean
  onMenuToggle: (open: boolean) => void
}) {
  return (
    <div className="relative group">
      <button
        onClick={onSelect}
        className={`w-full text-left px-3 py-2.5 rounded-lg transition-colors truncate ${
          isActive
            ? 'bg-sidebar-accent text-sidebar-accent-foreground'
            : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
        }`}
      >
        <div className="flex items-center gap-2 min-w-0">
          <MessageSquare className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm truncate">{session.title}</span>
        </div>
      </button>

      {/* Menu button */}
      <div className="absolute right-2 top-2.5">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onMenuToggle(!isMenuOpen)
          }}
          className={`p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
            isMenuOpen ? 'opacity-100 bg-sidebar-accent/50' : 'hover:bg-sidebar-accent/50'
          }`}
        >
          <MoreVertical className="w-4 h-4" />
        </button>

        {/* Dropdown menu */}
        {isMenuOpen && (
          <div className="absolute right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-10 min-w-max">
            <button
              onClick={onDelete}
              className="w-full text-left px-3 py-2 text-sm text-red-500 hover:bg-red-500/10 flex items-center gap-2 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Supprimer
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
