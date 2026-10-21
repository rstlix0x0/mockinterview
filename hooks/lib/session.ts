// Pure helpers for reading `.mockinterview/session.json` (written only by the
// runner, see docs/runner.md). Nothing here touches the engine, so it can be
// unit-tested and reused by the guard, the panes and the status line.

export type HintUse = { rung: string; cost: number }

export type Failure = {
  name: string
  category: string
  shown: boolean
  args?: string
  expected?: string
  got?: string
}

export type LastRun = {
  passed: number
  failed: number
  total: number
  byCategory: Record<string, string>
  perfLines: string[]
  failures: Failure[]
}

export type Current = {
  problem: string
  type: string
  limitSeconds: number | null
  title: string | null
  startedAt: string | null
  hintsUsed: HintUse[]
  lastRun: LastRun | null
}

export type RoundScore = {
  problem: string
  score: number
  penalty: number
  ratings: Record<string, number>
  evidence: Record<string, string>
}

export type Scorecard = {
  total: number
  reading: string
  rounds: RoundScore[]
  topGap: string | null
}

export type Session = {
  id: string
  mode: string
  level: string | null
  state: string
  round: number
  roundsTotal: number
  current: Current | null
  scorecard: Scorecard | null
}

type Obj = Record<string, unknown>

const isObj = (v: unknown): v is Obj =>
  typeof v === 'object' && v !== null && !Array.isArray(v)
const str = (v: unknown): string | null => (typeof v === 'string' ? v : null)
const num = (v: unknown): number | null =>
  typeof v === 'number' && Number.isFinite(v) ? v : null
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : [])

function strMap(v: unknown): Record<string, string> {
  const out: Record<string, string> = {}
  if (isObj(v)) for (const [k, x] of Object.entries(v)) out[k] = String(x)
  return out
}

function numMap(v: unknown): Record<string, number> {
  const out: Record<string, number> = {}
  if (isObj(v)) {
    for (const [k, x] of Object.entries(v)) {
      const n = num(x)
      if (n !== null) out[k] = n
    }
  }
  return out
}

function parseLastRun(v: unknown): LastRun | null {
  if (!isObj(v)) return null
  const perf = isObj(v.perf) ? arr(v.perf.lines).map(String) : []
  const failures: Failure[] = []
  for (const f of arr(v.failures)) {
    if (!isObj(f)) continue
    const failure: Failure = {
      name: str(f.name) ?? '?',
      category: str(f.category) ?? '?',
      shown: f.shown === true,
    }
    // A hidden case never carries details (runner contract); drop them anyway.
    if (failure.shown) {
      const args = str(f.args)
      const expected = str(f.expected)
      const got = str(f.got)
      if (args !== null) failure.args = args
      if (expected !== null) failure.expected = expected
      if (got !== null) failure.got = got
    }
    failures.push(failure)
  }
  return {
    passed: num(v.passed) ?? 0,
    failed: num(v.failed) ?? 0,
    total: num(v.total) ?? 0,
    byCategory: strMap(v.by_category),
    perfLines: perf,
    failures,
  }
}

function parseCurrent(v: unknown): Current | null {
  if (!isObj(v)) return null
  const minutes = num(v.time_minutes)
  const hints: HintUse[] = []
  for (const h of arr(v.hints_used)) {
    if (isObj(h)) hints.push({ rung: str(h.rung) ?? '?', cost: num(h.cost) ?? 0 })
  }
  return {
    problem: str(v.problem) ?? '',
    type: str(v.type) ?? '',
    limitSeconds: num(v.limit_seconds) ?? (minutes !== null ? minutes * 60 : null),
    title: str(v.title),
    startedAt: str(v.started_at),
    hintsUsed: hints,
    lastRun: parseLastRun(v.last_run),
  }
}

function parseScorecard(v: unknown): Scorecard | null {
  if (!isObj(v)) return null
  const rounds: RoundScore[] = []
  for (const r of arr(v.rounds)) {
    if (!isObj(r)) continue
    rounds.push({
      problem: str(r.problem) ?? '?',
      score: num(r.score) ?? 0,
      penalty: num(r.penalty) ?? 0,
      ratings: numMap(r.ratings),
      evidence: strMap(r.evidence),
    })
  }
  return {
    total: num(v.total) ?? 0,
    reading: str(v.reading) ?? '',
    rounds,
    topGap: str(v.top_gap),
  }
}

/**
 * Parses the session file. Returns null for a missing, empty, malformed or
 * unrecognisable file: every caller treats null as "no active session".
 */
export function parseSession(text: string | null | undefined): Session | null {
  if (typeof text !== 'string' || text.trim() === '') return null
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    return null
  }
  if (!isObj(raw)) return null
  const state = str(raw.state)
  const mode = str(raw.mode)
  if (state === null || mode === null) return null
  const loop = arr(raw.loop)
  return {
    id: str(raw.session_id) ?? '',
    mode,
    level: str(raw.level),
    state,
    round: num(raw.round) ?? 0,
    roundsTotal: num(raw.rounds_total) ?? loop.length,
    current: parseCurrent(raw.current),
    scorecard: parseScorecard(raw.scorecard),
  }
}

/** A round is chosen (`drawn`) or the clock is on (`running`). */
export function isActive(s: Session | null): s is Session {
  return s !== null && (s.state === 'drawn' || s.state === 'running')
}

/** The state in which hidden material must stay hidden. */
export function isInterviewLocked(s: Session | null): s is Session {
  return isActive(s) && s.mode === 'interview'
}

/**
 * Seconds left in the running round: negative past the limit, null when the
 * clock is not running or the file lacks a usable start time or limit.
 */
export function remainingSeconds(s: Session | null, nowMs: number): number | null {
  if (s === null || s.state !== 'running' || s.current === null) return null
  const { startedAt, limitSeconds } = s.current
  if (startedAt === null || limitSeconds === null || limitSeconds <= 0) return null
  const started = Date.parse(startedAt)
  if (!Number.isFinite(started)) return null
  return limitSeconds - (nowMs - started) / 1000
}

/** mm:ss, rounded up so the last second shows 00:01; never negative. */
export function formatClock(seconds: number): string {
  const total = Math.max(0, Math.ceil(seconds))
  const mm = Math.floor(total / 60)
  const ss = total % 60
  return `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`
}

/** The status-line text, or undefined (clears the entry) when nothing runs. */
export function statusText(s: Session | null, nowMs: number): string | undefined {
  if (s === null || s.state !== 'running') return undefined
  const label = `mockinterview ${s.round + 1}/${Math.max(s.roundsTotal, 1)}`
  const left = remainingSeconds(s, nowMs)
  if (left === null) return `${label} running`
  if (left <= 0) return `${label} time up`
  return `${label} ${formatClock(left)} left`
}
