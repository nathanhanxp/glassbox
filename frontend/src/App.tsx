import { useEffect, useState } from 'react'
import { api, streamEvents } from './api'
import { ClaimPanel } from './components/ClaimPanel'
import { GraphView } from './components/GraphView'
import { Pipeline } from './components/Pipeline'
import { ReportView } from './components/ReportFinance'
import type { GraphData, GraphNode, PipelineEvent, Report, RunSummary, SourceRow } from './types'

type Tab = 'graph' | 'pipeline' | 'report'

const COMPANY_NAME: Record<string, string> = {
  SCHW: 'Schwab',
  LPLA: 'LPL',
  RJF: 'Raymond James',
  AMP: 'Ameriprise',
  MS: 'Morgan Stanley',
  JPM: 'JPMorgan',
  USER: 'Your note',
}
const COMPANY_COLOR: Record<string, string> = {
  SCHW: '#e0c48a',
  LPLA: '#8fb596',
  RJF: '#8eb0c8',
  AMP: '#e0a48a',
  MS: '#c4a6c0',
  JPM: '#9db8a4',
  USER: '#f1d7b0',
}

const MIN = Date.parse('2025-10-16')
const MAX = Date.parse('2026-10-26')

function dayLabel(iso: string) {
  const day = iso.slice(0, 10)
  if (day === '2026-10-26') return 'Today'
  if (day === '2026-10-25') return 'Yesterday'
  return day
}

function formatAsOf(value: string) {
  const date = new Date(value + 'T00:00:00')
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [active, setActive] = useState<string>('run-schwab')
  const [report, setReport] = useState<Report | null>(null)
  const [graph, setGraph] = useState<GraphData | null>(null)
  const [tab, setTab] = useState<Tab>('graph')
  const [mode, setMode] = useState<'3d' | '2d'>('3d')
  const [asOf, setAsOf] = useState('2026-10-26')
  const [picked, setPicked] = useState<GraphNode | null>(null)
  const [events, setEvents] = useState<PipelineEvent[]>([])
  const [step, setStep] = useState<number | null>(null)
  const [sources, setSources] = useState<SourceRow[]>([])
  const [creating, setCreating] = useState(false)
  const [question, setQuestion] = useState('Did the third-quarter cash move mean sorting is back?')
  const [newAsOf, setNewAsOf] = useState('2026-10-26')

  async function loadRuns() {
    const list = await api.runs()
    setRuns(list)
    return list
  }

  async function openRun(id: string, date?: string) {
    const next = await api.report(id)
    setReport(next)
    setActive(id)
    const viewDate = date || next.as_of
    setAsOf(viewDate)
    setGraph(await api.graph(id, viewDate))
    setSources(await api.sources(id))
    setPicked(null)
    setStep(null)
  }

  useEffect(() => {
    loadRuns().then((list) => {
      const id = list.find((r) => r.id === 'run-schwab')?.id || list[0]?.id
      if (id) openRun(id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!active) return
    let cancelled = false
    setEvents([])
    const stop = streamEvents(active, false, (event) => {
      if (cancelled) return
      setEvents((prev) => (event.id != null && prev.some((item) => item.id === event.id) ? prev : [...prev, event]))
      if (event.kind === 'done' && event.message !== 'Replay finished.') {
        openRun(active, asOf)
        loadRuns()
      }
    })
    return () => {
      cancelled = true
      stop()
    }
  }, [active])

  async function slide(value: number) {
    const date = new Date(value).toISOString().slice(0, 10)
    setAsOf(date)
    if (active) setGraph(await api.graph(active, date))
  }

  const companiesInGraph = Array.from(new Set((graph?.nodes || []).map((node) => node.company).filter(Boolean))) as string[]

  return (
    <div className="flex h-full min-h-screen">
      <aside className="flex w-[280px] shrink-0 flex-col border-r border-[#e4d8c6] bg-[#f7f1e6] px-4 py-4">
        <div className="flex items-center gap-2 px-1">
          <span className="grid h-8 w-8 place-items-center rounded-xl bg-walnut text-sm text-[#f6efe4]">Gb</span>
          <span className="font-serif text-xl">Glassbox</span>
        </div>
        <button onClick={() => setCreating(true)} className="mt-4 rounded-2xl bg-walnut px-4 py-3 text-left text-sm font-semibold text-[#f6efe4]">
          + New report
        </button>
        <p className="mt-6 px-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-bark/45">Report history</p>
        <div className="mt-2 space-y-2 overflow-auto">
          {runs.map((run) => (
            <button
              key={run.id}
              onClick={() => { setEvents([]); openRun(run.id) }}
              className={`w-full rounded-2xl border px-3 py-3 text-left ${run.id === active ? 'border-brass bg-card shadow-desk' : 'border-transparent bg-white/40'}`}
            >
              <p className="text-sm font-semibold leading-snug">{run.title}</p>
              <p className="mt-1 text-xs text-bark/55">{dayLabel(run.created_at)} · as of {formatAsOf(run.as_of)}</p>
              <div className="mt-2">
                {run.unsupported > 0 ? (
                  <span className="rounded-full bg-[#f3ddc8] px-2 py-0.5 text-[11px] font-semibold text-clay">{run.unsupported} unsupported</span>
                ) : (
                  <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${run.status === 'draft' ? 'bg-sand text-bark/70' : 'bg-[#e5f0e4] text-moss'}`}>
                    {run.status === 'draft' ? 'Draft' : 'Verified'}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 p-3">
        <section className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-[28px] border border-[#e6d9c6] bg-[#fbf7f1] shadow-desk">
          <header className="flex flex-wrap items-center gap-3 px-4 py-3">
            <div className="flex rounded-full bg-sand/80 p-1">
              {(['graph', 'pipeline', 'report'] as Tab[]).map((item) => (
                <button
                  key={item}
                  onClick={() => setTab(item)}
                  className={`rounded-full px-3 py-1.5 text-sm capitalize ${tab === item ? 'bg-card font-semibold shadow' : 'text-bark/70'}`}
                >
                  {item === 'pipeline' ? 'Agent pipeline' : item[0].toUpperCase() + item.slice(1)}
                </button>
              ))}
            </div>
            {tab === 'graph' && (
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-bark/80">
                {companiesInGraph.map((company) => (
                  <span key={company} className="flex items-center gap-1">
                    <i className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: COMPANY_COLOR[company] || '#d9c4a0' }} />
                    {COMPANY_NAME[company] || company}
                  </span>
                ))}
                <span className="flex items-center gap-1">
                  <i className="inline-block h-2.5 w-2.5 rounded-full bg-clay" />
                  Unsupported
                </span>
                <span className="flex items-center gap-1">
                  <i className="inline-block h-0.5 w-4 bg-[#c4b39a]" />
                  Claim from this filing
                </span>
                <span className="flex items-center gap-1">
                  <i className="inline-block h-0.5 w-4 border-b border-dashed border-clay" />
                  Readings disagree
                </span>
              </div>
            )}
            <div className="ml-auto flex items-center gap-2">
              {tab === 'graph' && (
                <button onClick={() => setMode(mode === '3d' ? '2d' : '3d')} className="rounded-full border border-sand px-3 py-1 text-xs font-semibold">
                  {mode === '3d' ? '2D top-down' : '3D'}
                </button>
              )}
            </div>
          </header>
          <div className="relative min-h-0 flex-1">
            {tab === 'graph' && graph && <GraphView data={graph} mode={mode} onPick={setPicked} />}
            {tab === 'pipeline' && (
              <Pipeline
                events={events}
                selected={step}
                onSelect={setStep}
                onReplay={async () => {
                  if (!active) return
                  setEvents([])
                  setTab('pipeline')
                  await api.replay(active)
                  streamEvents(active, true, (event) => setEvents((prev) => [...prev, event]))
                }}
              />
            )}
            {tab === 'report' && report && (
              <ReportView
                report={report}
                nodes={graph?.nodes || []}
                onCite={(id) => {
                  const node = graph?.nodes.find((n) => n.id === id)
                  if (node) setPicked(node)
                }}
              />
            )}
          </div>
          {tab === 'graph' && (
            <footer className="border-t border-sand px-5 py-3">
              <div className="flex items-center gap-3 text-sm">
                <span className="font-semibold">As of</span>
                <input
                  type="range"
                  min={MIN}
                  max={MAX}
                  value={Date.parse(asOf)}
                  onChange={(e) => slide(Number(e.target.value))}
                  className="flex-1 accent-walnut"
                />
                <span className="w-32 text-right font-semibold">{formatAsOf(asOf)}</span>
              </div>
            </footer>
          )}
        </section>
        <SidePanel
          tab={tab}
          node={picked}
          report={report}
          nodes={graph?.nodes || []}
          event={step != null ? events[step] : null}
          sources={sources}
          onCloseNode={() => setPicked(null)}
          onCorrect={async (text) => {
            if (!active) return
            const next = await api.correct(active, text)
            setReport(next)
            setGraph(await api.graph(active, asOf))
            await loadRuns()
          }}
        />
      </main>

      {creating && (
        <div className="fixed inset-0 z-20 grid place-items-center bg-[#2c241c]/40 p-4">
          <form
            className="w-full max-w-lg rounded-3xl bg-card p-6 shadow-desk"
            onSubmit={async (e) => {
              e.preventDefault()
              const created = await api.start(question, newAsOf)
              setCreating(false)
              setEvents([])
              setTab('pipeline')
              await loadRuns()
              setActive(created.id)
            }}
          >
            <h2 className="font-serif text-2xl">New report</h2>
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} className="mt-4 h-28 w-full rounded-2xl border border-sand bg-paper p-3 text-sm" />
            <label className="mt-3 block text-sm">As of
              <input type="date" value={newAsOf} min="2025-10-16" max="2026-10-26" onChange={(e) => setNewAsOf(e.target.value)} className="mt-1 w-full rounded-xl border border-sand bg-paper px-3 py-2" />
            </label>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" onClick={() => setCreating(false)} className="rounded-full px-4 py-2 text-sm">Cancel</button>
              <button className="rounded-full bg-walnut px-4 py-2 text-sm font-semibold text-[#f6efe4]">Run pipeline</button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

function SidePanel({
  tab,
  node,
  report,
  nodes,
  event,
  sources,
  onCloseNode,
  onCorrect,
}: {
  tab: Tab
  node: GraphNode | null
  report: Report | null
  nodes: GraphNode[]
  event: PipelineEvent | null
  sources: SourceRow[]
  onCloseNode: () => void
  onCorrect: (text: string) => Promise<void>
}) {
  if (tab === 'graph' && node) {
    return <ClaimPanel node={node} report={report} onClose={onCloseNode} onCorrect={onCorrect} />
  }
  const rows = rowsFor(event, sources)
  return (
    <aside className="flex h-full w-[340px] shrink-0 flex-col border-l border-sand bg-card">
      <div className="px-4 py-3">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-bark/50">
          {tab === 'pipeline' ? 'Job' : tab === 'report' ? 'Report' : 'Inspect'}
        </p>
      </div>
      <div className="flex-1 overflow-auto px-4 pb-4 text-sm">
        {tab === 'graph' && <p className="text-bark/70">Click a node to read its quote, source, and checks.</p>}
        {tab === 'report' && (
          <ol className="space-y-2 text-bark/80">
            <li>Findings, with a link for each source</li>
            <li>Scenario, the migration math from those figures</li>
            <li>Still open, anything the filings do not cover</li>
          </ol>
        )}
        {tab === 'pipeline' && !event && <p className="text-bark/70">Click a lane or a step.</p>}
        {tab === 'pipeline' && event && (
          <div>
            <p className="font-semibold text-walnut">{event.agent} · {event.kind}</p>
            <p className="mt-2 leading-relaxed text-ink">{event.message}</p>
            {explain(event, report, nodes).map((item) => (
              <div key={item.id} className="mt-3 rounded-xl bg-paper px-3 py-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-bark/50">{item.kind}</p>
                <p className="mt-1 leading-relaxed">{item.text}</p>
                {item.why.map((reason) => (
                  <p key={reason} className="mt-1 text-clay">{reason}</p>
                ))}
              </div>
            ))}
            {rows.length > 0 && (
              <ul className="mt-4 space-y-3">
                {rows.map((row) => (
                  <li key={row.id}>
                    <p className="font-semibold">{row.title}</p>
                    <p className="text-xs uppercase tracking-wide text-bark/50">{row.decision || row.status || 'checked'}{row.fetch_status ? ` · ${row.fetch_status}` : ''}</p>
                    {row.url && <a className="block truncate text-walnut underline" href={row.url} target="_blank" rel="noreferrer">{row.url}</a>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}

function explain(event: PipelineEvent, report: Report | null, nodes: GraphNode[]): { id: string; kind: string; text: string; why: string[] }[] {
  const payload = event.payload || {}
  const sentences = report?.sentences || []
  const byId = new Map(nodes.map((node) => [node.id, node]))
  const packed = payload.failures || payload.unsupported
  if (Array.isArray(packed) && packed.length && typeof packed[0] === 'object') {
    return (packed as { id: string; text: string; why?: string[] }[]).map((item) => ({
      id: item.id,
      kind: event.kind === 'retry' ? 'Sent back' : 'Left unsupported',
      text: item.text,
      why: item.why?.length ? item.why : ['Shown because this sentence failed a check and stayed in the report.'],
    }))
  }
  const ids = Array.isArray(payload.ids) ? payload.ids as string[] : []
  if (ids.length || event.agent === 'Verifier') {
    const chosen = ids.length ? sentences.filter((sentence) => ids.includes(sentence.id)) : sentences.filter((sentence) => sentence.status !== 'supported')
    return chosen.map((sentence) => ({
      id: sentence.id,
      kind: sentence.status,
      text: sentence.text,
      why: (sentence.checks || []).filter((check) => check.passed === false).map((check) => check.detail).concat(
        sentence.status === 'supported' ? ['Every code check passed, so the writer kept it.'] : [],
      ),
    }))
  }
  if (event.agent === 'Writer') {
    const shown = event.kind === 'revise' ? sentences.filter((sentence) => sentence.status !== 'supported') : sentences
    return shown.map((sentence) => {
      const sources = sentence.claim_ids.map((id) => byId.get(id)?.label || id).join(', ')
      return {
        id: sentence.id,
        kind: sentence.status,
        text: sentence.text,
        why: [
          sources ? `Written from ${sources}.` : 'No claim id on this sentence.',
          sentence.status === 'supported' ? 'Kept because the cited claim is on or before the as-of date and the numbers match the source.' : 'Kept visible because a check failed. It is not treated as supported.',
        ],
      }
    })
  }
  if (event.agent === 'Extractor') {
    return nodes.filter((node) => node.type === 'claim' || node.type === 'user_assertion').map((node) => ({
      id: node.id,
      kind: node.company || 'claim',
      text: node.title || node.label,
      why: [`Pulled from ${node.source_title || node.label}${node.date ? ` (${node.date})` : ''}. It is on the graph because a report sentence cites it.`],
    }))
  }
  if (event.agent === 'Linker') {
    return nodes.filter((node) => node.contradiction || node.type === 'claim').slice(0, 12).map((node) => ({
      id: node.id,
      kind: node.contradiction ? 'Contradiction' : 'Attached to source',
      text: node.label,
      why: [node.contradiction || `Linked to ${node.source_title || 'its document'} so the report can cite it.`],
    }))
  }
  if (event.agent === 'Orchestrator') {
    return [{
      id: `orch-${event.kind}`,
      kind: event.kind,
      text: payload.question ? String(payload.question) : (report?.question || event.message),
      why: [
        payload.as_of ? `As of ${payload.as_of}. Later documents stay off the graph.` : `Run status ${report?.status || 'saved'}.`,
        payload.latency_ms != null ? `Finished in ${payload.latency_ms} ms. ${payload.sentences ?? sentences.length} sentences, ${payload.unsupported ?? 0} unsupported.` : 'This step only records the handoff. The sentences are in the writer and verifier steps.',
      ],
    }]
  }
  if (event.agent === 'Collector' && event.kind === 'chunk') {
    return [{
      id: 'chunk',
      kind: 'Chunks',
      text: event.message,
      why: ['Each document is split so the extractor can quote a passage instead of the whole filing.'],
    }]
  }
  return []
}

function rowsFor(event: PipelineEvent | null, sources: SourceRow[]): SourceRow[] {
  if (!event) return []
  const payload = event.payload || {}
  if (Array.isArray(payload.checked)) return payload.checked as SourceRow[]
  if (Array.isArray(payload.urls)) {
    return (payload.urls as { id: string; title: string; url?: string; published_at?: string }[]).map((row) => ({
      ...row,
      decision: 'keep',
    }))
  }
  if (event.agent === 'Extractor' || event.agent === 'Collector') return sources
  return []
}
