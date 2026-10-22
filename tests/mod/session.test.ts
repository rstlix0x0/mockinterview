import { expect, test } from 'claude-code/testing'

import {
  formatClock,
  isActive,
  isInterviewLocked,
  parseSession,
  remainingSeconds,
  statusText,
} from '../../hooks/lib/session'

const T0 = Date.parse('2026-10-21T09:31:12Z')

function file(over: Record<string, unknown> = {}, current: Record<string, unknown> = {}): string {
  return JSON.stringify({
    schema: 1,
    session_id: 's-1',
    mode: 'interview',
    level: 'senior',
    state: 'running',
    round: 0,
    rounds_total: 3,
    loop: [{}, {}, {}],
    current: {
      problem: 'lc-c01-lru-cache',
      type: 'live-coding',
      time_minutes: 30,
      limit_seconds: 1800,
      title: 'LRU Cache',
      started_at: '2026-10-21T09:31:12Z',
      hints_used: [{ rung: 'H1', cost: 5 }],
      last_run: null,
      ...current,
    },
    scorecard: null,
    ...over,
  })
}

test('parseSession reads a valid session file', async () => {
  const s = parseSession(file())
  expect(s?.id).toBe('s-1')
  expect(s?.mode).toBe('interview')
  expect(s?.level).toBe('senior')
  expect(s?.state).toBe('running')
  expect(s?.roundsTotal).toBe(3)
  expect(s?.current?.limitSeconds).toBe(1800)
  expect(s?.current?.hintsUsed).toEqual([{ rung: 'H1', cost: 5 }])
})

test('parseSession returns null for missing, empty and malformed input', async () => {
  expect(parseSession(null)).toBeNull()
  expect(parseSession(undefined)).toBeNull()
  expect(parseSession('')).toBeNull()
  expect(parseSession('   ')).toBeNull()
  expect(parseSession('{not json')).toBeNull()
  expect(parseSession('[]')).toBeNull()
  expect(parseSession('"text"')).toBeNull()
  expect(parseSession('{}')).toBeNull()
  expect(parseSession('{"state": "running"}')).toBeNull()
  expect(parseSession('{"mode": "interview"}')).toBeNull()
})

test('parseSession tolerates wrong field types without throwing', async () => {
  const s = parseSession(
    JSON.stringify({ mode: 'practice', state: 'drawn', round: 'x', current: 5, scorecard: 'no', loop: 7 }),
  )
  expect(s?.round).toBe(0)
  expect(s?.roundsTotal).toBe(0)
  expect(s?.current).toBeNull()
  expect(s?.scorecard).toBeNull()
})

test('parseSession reads the solution language, null when absent', async () => {
  const s = parseSession(file({ language: 'python', solution: '.mockinterview/work/solution.py' }))
  expect(s?.language).toBe('python')
  expect(s?.solution).toBe('.mockinterview/work/solution.py')
  const old = parseSession(file())
  expect(old?.language).toBeNull()
  expect(old?.solution).toBeNull()
})

test('limit_seconds falls back to time_minutes', async () => {
  const s = parseSession(file({}, { limit_seconds: undefined, time_minutes: 20 }))
  expect(s?.current?.limitSeconds).toBe(1200)
})

test('a hidden failing case never keeps details', async () => {
  const s = parseSession(
    file(
      {},
      {
        last_run: {
          passed: 1,
          failed: 2,
          total: 3,
          by_category: { visible: '1/1', hidden: '0/2' },
          failures: [
            { name: 'a', category: 'visible', shown: true, args: '1', expected: '2', got: '3' },
            { name: 'b', category: 'hidden', shown: false, args: 'SECRET', expected: 'SECRET', got: 'x' },
          ],
        },
      },
    ),
  )
  const failures = s?.current?.lastRun?.failures ?? []
  expect(failures).toHaveLength(2)
  expect(failures[0]?.args).toBe('1')
  expect(failures[1]?.args).toBeUndefined()
  expect(failures[1]?.expected).toBeUndefined()
})

test('isActive and isInterviewLocked follow state and mode', async () => {
  expect(isActive(parseSession(file({ state: 'drawn' })))).toBe(true)
  expect(isActive(parseSession(file({ state: 'running' })))).toBe(true)
  expect(isActive(parseSession(file({ state: 'finished' })))).toBe(false)
  expect(isActive(parseSession(file({ state: 'scored' })))).toBe(false)
  expect(isActive(null)).toBe(false)
  expect(isInterviewLocked(parseSession(file({ state: 'drawn' })))).toBe(true)
  expect(isInterviewLocked(parseSession(file({ state: 'running' })))).toBe(true)
  expect(isInterviewLocked(parseSession(file({ state: 'running', mode: 'practice' })))).toBe(false)
  expect(isInterviewLocked(parseSession(file({ state: 'finished' })))).toBe(false)
})

test('remainingSeconds: before start, running, past the limit', async () => {
  // not started: state drawn, or running without a start time
  expect(remainingSeconds(parseSession(file({ state: 'drawn' })), T0)).toBeNull()
  expect(remainingSeconds(parseSession(file({}, { started_at: null })), T0)).toBeNull()
  // running
  expect(remainingSeconds(parseSession(file()), T0)).toBe(1800)
  expect(remainingSeconds(parseSession(file()), T0 + 90_000)).toBe(1710)
  // past the limit is negative
  const late = remainingSeconds(parseSession(file()), T0 + 1_900_000)
  expect(late).toBe(-100)
  // unusable inputs
  expect(remainingSeconds(parseSession(file({}, { started_at: 'nonsense' })), T0)).toBeNull()
  expect(remainingSeconds(parseSession(file({}, { limit_seconds: 0, time_minutes: 0 })), T0)).toBeNull()
  expect(remainingSeconds(null, T0)).toBeNull()
})

test('formatClock rounds up and never goes negative', async () => {
  expect(formatClock(1800)).toBe('30:00')
  expect(formatClock(65)).toBe('01:05')
  expect(formatClock(0.2)).toBe('00:01')
  expect(formatClock(0)).toBe('00:00')
  expect(formatClock(-30)).toBe('00:00')
  expect(formatClock(4500)).toBe('75:00')
})

test('statusText shows the timer only while running', async () => {
  expect(statusText(null, T0)).toBeUndefined()
  expect(statusText(parseSession(file({ state: 'drawn' })), T0)).toBeUndefined()
  expect(statusText(parseSession(file({ state: 'finished' })), T0)).toBeUndefined()
  expect(statusText(parseSession(file()), T0 + 60_000)).toBe('mockinterview 1/3 29:00 left')
  expect(statusText(parseSession(file({ round: 1 })), T0)).toBe('mockinterview 2/3 30:00 left')
  expect(statusText(parseSession(file()), T0 + 1_800_000)).toBe('mockinterview 1/3 time up')
  expect(statusText(parseSession(file()), T0 + 2_000_000)).toBe('mockinterview 1/3 time up')
  expect(statusText(parseSession(file({}, { started_at: null })), T0)).toBe('mockinterview 1/3 running')
})
