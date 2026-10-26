export type RunSummary = {
  id: string
  title: string
  question: string
  as_of: string
  status: string
  created_at: string
  unsupported: number
}

export type Check = { name: string; passed: boolean; detail: string; skipped?: boolean }

export type Sentence = {
  id: string
  text: string
  quote: string
  claim_ids: string[]
  status: string
  checks: Check[]
  attempt: number
  hedged: boolean
  derived: boolean
}

export type Finance = {
  knowable: boolean
  reason?: string
  balance?: { balance_billion: number; label: string; source: string; source_id: string }
  also_knowable?: { balance_billion: number; label: string; source: string }[]
  spread?: number
  spread_label?: string
  spread_note?: string
  formula?: string
  rows?: { migration: number; migrated_billion: number; annual_revenue_at_risk: number }[]
  recompute?: {
    june_sweep_billion: number
    june_sweep_source: string
    june_short_credits_billion: number
    june_short_source: string
    sept_sweep_billion: number
    sept_sweep_source: string
    sept_short_credits_billion: number
    sept_short_source: string
    june_ex_short_billion: number
    sept_ex_short_billion: number
    decline_billion: number
    note: string
  } | null
  nim_context?: { value: string; source: string; used_in_scenario: boolean }
}

export type Report = {
  id: string
  title: string
  question: string
  as_of: string
  status: string
  summary: string
  sentences: Sentence[]
  gaps: string[]
  finance: Finance
  metrics: { latency_ms: number; llm_calls: number; tokens: number; unsupported: number; mode: string; documents: number; claims: number }
  orchestrator: string
  created_at?: string
  corrections?: { id: number; text: string; created_at: string }[]
}

export type GraphNode = {
  id: string
  type: string
  label: string
  detail?: string
  title?: string
  quote?: string
  company?: string
  tier?: string
  date?: string | null
  url?: string
  chunk_id?: string
  doc_id?: string
  source_title?: string
  supported?: boolean
  secondary?: boolean
  sentence_ids?: string[]
  contradiction?: string
  scope?: string
  x: number
  y: number
  z: number
}

export type GraphLink = { source: string; target: string; type: string; note?: string }

export type GraphData = { as_of: string; nodes: GraphNode[]; links: GraphLink[] }

export type PipelineEvent = {
  id?: number
  agent: string
  kind: string
  message: string
  ts?: string
  payload?: Record<string, unknown>
}

export type SourceRow = {
  id: string
  job?: string
  title: string
  url?: string
  published_at?: string
  decision?: string
  status?: string
  fetch_status?: string
  fetch_reason?: string
}
