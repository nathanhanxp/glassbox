import demo from './demoRun.json'
import type { GraphData, PipelineEvent, Report, RunSummary, SourceRow } from './types'

const saved = demo as {
  run: RunSummary
  report: Report
  graph: GraphData
  events: PipelineEvent[]
  sources: SourceRow[]
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function liveOrSaved<T>(request: Promise<T>, fallback: T): Promise<T> {
  try {
    return await request
  } catch {
    return fallback
  }
}

export const api = {
  runs: () => liveOrSaved(fetch('/api/runs').then((r) => json<RunSummary[]>(r)), [saved.run]),
  report: (id: string) => liveOrSaved(fetch(`/api/runs/${id}/report`).then((r) => json<Report>(r)), saved.report),
  graph: (id: string, asOf: string) =>
    liveOrSaved(fetch(`/api/runs/${id}/graph?as_of=${asOf}`).then((r) => json<GraphData>(r)), saved.graph),
  start: (question: string, asOf: string) =>
    liveOrSaved(
      fetch('/api/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, as_of: asOf }),
      }).then((r) => json<{ id: string }>(r)),
      { id: saved.run.id },
    ),
  correct: (id: string, text: string) =>
    fetch(`/api/runs/${id}/corrections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then((r) => json<Report>(r)),
  replay: (id: string) => fetch(`/api/runs/${id}/replay`, { method: 'POST' }).then((r) => json(r)),
  sources: (id: string) => liveOrSaved(fetch(`/api/runs/${id}/sources`).then((r) => json<SourceRow[]>(r)), saved.sources),
}

export function streamEvents(id: string, replay: boolean, onEvent: (event: PipelineEvent) => void) {
  let received = false
  const source = new EventSource(`/api/runs/${id}/events?replay=${replay ? 1 : 0}`)
  source.onmessage = (message) => {
    received = true
    const event = JSON.parse(message.data) as PipelineEvent
    onEvent(event)
    if (replay && event.kind === 'done' && event.message === 'Replay finished.') source.close()
  }
  source.onerror = () => {
    source.close()
    if (received) return
    saved.events.forEach(onEvent)
  }
  return () => source.close()
}
