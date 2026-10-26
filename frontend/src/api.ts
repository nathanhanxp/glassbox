import type { GraphData, PipelineEvent, Report, RunSummary, SourceRow } from './types'

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const api = {
  runs: () => fetch('/api/runs').then((r) => json<RunSummary[]>(r)),
  report: (id: string) => fetch(`/api/runs/${id}/report`).then((r) => json<Report>(r)),
  graph: (id: string, asOf: string) =>
    fetch(`/api/runs/${id}/graph?as_of=${asOf}`).then((r) => json<GraphData>(r)),
  start: (question: string, asOf: string) =>
    fetch('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, as_of: asOf }),
    }).then((r) => json<{ id: string }>(r)),
  correct: (id: string, text: string) =>
    fetch(`/api/runs/${id}/corrections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then((r) => json<Report>(r)),
  replay: (id: string) => fetch(`/api/runs/${id}/replay`, { method: 'POST' }).then((r) => json(r)),
  sources: (id: string) => fetch(`/api/runs/${id}/sources`).then((r) => json<SourceRow[]>(r)),
}

export function streamEvents(id: string, replay: boolean, onEvent: (event: PipelineEvent) => void) {
  const source = new EventSource(`/api/runs/${id}/events?replay=${replay ? 1 : 0}`)
  source.onmessage = (message) => {
    const event = JSON.parse(message.data) as PipelineEvent
    onEvent(event)
    if (replay && event.kind === 'done' && event.message === 'Replay finished.') source.close()
  }
  return () => source.close()
}
