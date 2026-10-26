import { useState } from 'react'
import type { GraphNode, Report } from '../types'

export function ClaimPanel({
  node,
  report,
  onClose,
  onCorrect,
}: {
  node: GraphNode
  report: Report | null
  onClose: () => void
  onCorrect: (text: string) => Promise<void>
}) {
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const sentences = citedBy(node, report)
  const checks = sentences[0]?.checks || []
  return (
    <aside className="flex h-full w-[340px] shrink-0 flex-col border-l border-sand bg-card">
      <div className="flex items-center justify-between px-4 py-3">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-bark/50">Claim</p>
        <button onClick={onClose} className="text-bark/50" aria-label="Close">×</button>
      </div>
      <div className="flex-1 overflow-auto px-4 pb-4">
        <h2 className="font-serif text-[22px] leading-tight text-ink">{node.title || node.label}</h2>
        <div className="mt-3">
          <span className="rounded-full bg-[#efe2cf] px-2 py-1 text-xs font-semibold text-walnut">
            {node.tier === 'secondary' ? 'Secondary' : node.tier === 'user' ? 'User assertion' : 'Primary'} · {node.type}
          </span>
        </div>
        {node.quote && <p className="mt-4 text-sm leading-relaxed text-bark/85">“{node.quote}”</p>}
        {node.contradiction && (
          <p className="mt-3 rounded-xl bg-[#f8efe4] px-3 py-2 text-sm text-clay">{node.contradiction}</p>
        )}
        <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.14em] text-bark/45">Source</p>
        <p className="mt-1 text-sm font-semibold">{node.source_title || node.title}</p>
        <p className="text-sm text-bark/70">{node.date || 'No date'}{node.chunk_id ? ` · ${node.chunk_id}` : ''}</p>
        {node.url && <a className="mt-1 block truncate text-sm text-walnut underline" href={node.url} target="_blank" rel="noreferrer">{node.url}</a>}
        {checks.length > 0 && (
          <>
            <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.14em] text-bark/45">Checks</p>
            <ul className="mt-2 space-y-1 text-sm">
              {checks.map((check) => (
                <li key={check.name} className="flex gap-2">
                  <span className={check.skipped ? 'text-brass' : check.passed ? 'text-moss' : 'text-clay'}>
                    {check.skipped ? '–' : check.passed ? '✓' : '!'}
                  </span>
                  <span>{check.detail}</span>
                </li>
              ))}
            </ul>
          </>
        )}
        <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.14em] text-bark/45">Why it is in the report</p>
        {sentences.length === 0 ? (
          <p className="mt-1 text-sm text-bark/70">No report sentence cites this node.</p>
        ) : (
          <ul className="mt-2 space-y-2 text-sm leading-relaxed">
            {sentences.map((sentence) => (
              <li key={sentence.id}>{sentence.text}</li>
            ))}
          </ul>
        )}
        {report?.summary && (
          <>
            <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.14em] text-bark/45">Report summary</p>
            <p className="mt-1 text-sm leading-relaxed">{report.summary}</p>
          </>
        )}
        <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.14em] text-bark/45">Correct or add context</p>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder='e.g. "These two terms mean the same product."'
          className="mt-2 h-24 w-full resize-none rounded-2xl border border-sand bg-paper px-3 py-2 text-sm outline-none"
        />
        <button
          disabled={busy || note.trim().length < 3}
          onClick={async () => {
            setBusy(true)
            try { await onCorrect(note.trim()); setNote('') } finally { setBusy(false) }
          }}
          className="mt-2 rounded-full bg-walnut px-4 py-2 text-sm font-semibold text-[#f6efe4] disabled:opacity-40"
        >
          {busy ? 'Re-running writer…' : 'Save and re-verify'}
        </button>
        <p className="mt-2 text-xs text-bark/55">Saved as an unverified user assertion. Only the writer and verifier run again.</p>
      </div>
    </aside>
  )
}

function citedBy(node: GraphNode, report: Report | null) {
  return (report?.sentences || []).filter((sentence) => {
    if ((node.sentence_ids || []).includes(sentence.id)) return true
    if (sentence.claim_ids.includes(node.id)) return true
    if (node.type === 'document') return sentence.claim_ids.some((id) => id.startsWith(`${node.id}:`))
    return false
  })
}
