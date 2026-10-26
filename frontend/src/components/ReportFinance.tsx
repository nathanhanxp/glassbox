import { useState } from 'react'
import type { GraphNode, Report, Sentence } from '../types'

const money = (n: number) =>
  n >= 1_000_000_000 ? `$${(n / 1_000_000_000).toFixed(2)}B` : `$${(n / 1_000_000).toFixed(1)}M`

export function ReportView({
  report,
  nodes,
  onCite,
}: {
  report: Report
  nodes: GraphNode[]
  onCite: (id: string) => void
}) {
  const byId = new Map(nodes.map((node) => [node.id, node]))
  const [editing, setEditing] = useState(false)
  const [note, setNote] = useState('')
  const [addition, setAddition] = useState<string | null>(null)
  return (
    <article className="report-sheet h-full overflow-auto px-8 py-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brass">Report</p>
          <h2 className="mt-1 font-serif text-3xl text-ink">{report.title}</h2>
          <p className="mt-2 max-w-3xl text-bark/80">{report.question}</p>
          <p className="mt-1 text-sm text-bark/60">As of {report.as_of}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setEditing((open) => !open)} className="rounded-full border border-sand bg-card px-4 py-2 text-sm font-semibold text-walnut">
            Edit
          </button>
          <button onClick={() => exportPdf(report, nodes, addition)} className="rounded-full bg-walnut px-4 py-2 text-sm font-semibold text-[#f6efe4]">
            Export PDF
          </button>
        </div>
      </div>
      {editing && (
        <form
          className="mt-4 rounded-2xl border border-sand bg-card p-4"
          onSubmit={(e) => {
            e.preventDefault()
            const typed = note.trim() || 'Add the peer cash-ratio context'
            setAddition(
              `Your edit: “${typed}”. NVIDIA NIM search is hardcoded for this demo and was not called. It would look for a second source on this point. The hardcoded result: LPL, not Schwab, reported client cash at 2.2% of client assets in its July 30, 2026 release. Schwab’s own October 15, 2026 release remains the source for the $492.8 billion sweep figure.`,
            )
            setEditing(false)
            setNote('')
          }}
        >
          <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Add a line to the report" className="h-24 w-full rounded-xl border border-sand bg-paper p-3 text-sm" />
          <button className="mt-2 rounded-full bg-walnut px-4 py-2 text-sm font-semibold text-[#f6efe4]">Add to report</button>
        </form>
      )}
      {addition && <p className="mt-4 rounded-2xl border border-brass bg-[#f6ecda] px-4 py-3 text-sm leading-relaxed">{addition}</p>}
      <h3 className="mt-8 font-serif text-xl">Findings</h3>
      <div className="mt-3 space-y-4">
        {report.sentences.map((sentence) => (
          <SentenceBlock key={sentence.id} sentence={sentence} byId={byId} onCite={onCite} />
        ))}
      </div>
      <h3 className="mt-10 font-serif text-xl">Scenario</h3>
      <p className="mt-1 max-w-3xl text-sm text-bark/70">What the cited Schwab figures imply if sweep cash migrates. The yield spread is an assumption. It is not a second report.</p>
      <FinanceView report={report} />
      {report.gaps?.length > 0 && (
        <section className="mt-8">
          <h3 className="font-serif text-xl">Still open</h3>
          <div className="mt-3 space-y-2 text-sm text-bark">
            {report.gaps.map((gap) => <p key={gap}>{gap}</p>)}
          </div>
        </section>
      )}
    </article>
  )
}

function SentenceBlock({
  sentence,
  byId,
  onCite,
}: {
  sentence: Sentence
  byId: Map<string, GraphNode>
  onCite: (id: string) => void
}) {
  const tone = sentence.status === 'supported' ? 'border-moss/30' : sentence.status === 'unverified' ? 'border-brass' : 'border-clay/50'
  return (
    <div className={`rounded-2xl border bg-card px-4 py-3 ${tone}`}>
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
        <span className={sentence.status === 'supported' ? 'text-moss' : 'text-clay'}>{sentence.status}</span>
        {sentence.derived && <span className="text-brass">recomputed</span>}
        {sentence.hedged && <span className="text-brass">hedged</span>}
      </div>
      <p className="text-[15px] leading-relaxed text-ink">{sentence.text}</p>
      <div className="mt-2 space-y-1">
        {sentence.claim_ids.map((id) => {
          const node = byId.get(id)
          return (
            <p key={id} className="text-sm">
              <button onClick={() => onCite(id)} className="font-semibold text-walnut underline">
                {node?.source_title || node?.label || id}
              </button>
              {node?.date ? <span className="text-bark/60"> · {node.date}</span> : null}
              {node?.url ? (
                <a className="mt-0.5 block truncate text-walnut underline" href={node.url} target="_blank" rel="noreferrer">{node.url}</a>
              ) : null}
            </p>
          )
        })}
      </div>
    </div>
  )
}

export function FinanceView({ report }: { report: Report }) {
  const finance = report.finance
  if (!finance?.knowable || !finance.balance) {
    return <div className="p-8 text-bark/70">{finance?.reason || 'No sweep balance is knowable at this as-of date.'}</div>
  }
  return (
    <div className="mt-3">
      <p className="mt-2 max-w-3xl text-sm text-bark/75">{finance.formula}</p>
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <Card k="Sweep balance" v={`$${finance.balance.balance_billion}B`} d={finance.balance.source} />
        <Card k="Yield spread" v="250 bp" d={finance.spread_label || ''} />
        <Card
          k="Firm NIM, not used"
          v={finance.nim_context?.value || '—'}
          d={finance.nim_context ? 'Shown for context. Not an input to the scenario.' : 'Not knowable at this as-of date.'}
        />
      </div>
      <table className="mt-6 w-full overflow-hidden rounded-2xl border border-sand text-sm">
        <thead className="bg-sand/70 text-left text-walnut">
          <tr>
            <th className="px-4 py-3">Migration</th>
            <th className="px-4 py-3">Cash that leaves</th>
            <th className="px-4 py-3">Annual revenue at risk</th>
          </tr>
        </thead>
        <tbody>
          {finance.rows?.map((row) => (
            <tr key={row.migration} className="border-t border-sand bg-card">
              <td className="px-4 py-3 font-semibold">{Math.round(row.migration * 100)}%</td>
              <td className="px-4 py-3">${row.migrated_billion}B</td>
              <td className="px-4 py-3">{money(row.annual_revenue_at_risk)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-xs text-bark/60">{finance.spread_note}</p>
      {finance.also_knowable && (
        <ul className="mt-4 space-y-1 text-sm text-bark/80">
          {finance.also_knowable.map((item) => (
            <li key={item.label}>{item.label}: ${item.balance_billion}B · {item.source}</li>
          ))}
        </ul>
      )}
      {finance.recompute && (
        <div className="mt-6 rounded-3xl border border-sand bg-card p-5">
          <h3 className="font-serif text-xl">Recompute of the third-party $12.5B figure</h3>
          <p className="mt-2 text-sm leading-relaxed text-bark/80">{finance.recompute.note}</p>
          <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
            <Item k="June sweep" v={`$${finance.recompute.june_sweep_billion}B`} d={finance.recompute.june_sweep_source} />
            <Item k="June short credits" v={`$${finance.recompute.june_short_credits_billion}B`} d={finance.recompute.june_short_source} />
            <Item k="June ex-short" v={`$${finance.recompute.june_ex_short_billion}B`} d="485.7 − 43.7" />
            <Item k="September sweep" v={`$${finance.recompute.sept_sweep_billion}B`} d={finance.recompute.sept_sweep_source} />
            <Item k="September short credits" v={`$${finance.recompute.sept_short_credits_billion}B`} d={finance.recompute.sept_short_source} />
            <Item k="September ex-short" v={`$${finance.recompute.sept_ex_short_billion}B`} d="492.8 − 63.3" />
          </dl>
          <p className="mt-4 font-serif text-2xl text-ink">Decline ex-short credits: ${finance.recompute.decline_billion}B</p>
        </div>
      )}
    </div>
  )
}

function Card({ k, v, d }: { k: string; v: string; d: string }) {
  return (
    <div className="rounded-2xl border border-sand bg-card p-4">
      <p className="text-xs uppercase tracking-wide text-brass">{k}</p>
      <p className="mt-1 font-serif text-2xl">{v}</p>
      <p className="mt-1 text-xs text-bark/70">{d}</p>
    </div>
  )
}

function Item({ k, v, d }: { k: string; v: string; d: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-brass">{k}</dt>
      <dd className="font-semibold">{v}</dd>
      <dd className="text-xs text-bark/60">{d}</dd>
    </div>
  )
}

function escapeHtml(value: string) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function exportPdf(report: Report, nodes: GraphNode[], addition: string | null) {
  const byId = new Map(nodes.map((node) => [node.id, node]))
  const findings = report.sentences.map((sentence) => {
    const sources = sentence.claim_ids.map((id) => {
      const node = byId.get(id)
      const title = escapeHtml(node?.source_title || node?.label || id)
      const link = node?.url ? ` <a href="${escapeHtml(node.url)}">${escapeHtml(node.url)}</a>` : ''
      return `<li>${title}${node?.date ? ` (${escapeHtml(node.date)})` : ''}${link}</li>`
    }).join('')
    return `<h3>${escapeHtml(sentence.status)}</h3><p>${escapeHtml(sentence.text)}</p><ul>${sources}</ul>`
  }).join('')
  const finance = report.finance
  const rows = (finance?.rows || []).map((row) =>
    `<tr><td>${Math.round(row.migration * 100)}%</td><td>$${row.migrated_billion}B</td><td>${money(row.annual_revenue_at_risk)}</td></tr>`,
  ).join('')
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(report.title)}</title>
    <style>
      body { font-family: Georgia, serif; color: #2c241c; margin: 48px auto; max-width: 740px; line-height: 1.45; }
      a { color: #6b4528; }
      table { border-collapse: collapse; width: 100%; }
      td, th { border-bottom: 1px solid #e4d8c6; text-align: left; padding: 6px; }
    </style></head><body>
    <p>REPORT</p>
    <h1>${escapeHtml(report.title)}</h1>
    <p>${escapeHtml(report.question)}</p>
    <p>As of ${escapeHtml(report.as_of)}</p>
    ${addition ? `<h2>Added</h2><p>${escapeHtml(addition)}</p>` : ''}
    <h2>Findings</h2>${findings}
    <h2>Scenario</h2>
    <p>${escapeHtml(finance?.formula || '')}</p>
    <p>Sweep balance ${finance?.balance ? `$${finance.balance.balance_billion}B` : 'n/a'}. ${escapeHtml(finance?.balance?.source || '')}</p>
    <table><tr><th>Migration</th><th>Cash that leaves</th><th>Annual revenue at risk</th></tr>${rows}</table>
    <p>${escapeHtml(finance?.spread_note || '')}</p>
    ${(report.gaps || []).length ? `<h2>Still open</h2>${report.gaps.map((gap) => `<p>${escapeHtml(gap)}</p>`).join('')}` : ''}
    <script>window.onload = function () { window.print() }<\/script>
    </body></html>`
  const popup = window.open('', '_blank', 'width=900,height=700')
  if (!popup) {
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'glassbox-report.html'
    link.click()
    URL.revokeObjectURL(url)
    return
  }
  popup.document.open()
  popup.document.write(html)
  popup.document.close()
}
