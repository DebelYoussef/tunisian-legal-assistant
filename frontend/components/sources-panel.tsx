'use client'

import { RagSource } from '@/lib/api'
import { ChevronDown } from 'lucide-react'
import { useState } from 'react'

interface SourcesPanelProps {
  sources?: RagSource[]
  title?: string
}

export function SourcesPanel({
  sources = [],
  title = 'Sources Juridiques',
}: SourcesPanelProps) {
  const [expanded, setExpanded] = useState(true)

  if (!sources || sources.length === 0) {
    return (
      <div className="px-4 py-3 text-sm text-muted-foreground text-center">
        Aucune source disponible
      </div>
    )
  }

  return (
    <div className="border-t border-border">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-card/50 transition-colors"
      >
        <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
          {title}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground transition-transform ${
            expanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-border/50">
          {sources.map((source, index) => (
            <SourceItem key={index} source={source} />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Individual source item
 */
function SourceItem({ source }: { source: RagSource }) {
  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500'
    if (score >= 0.6) return 'text-blue-500'
    return 'text-orange-500'
  }

  const getRelevanceLabel = (score: number) => {
    if (score >= 0.8) return 'Très pertinent'
    if (score >= 0.6) return 'Pertinent'
    return 'Pertinent'
  }

  return (
    <div className="group p-3 rounded-lg bg-card border border-border hover:border-accent transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-semibold text-foreground group-hover:text-accent transition-colors line-clamp-2 flex-1">
          {source.document_name}
        </h4>
        <span
          className={`text-xs font-medium flex-shrink-0 ${getRelevanceColor(
            source.score
          )}`}
        >
          {Math.round(source.score * 100)}%
        </span>
      </div>

      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{source.text}</p>

      <div className="flex items-center">
        <span className="text-xs text-muted-foreground">
          {getRelevanceLabel(source.score)}
        </span>
      </div>
    </div>
  )
}
