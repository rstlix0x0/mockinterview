import { expect, test } from 'claude-code/testing'

import {
  NO_SESSION,
  problemBlocks,
  resultsBlocks,
  scorecardBlocks,
  type Block,
} from '../../hooks/lib/format'
import { parseSession } from '../../hooks/lib/session'

function session(over: Record<string, unknown> = {}, current: Record<string, unknown> | null = {}) {
  return parseSession(
    JSON.stringify({
      session_id: 's-1',
      mode: 'interview',
      level: 'senior',
      state: 'running',
      round: 0,
      rounds_total: 2,
      current:
        current === null
          ? null
          : {
              problem: 'lc-c01-lru-cache',
              type: 'live-coding',
              limit_seconds: 1800,
              title: 'LRU Cache',
              started_at: '2026-10-21T09:31:12Z',
              hints_used: [],
              last_run: null,
              ...current,
            },
      scorecard: null,
      ...over,
    }),
  )
}

const texts = (blocks: Block[]): string => blocks.map(b => b.text).join('\n')

test('Problem tab: no session', async () => {
  expect(problemBlocks(null, null)).toEqual([{ kind: 'dim', text: NO_SESSION }])
  expect(resultsBlocks(null)[0]?.text).toBe(NO_SESSION)
  expect(scorecardBlocks(null)[0]?.text).toBe(NO_SESSION)
})

test('Problem tab: interview round before go shows only round and level', async () => {
  const s = session({ state: 'drawn' }, { title: 'LRU Cache' })
  const all = texts(problemBlocks(s, '# LRU Cache\nSECRET STATEMENT'))
  expect(all).toContain('Round 1 of 2 - say go when ready')
  expect(all).toContain('Level: senior')
  // nothing that identifies the problem
  expect(all).not.toContain('LRU')
  expect(all).not.toContain('lru')
  expect(all).not.toContain('SECRET')
  expect(all).not.toContain('lc-c01')
})

test('Problem tab: practice round before go may show the title', async () => {
  const s = session({ state: 'drawn', mode: 'practice' }, { title: 'LRU Cache' })
  expect(texts(problemBlocks(s, null))).toContain('LRU Cache')
})

test('Problem tab: running shows PROBLEM.md as Markdown', async () => {
  const blocks = problemBlocks(session(), '# LRU Cache\nDesign a cache.')
  const md = blocks.find(b => b.kind === 'markdown')
  expect(md?.text).toBe('# LRU Cache\nDesign a cache.')
})

test('Problem tab: running without PROBLEM.md says so', async () => {
  const blocks = problemBlocks(session(), null)
  expect(blocks.some(b => b.kind === 'markdown')).toBe(false)
  expect(texts(blocks)).toContain('PROBLEM.md')
  expect(texts(problemBlocks(session(), '   '))).toContain('PROBLEM.md')
})

test('Problem tab: later rounds count from one', async () => {
  const s = session({ state: 'drawn', round: 1 })
  expect(texts(problemBlocks(s, null))).toContain('Round 2 of 2 - say go when ready')
})

test('Problem tab: finished, scored and abandoned', async () => {
  expect(texts(problemBlocks(session({ state: 'finished' }), null))).toContain('Waiting for the scorecard')
  expect(texts(problemBlocks(session({ state: 'scored' }), null))).toContain('Scorecard tab')
  expect(texts(problemBlocks(session({ state: 'abandoned' }), null))).toContain('abandoned')
})

test('Results tab: no run yet, code and design rounds', async () => {
  expect(texts(resultsBlocks(session()))).toContain('No test run yet')
  const design = session({}, { type: 'system-design' })
  expect(texts(resultsBlocks(design))).toContain('Design round: no tests')
})

test('Results tab: counts, categories, perf, shown and hidden failures, hints', async () => {
  const s = session(
    {},
    {
      hints_used: [
        { rung: 'H0', cost: 0 },
        { rung: 'H1', cost: 5 },
      ],
      last_run: {
        passed: 15,
        failed: 2,
        total: 17,
        by_category: { visible: '3/3', edge: '3/4', hidden: '6/7' },
        perf: { ran: true, ok: true, lines: ['n=20000 120 ms (limit 3000 ms) ok'] },
        failures: [
          { name: 'edge-dup', category: 'edge', shown: true, args: '{"nums":[3,3]}', expected: '[0,1]', got: '[]' },
          { name: 'h1', category: 'hidden', shown: false },
        ],
      },
    },
  )
  const blocks = resultsBlocks(s)
  const all = texts(blocks)
  expect(all).toContain('15 of 17 cases pass')
  expect(blocks.find(b => b.text.startsWith('15 of 17'))?.kind).toBe('bad')
  expect(all).toContain('visible: 3/3')
  expect(all).toContain('hidden: 6/7')
  expect(all).toContain('perf n=20000')
  expect(all).toContain('FAIL edge-dup [edge]')
  expect(all).toContain('expected: [0,1]')
  expect(all).toContain('Hints used: H0 (0), H1 (-5)')
  expect(all).toContain('1 failing case is not shown during an interview.')
  expect(all).not.toContain('FAIL h1')
})

test('Results tab: a clean run is good', async () => {
  const s = session({}, { last_run: { passed: 4, failed: 0, total: 4, by_category: { visible: '4/4' }, failures: [] } })
  const blocks = resultsBlocks(s)
  expect(blocks.find(b => b.text.startsWith('4 of 4'))?.kind).toBe('good')
})

test('Results tab: long failure values are clipped', async () => {
  const long = 'x'.repeat(5000)
  const s = session(
    {},
    {
      last_run: {
        passed: 0,
        failed: 1,
        total: 1,
        by_category: { visible: '0/1' },
        failures: [{ name: 'big', category: 'visible', shown: true, args: long, expected: '1', got: '2' }],
      },
    },
  )
  const code = resultsBlocks(s).find(b => b.kind === 'code' && b.text.startsWith('args:'))
  expect((code?.text.length ?? 0) < 600).toBe(true)
  expect(code?.text).toContain('(5010 characters)')
})

test('Scorecard tab: not scored, then scored', async () => {
  expect(texts(scorecardBlocks(session()))).toContain('Not scored yet')
  expect(texts(scorecardBlocks(session({ state: 'scored' })))).toContain('Not scored yet')
  const s = session(
    {
      state: 'scored',
      scorecard: {
        total: 78.5,
        reading: '70 to 84: close',
        top_gap: 'testing before coding',
        rounds: [
          {
            problem: 'lc-c01-lru-cache',
            score: 80,
            penalty: 5,
            ratings: { framing: 3, approach: 4 },
            evidence: { framing: 'asked about capacity zero' },
          },
        ],
      },
    },
    {},
  )
  const all = texts(scorecardBlocks(s))
  expect(all).toContain('Score: 78.5 of 100')
  expect(all).toContain('70 to 84: close')
  expect(all).toContain('lc-c01-lru-cache: 80.0, hint penalty -5')
  expect(all).toContain('framing: 3 of 4 - asked about capacity zero')
  expect(all).toContain('approach: 4 of 4')
  expect(all).toContain('Top gap: testing before coding')
})
