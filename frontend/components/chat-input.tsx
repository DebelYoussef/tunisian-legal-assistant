'use client'

import { Send } from 'lucide-react'
import { useRef, useEffect, useState } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = 'Posez votre question juridique...',
}: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-grow textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
  }, [value])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Handle IME composition state (CJK languages)
    if (e.nativeEvent instanceof CompositionEvent || 'isComposing' in e.nativeEvent) {
      return
    }

    const trimmed = value.trim()
    if (!trimmed || isLoading) return

    onSend(trimmed)
    setValue('')

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (but not Shift+Enter for new line)
    // Also respect IME composition state
    if (
      e.key === 'Enter' &&
      !e.shiftKey &&
      !e.nativeEvent.isComposing &&
      e.nativeEvent.keyCode !== 229
    ) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex gap-3 p-4 border-t border-border bg-background"
    >
      <div className="flex-1 flex items-end gap-2 bg-card rounded-lg px-4 py-3 border border-input focus-within:border-accent transition-colors">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isLoading}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-foreground placeholder-muted-foreground outline-none resize-none text-sm min-h-6"
          rows={1}
        />
      </div>

      <button
        type="submit"
        disabled={disabled || isLoading || !value.trim()}
        className="flex-shrink-0 w-10 h-10 rounded-lg bg-accent hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
        aria-label="Send message"
      >
        <Send className="w-5 h-5" />
      </button>
    </form>
  )
}
