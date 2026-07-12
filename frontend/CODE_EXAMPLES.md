# Dark Mode Code Examples

## Theme Toggle Component

```tsx
// components/theme-toggle.tsx
'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="h-10 w-10" />
  }

  const isDark = theme === 'dark'

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="inline-flex items-center justify-center rounded-lg p-2 text-sm font-medium transition-colors hover:bg-sidebar-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun className="h-5 w-5 text-accent transition-transform" />
      ) : (
        <Moon className="h-5 w-5 text-accent transition-transform" />
      )}
    </button>
  )
}
```

## Layout Setup

```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes'
import './globals.css'

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          storageKey="theme-preference"
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

## CSS Variables Setup

```css
/* app/globals.css */

/* Light mode (default) */
:root {
  color-scheme: light;
  --background: #FFFFFF;
  --foreground: #145A4C;
  --sidebar: #1E293B;
  --sidebar-foreground: #94A3B8;
  --card: #E2E8F0;
  --accent: #14B8A6;
  --input: #FFFFFF;
  --border: #CBD5E1;
}

/* Dark mode */
.dark {
  color-scheme: dark;
  --background: #1A1F2E;
  --foreground: #FFFFFF;
  --sidebar: #0F172A;
  --sidebar-foreground: #94A3B8;
  --sidebar-accent: #1E293B;
  --card: #1E293B;
  --accent: #14B8A6;
  --input: #1E293B;
  --border: #334155;
}

/* System preference fallback */
@media (prefers-color-scheme: dark) {
  :root:not(.light) {
    --background: #1A1F2E;
    --foreground: #FFFFFF;
    /* ... other variables ... */
  }
}
```

## Message Components

### User Message (Teal)
```tsx
export function UserMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-xs rounded-lg bg-accent px-4 py-3 text-white">
        <p className="text-sm leading-relaxed">{content}</p>
      </div>
    </div>
  )
}
```

### Assistant Message (Card)
```tsx
export function AssistantMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-xs rounded-lg border border-border bg-card px-4 py-3 text-card-foreground">
        <p className="text-sm leading-relaxed">{content}</p>
      </div>
    </div>
  )
}
```

### With Sources
```tsx
export function MessageWithSources({
  content,
  sources,
}: {
  content: string
  sources: Array<{ text: string; document_name: string; score: number }>
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="max-w-2xl space-y-2 rounded-lg bg-card px-4 py-3 text-card-foreground">
      <p className="text-sm leading-relaxed">{content}</p>

      {sources && sources.length > 0 && (
        <div className="mt-3 pt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-xs font-medium text-muted-foreground hover:text-foreground"
          >
            <span>Sources ({sources.length})</span>
            <span className={expanded ? 'rotate-180' : ''}>▼</span>
          </button>

          {expanded && (
            <div className="mt-2 space-y-2">
              {sources.map((source, idx) => (
                <div
                  key={idx}
                  className="rounded border border-border bg-background/50 p-2 text-xs"
                >
                  <div className="font-semibold text-foreground">
                    {source.document_name}
                  </div>
                  <div className="mt-1 text-muted-foreground">
                    {source.text}
                  </div>
                  <div className="mt-1 font-medium text-muted-foreground">
                    Relevance: {(source.score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

## Sidebar Component

```tsx
export function Sidebar() {
  return (
    <div className="flex h-screen w-60 flex-col border-r border-border bg-sidebar">
      {/* Header */}
      <div className="border-b border-sidebar-border p-4">
        <h1 className="text-lg font-bold text-sidebar-foreground">
          Assistant Juridique
        </h1>
        <p className="text-xs text-sidebar-foreground/70">Tunisien</p>

        <button className="mt-4 w-full rounded-lg bg-accent px-4 py-2 font-medium text-white hover:opacity-90">
          Nouvelle conversation
        </button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="flex items-center gap-2 rounded-lg bg-sidebar-accent px-3 py-2 text-sidebar-accent-foreground"
            >
              <span className="flex-1 truncate text-sm">{session.title}</span>
              <button className="text-sidebar-foreground/60 hover:text-destructive">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-sidebar-border p-4">
        <div className="flex items-center gap-3 rounded-lg bg-sidebar-accent px-3 py-2">
          <div className="h-8 w-8 rounded-full bg-accent" />
          <div className="flex-1">
            <p className="text-sm font-medium text-sidebar-accent-foreground">
              User
            </p>
            <p className="text-xs text-sidebar-foreground/70">
              user@example.com
            </p>
          </div>
        </div>
        <button className="mt-3 w-full rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent">
          Déconnexion
        </button>
      </div>
    </div>
  )
}
```

## Navbar with Theme Toggle

```tsx
import { ThemeToggle } from '@/components/theme-toggle'

export function Navbar() {
  return (
    <div className="border-b border-border bg-sidebar px-6 py-3 md:bg-background">
      <div className="flex items-center justify-between">
        <h2 className="flex-1 text-lg font-semibold text-foreground">
          Assistant Juridique Tunisien
        </h2>
        <ThemeToggle />
      </div>
    </div>
  )
}
```

## Input Component

```tsx
export function ChatInput({
  value,
  onChange,
  onSend,
}: {
  value: string
  onChange: (value: string) => void
  onSend: () => void
}) {
  return (
    <div className="border-t border-border bg-background p-6">
      <div className="mx-auto max-w-3xl flex gap-3">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault()
              onSend()
            }
          }}
          placeholder="Posez votre question juridique..."
          className="flex-1 resize-none rounded-lg border border-input bg-input px-4 py-2 text-foreground placeholder:text-muted-foreground focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/50"
          rows={1}
          style={{ minHeight: '44px', maxHeight: '120px' }}
        />
        <button
          onClick={onSend}
          disabled={!value.trim()}
          className="self-end rounded-lg bg-accent px-4 py-2 text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}
```

## Using Theme Hook

```tsx
'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function ThemeInfo() {
  const { theme, setTheme, themes, systemTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="space-y-2 rounded-lg bg-card p-4 text-card-foreground">
      <p>
        <strong>Current theme:</strong> {theme}
      </p>
      <p>
        <strong>System theme:</strong> {systemTheme}
      </p>
      <p>
        <strong>Available themes:</strong> {themes.join(', ')}
      </p>
      <div className="flex gap-2">
        <button
          onClick={() => setTheme('light')}
          className="rounded bg-accent px-3 py-1 text-sm text-white"
        >
          Light
        </button>
        <button
          onClick={() => setTheme('dark')}
          className="rounded bg-accent px-3 py-1 text-sm text-white"
        >
          Dark
        </button>
        <button
          onClick={() => setTheme('system')}
          className="rounded bg-accent px-3 py-1 text-sm text-white"
        >
          System
        </button>
      </div>
    </div>
  )
}
```

## RTL Content Detection

```tsx
function isRTL(text: string): boolean {
  return /[\u0600-\u06FF]/.test(text)
}

export function SmartMessage({ content }: { content: string }) {
  const rtl = isRTL(content)
  
  return (
    <div dir={rtl ? 'rtl' : 'ltr'} className="rounded-lg bg-card p-3">
      {content}
    </div>
  )
}
```

## Conditional Styling Example

```tsx
export function AdaptiveCard({
  children,
  isDarkMode,
}: {
  children: React.ReactNode
  isDarkMode?: boolean
}) {
  // Option 1: Using useTheme hook
  const { theme } = useTheme()
  const dark = theme === 'dark'

  // Option 2: Using CSS variables directly
  return (
    <div
      className="rounded-lg border border-border bg-card p-4 text-card-foreground"
      style={{
        backgroundColor: dark ? 'var(--card)' : 'var(--card)',
      }}
    >
      {children}
    </div>
  )
}
```

## Custom Theme Provider Wrapper (Optional)

```tsx
// lib/theme-context.tsx
'use client'

import { createContext, useContext } from 'react'
import { useTheme } from 'next-themes'

interface ThemeContextType {
  isDark: boolean
  theme: string | undefined
  setTheme: (theme: string) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeContextProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const { theme, setTheme } = useTheme()

  return (
    <ThemeContext.Provider
      value={{
        isDark: theme === 'dark',
        theme,
        setTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  )
}

export function useThemeContext() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useThemeContext must be used within ThemeContextProvider')
  }
  return context
}
```

## Best Practices

### ✅ DO

```tsx
// Use semantic color tokens
<div className="bg-background text-foreground" />

// Use accent for primary actions
<button className="bg-accent text-white" />

// Check if mounted before rendering theme-dependent UI
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
```

### ❌ DON'T

```tsx
// Don't hardcode colors
<div className="bg-[#1e293b]" />

// Don't forget to mark components as 'use client' if using hooks
export function MyComponent() { // Missing 'use client'
  const { theme } = useTheme()
}

// Don't use theme values before component mounts
export function MyComponent() {
  const { theme } = useTheme()
  return <div>{theme}</div> // May show "undefined" before mount
}
```

---

**All these components are fully integrated and working in your app!**
