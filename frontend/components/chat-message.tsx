'use client'

import { RagSource } from '@/lib/api'
import { Copy, Check } from 'lucide-react'
import { useState } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: RagSource[]
  createdAt: string
}

interface ChatMessageProps {
  message: Message
  isLoading?: boolean
}

export function ChatMessage({ message, isLoading }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)
  const isAssistant = message.role === 'assistant'

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isLoading) {
    return (
      <div className="flex items-end gap-3 mb-4">
        <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
        </div>
        <div className="bg-card rounded-lg px-4 py-3 max-w-md">
          <div className="flex gap-2">
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-100" />
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-200" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-3 mb-4 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      {isAssistant && (
        <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-semibold">⚖</span>
        </div>
      )}

      <div
        className={`max-w-md rounded-lg px-4 py-3 ${
          isAssistant ? 'bg-card text-foreground' : 'bg-accent text-white'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

        {isAssistant && (
          <button
            onClick={copyToClipboard}
            className="mt-2 flex items-center gap-2 text-xs opacity-60 hover:opacity-100 transition-opacity"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3" />
                Copié
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                Copier
              </>
            )}
          </button>
        )}
      </div>

      {!isAssistant && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm">U</span>
        </div>
      )}
    </div>
  )
}

/**
 * Sources display for messages with law references
 */
export function MessageSources({ sources = [] }: { sources?: RagSource[] }) {
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-4 pt-4 border-t border-border space-y-2">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
        Sources Juridiques
      </p>
      <div className="space-y-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="block text-xs border border-border rounded p-2 hover:bg-card/50 transition-colors"
          >
            <div className="flex items-start gap-2">
              <span className="flex-shrink-0 text-accent text-xs mt-0.5">→</span>
              <div className="flex-1">
                <p className="font-medium text-foreground">{source.document_name}</p>
                <p className="text-muted-foreground text-xs line-clamp-2 mt-1">{source.text}</p>
                <div className="mt-1 flex items-center gap-1">
                  <div className="text-xs text-accent font-medium">
                    {Math.round(source.score * 100)}% pertinent
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
