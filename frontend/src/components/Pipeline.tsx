import type { PipelineEvent } from '../types'

const LANES = ['Orchestrator', 'Collector', 'Extractor', 'Linker', 'Writer', 'Verifier']

export function Pipeline({
  events,
  selected,
  onSelect,
  onReplay,
}: {
  events: PipelineEvent[]
  selected: number | null
  onSelect: (index: number) => void
  onReplay: () => void
}) {
  const width = 920
  const height = 420
  const left = 140
  const top = 48
  const laneH = 58
  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-4 flex items-center justify-between">
        <p className="font-serif text-2xl text-ink">Agent pipeline</p>
        <button onClick={onReplay} className="rounded-full border border-sand bg-card px-4 py-2 text-sm font-semibold text-walnut">
          Replay saved run
        </button>
      </div>
      <div className="stage relative flex-1 overflow-hidden rounded-3xl">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
          {LANES.map((lane, i) => (
            <g key={lane} onClick={() => {
              const index = events.findIndex((event) => event.agent === lane)
              if (index >= 0) onSelect(index)
            }} style={{ cursor: 'pointer' }}>
              <text x="16" y={top + i * laneH + 6} fill="#e7d7c2" fontSize="13" fontFamily="Source Sans 3">
                {lane}
              </text>
              <line x1={left} x2={width - 24} y1={top + i * laneH} y2={top + i * laneH} stroke="#6b5344" strokeWidth="1" />
            </g>
          ))}
          {events.map((event, i) => {
            const lane = Math.max(0, LANES.indexOf(event.agent))
            const x = left + 28 + i * Math.min(36, (width - left - 80) / Math.max(events.length, 1))
            const y = top + lane * laneH
            const fill = selected === i ? '#f6efe4' : event.kind === 'skip' || event.kind === 'retry' ? '#e08a45' : '#e0c48a'
            return (
              <g key={`${event.id ?? i}-${event.kind}`} onClick={() => onSelect(i)} style={{ cursor: 'pointer' }}>
                <circle cx={x} cy={y} r={selected === i ? 8 : 6} fill={fill} />
                <text x={x + 8} y={y - 10} fill="#f3e6d4" fontSize="10" fontFamily="Source Sans 3">
                  {event.kind}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}
