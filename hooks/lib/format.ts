// What each pane tab says, as plain data: a list of blocks that register.tsx
// turns into elements. Pure, so every state of every tab is unit-testable.

import type { Failure, Session } from './session'

export type Block = {
  kind: 'title' | 'text' | 'dim' | 'good' | 'bad' | 'warn' | 'code' | 'markdown'
  text: string
}

export const NO_SESSION = 'No active session. Run /mockinterview:interview'

const MAX_CODE = 400

const clip = (s: string): string =>
  s.length <= MAX_CODE ? s : `${s.slice(0, MAX_CODE)}... (${s.length} characters)`

function header(s: Session): Block {
  const level = s.level === null ? '' : `, ${s.level}`
  const total = Math.max(s.roundsTotal, 1)
  return {
    kind: 'dim',
    text: `${s.mode}${level}, round ${s.round + 1} of ${total}, ${s.state}`,
  }
}

/** Problem tab. `problemMd` is `.mockinterview/work/PROBLEM.md`, or null. */
export function problemBlocks(s: Session | null, problemMd: string | null): Block[] {
  if (s === null) return [{ kind: 'dim', text: NO_SESSION }]
  const total = Math.max(s.roundsTotal, 1)
  const out: Block[] = [header(s)]

  if (s.state === 'drawn') {
    // Interview mode: the title and id stay hidden until the engineer says go.
    out.push({ kind: 'title', text: `Round ${s.round + 1} of ${total} - say go when ready` })
    if (s.level !== null) out.push({ kind: 'text', text: `Level: ${s.level}` })
    const title = s.mode === 'interview' ? null : (s.current?.title ?? null)
    if (title !== null) out.push({ kind: 'text', text: title })
    return out
  }
  if (s.state === 'running') {
    if (problemMd !== null && problemMd.trim() !== '') {
      out.push({ kind: 'markdown', text: problemMd })
    } else {
      out.push({
        kind: 'warn',
        text: 'The problem statement is not there yet: .mockinterview/work/PROBLEM.md',
      })
    }
    return out
  }
  if (s.state === 'finished') {
    out.push({ kind: 'text', text: 'All rounds are finished. Waiting for the scorecard.' })
  } else if (s.state === 'scored') {
    out.push({ kind: 'text', text: 'This session is scored. See the Scorecard tab.' })
  } else if (s.state === 'abandoned') {
    out.push({ kind: 'dim', text: 'This session was abandoned.' })
  } else {
    out.push({ kind: 'dim', text: NO_SESSION })
  }
  return out
}

function failureBlocks(f: Failure): Block[] {
  const out: Block[] = [{ kind: 'bad', text: `FAIL ${f.name} [${f.category}]` }]
  if (f.args !== undefined) out.push({ kind: 'code', text: clip(`args:     ${f.args}`) })
  if (f.expected !== undefined) out.push({ kind: 'code', text: clip(`expected: ${f.expected}`) })
  if (f.got !== undefined) out.push({ kind: 'code', text: clip(`got:      ${f.got}`) })
  return out
}

/** Results tab: the last test run of the current round. */
export function resultsBlocks(s: Session | null): Block[] {
  if (s === null) return [{ kind: 'dim', text: NO_SESSION }]
  const out: Block[] = [header(s)]
  const cur = s.current
  if (cur !== null && cur.hintsUsed.length > 0) {
    const used = cur.hintsUsed.map(h => `${h.rung} (${h.cost > 0 ? '-' : ''}${h.cost})`)
    out.push({ kind: 'text', text: `Hints used: ${used.join(', ')}` })
  }
  const run = cur?.lastRun ?? null
  if (run === null) {
    const isCode = cur === null || cur.type === 'live-coding'
    out.push({
      kind: 'dim',
      text: isCode
        ? 'No test run yet. Ask the interviewer to run your tests.'
        : 'Design round: no tests. The interviewer runs the estimate and design checks.',
    })
    return out
  }
  const isPass = run.failed === 0 && run.total > 0
  out.push({
    kind: isPass ? 'good' : 'bad',
    text: `${run.passed} of ${run.total} cases pass`,
  })
  for (const [category, ratio] of Object.entries(run.byCategory)) {
    out.push({ kind: 'text', text: `${category}: ${ratio}` })
  }
  for (const line of run.perfLines) out.push({ kind: 'text', text: `perf ${line}` })
  const shown = run.failures.filter(f => f.shown)
  for (const f of shown) out.push(...failureBlocks(f))
  const hidden = run.failures.length - shown.length
  if (hidden > 0) {
    out.push({
      kind: 'dim',
      text: `${hidden} failing ${hidden === 1 ? 'case is' : 'cases are'} not shown during an interview.`,
    })
  }
  return out
}

/** Scorecard tab. */
export function scorecardBlocks(s: Session | null): Block[] {
  if (s === null) return [{ kind: 'dim', text: NO_SESSION }]
  if (s.state !== 'scored' || s.scorecard === null) {
    return [header(s), { kind: 'dim', text: 'Not scored yet' }]
  }
  const card = s.scorecard
  const out: Block[] = [header(s), { kind: 'title', text: `Score: ${card.total.toFixed(1)} of 100` }]
  if (card.reading !== '') out.push({ kind: 'text', text: card.reading })
  for (const round of card.rounds) {
    const penalty = round.penalty > 0 ? `, hint penalty -${round.penalty}` : ''
    out.push({ kind: 'title', text: `${round.problem}: ${round.score.toFixed(1)}${penalty}` })
    for (const [dimension, rating] of Object.entries(round.ratings)) {
      const evidence = round.evidence[dimension]
      const note = evidence === undefined || evidence === '' ? '' : ` - ${evidence}`
      out.push({ kind: 'text', text: `${dimension}: ${rating} of 4${note}` })
    }
  }
  if (card.topGap !== null && card.topGap !== '') {
    out.push({ kind: 'warn', text: `Top gap: ${card.topGap}` })
  }
  return out
}
