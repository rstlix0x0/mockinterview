// Whole-module tests: the plugin is loaded by the engine's own host, nothing
// sits beneath it, so every call on `$` is answered by a hook below.

import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

const PLUGIN = 'mockinterview'
const DENIED = 'Hidden during an interview round. Use the runner.'
const T0 = Date.parse('2026-10-21T09:31:12Z')
const CWD = '/work/proj'

// What the person's own `/mi-pane` looks like to the engine.
const MI_PANE = {
  command: 'mi-pane',
  args: '',
  origin: { kind: 'composer' },
  presentation: { isFullscreen: true, columns: 160 },
} as const

function sessionJson(over: Record<string, unknown> = {}, current: Record<string, unknown> = {}): string {
  return JSON.stringify({
    schema: 1,
    session_id: 's-1',
    mode: 'interview',
    level: 'senior',
    state: 'running',
    round: 0,
    rounds_total: 2,
    loop: [{}, {}],
    current: {
      problem: 'lc-c01-lru-cache',
      type: 'live-coding',
      time_minutes: 30,
      limit_seconds: 1800,
      title: 'LRU Cache',
      started_at: '2026-10-21T09:31:12Z',
      hints_used: [],
      last_run: null,
      ...current,
    },
    scorecard: null,
    ...over,
  })
}

type Files = Record<string, string>

// The world beneath the plugin: files, the working directory, the engine's tool.
function world(on: On, files: Files, isPlaced = true) {
  const opened: string[] = []
  const closed: string[] = []
  const statuses: (string | undefined)[] = []
  let invalidations = 0
  let isPaneOpen = false

  // Relative paths reach the hook resolved against the test's working
  // directory, so a file is matched by the tail of the path.
  on('fs.read', (_, e) => {
    const hit = Object.entries(files).find(([name]) => e.path === name || e.path.endsWith(`/${name}`))
    return hit === undefined ? { deny: 'ENOENT' } : { value: hit[1] }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('fs.stat', (_, e) => ({
    value: { kind: 'file', size: 1, mtimeMs: 0, isLink: false, realPath: e.path },
  }))
  on('session.cwd', () => ({ value: CWD }))
  on('tool.call', () => ({ result: {} }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('ui.open', (_, e) => {
    opened.push(e.id)
    isPaneOpen = true
    return { value: isPlaced ? { isPlaced: true } : { isPlaced: false, reason: 'too narrow' } }
  })
  on('ui.close', (_, e) => {
    closed.push(e.id)
    isPaneOpen = false
    return { value: undefined }
  })
  on('ui.panes', () => ({
    value: isPaneOpen
      ? [{ id: 'mockinterview-problem', title: 'Problem', isShown: true, isFocused: false, isPlaced: true }]
      : [],
  }))
  on('ui.status', (_, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.invalidate', () => {
    invalidations += 1
    return { value: undefined }
  })

  return {
    opened,
    closed,
    statuses,
    get invalidations() {
      return invalidations
    },
  }
}

const READ_PACK = { tool: 'Read', file_path: '/plugins/x/content/live-coding/lc-a01-two-sum.md' } as const

// ---------------------------------------------------------------- guard

test('guard refuses pack reads during an interview round', async ($, on) => {
  world(on, { '.mockinterview/session.json': sessionJson() })
  const pack = `/plugins/mockinterview/content/live-coding/lc-a01-two-sum.md`

  expect((await $.tool.call({ tool: 'Read', file_path: pack })).deny).toBe(DENIED)
  expect((await $.tool.call({ tool: 'Read', file_path: '~/.mockinterview/packs/a.md' })).deny).toBe(DENIED)
  expect((await $.tool.call({ tool: 'Glob', pattern: '**/*.md', path: `/plugins/mockinterview/content/live-coding` })).deny).toBe(DENIED)
  expect((await $.tool.call({ tool: 'Grep', pattern: 'oracle', path: '.mockinterview/packs' })).deny).toBe(DENIED)
  expect((await $.tool.call({ tool: 'Bash', command: `cat ${pack}` })).deny).toBe(DENIED)
})

test('guard allows the runner, the work folder and ordinary files', async ($, on) => {
  world(on, { '.mockinterview/session.json': sessionJson() })

  const runner = `python3 "/plugins/mockinterview/runner/mi.py" run --mode all`
  expect((await $.tool.call({ tool: 'Bash', command: runner })).deny).toBeUndefined()
  expect((await $.tool.call({ tool: 'Read', file_path: '.mockinterview/work/PROBLEM.md' })).deny).toBeUndefined()
  expect((await $.tool.call({ tool: 'Read', file_path: `${CWD}/src/app.py` })).deny).toBeUndefined()
  expect((await $.tool.call({ tool: 'Bash', command: 'cat .mockinterview/work/solution.py' })).deny).toBeUndefined()
  expect((await $.tool.call({ tool: 'Edit', file_path: READ_PACK.file_path, old_string: 'a', new_string: 'b' })).deny).toBeUndefined()
})

test('guard is off outside an interview round', async ($, on) => {
  const w = world(on, { '.mockinterview/session.json': sessionJson({ state: 'finished' }) })
  expect(w.opened).toHaveLength(0)
  const pack = `/plugins/mockinterview/content/live-coding/lc-a01-two-sum.md`
  expect((await $.tool.call({ tool: 'Read', file_path: pack })).deny).toBeUndefined()
})

test('guard is off in practice mode', async ($, on) => {
  world(on, { '.mockinterview/session.json': sessionJson({ mode: 'practice' }) })
  expect((await $.tool.call(READ_PACK)).deny).toBeUndefined()
})

test('guard fails open with no session file or a malformed one', async ($, on) => {
  world(on, {})
  expect((await $.tool.call(READ_PACK)).deny).toBeUndefined()
})

test('guard fails open on a malformed session file', async ($, on) => {
  world(on, { '.mockinterview/session.json': '{ this is not json' })
  expect((await $.tool.call(READ_PACK)).deny).toBeUndefined()
})

test('guard fails open when the file system errors', async ($, on) => {
  on('fs.read', () => ({ deny: 'EIO' }))
  on('session.cwd', () => ({ value: CWD }))
  on('tool.call', () => ({ result: {} }))
  expect((await $.tool.call(READ_PACK)).deny).toBeUndefined()
})

test('guard is switched off by the strict_guard option', { options: { strict_guard: false } }, async ($, on) => {
  world(on, { '.mockinterview/session.json': sessionJson() })
  const pack = `/plugins/mockinterview/content/live-coding/lc-a01-two-sum.md`
  expect((await $.tool.call({ tool: 'Read', file_path: pack })).deny).toBeUndefined()
})

test('guard honours the packs_dir option', { options: { packs_dir: '/team/packs' } }, async ($, on) => {
  world(on, { '.mockinterview/session.json': sessionJson() })
  expect((await $.tool.call({ tool: 'Read', file_path: '/team/packs/lc-x.md' })).deny).toBe(DENIED)
})

// ------------------------------------------------- start, status, auto-open

test('session.start opens the panes for a running session and ticks the status line', async ($, on) => {
  const clock = mock.clock(on, { now: T0 + 60_000 })
  mock.store(on)
  const w = world(on, { '.mockinterview/session.json': sessionJson() })

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()

  expect(w.opened).toEqual(['mockinterview-problem', 'mockinterview-results', 'mockinterview-scorecard'])
  expect(w.statuses).toContain('mockinterview 1/2 29:00 left')

  await clock.advance(1000)
  expect(w.statuses).toContain('mockinterview 1/2 28:59 left')

  // past the limit
  await clock.set(T0 + 1_850_000)
  await clock.advance(1000)
  expect(w.statuses[w.statuses.length - 1]).toBe('mockinterview 1/2 time up')

  // the panes were opened once, not on every tick
  expect(w.opened).toHaveLength(3)
})

test('session.start opens nothing and sets no status without a session', async ($, on) => {
  const clock = mock.clock(on, { now: T0 })
  mock.store(on)
  const w = world(on, {})

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()
  await clock.advance(3000)

  expect(w.opened).toHaveLength(0)
  expect(w.statuses).toHaveLength(0)
})

test('a session that appears later opens the panes once', async ($, on) => {
  const clock = mock.clock(on, { now: T0 })
  mock.store(on)
  const files: Files = {}
  const w = world(on, files)

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.opened).toHaveLength(0)

  files['.mockinterview/session.json'] = sessionJson({ state: 'drawn' }, { title: null, started_at: null })
  await clock.advance(1000)
  expect(w.opened).toHaveLength(3)
  expect(w.invalidations).toBeGreaterThan(0)

  await clock.advance(3000)
  expect(w.opened).toHaveLength(3)
})

test('the status line clears when the round ends', async ($, on) => {
  const clock = mock.clock(on, { now: T0 + 1000 })
  mock.store(on)
  const files: Files = { '.mockinterview/session.json': sessionJson() }
  const w = world(on, files)

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.statuses[w.statuses.length - 1]).toBe('mockinterview 1/2 29:59 left')

  files['.mockinterview/session.json'] = sessionJson({ state: 'finished' })
  await clock.advance(1000)
  expect(w.statuses[w.statuses.length - 1]).toBeUndefined()
})

test('pane_auto_open false keeps the panes closed', { options: { pane_auto_open: false } }, async ($, on) => {
  const clock = mock.clock(on, { now: T0 })
  mock.store(on)
  const w = world(on, { '.mockinterview/session.json': sessionJson() })

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()
  await clock.advance(2000)

  expect(w.opened).toHaveLength(0)
  // the status line still works
  expect(w.statuses.length).toBeGreaterThan(0)
})

test('a malformed session file starts quietly', async ($, on) => {
  const clock = mock.clock(on, { now: T0 })
  mock.store(on)
  const w = world(on, { '.mockinterview/session.json': '<<<' })

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })
  await clock.settle()
  await clock.advance(2000)

  expect(w.opened).toHaveLength(0)
  expect(w.statuses).toHaveLength(0)
})

// ---------------------------------------------------------------- command

test('/mi-pane opens the panes, then closes them', async ($, on) => {
  mock.store(on)
  const w = world(on, {})

  await $.session.start({ cwd: CWD, surface: 'terminal', isInteractive: true })

  const first = await $.command.run(MI_PANE)
  expect(first.text).toBe('mockinterview pane opened.')
  expect(w.opened).toEqual(['mockinterview-problem', 'mockinterview-results', 'mockinterview-scorecard'])

  const second = await $.command.run(MI_PANE)
  expect(second.text).toBe('mockinterview pane closed.')
  expect(w.closed).toEqual(['mockinterview-problem', 'mockinterview-results', 'mockinterview-scorecard'])
})

test('/mi-pane says so when no surface can place the panes', async ($, on) => {
  mock.store(on)
  world(on, {}, false)

  const run = await $.command.run(MI_PANE)
  expect(run.text).toContain('waiting for room')
})

// ------------------------------------------------------------------ panes

const PANE_PROPS = {
  title: 'Problem',
  isFocused: false,
  bodyColumns: 60,
  placement: 'dock',
  scroll: { offset: 0, bodyRows: 20 },
  view: {},
} as const

const SURFACES = ['terminal', 'desktop', 'vscode', 'mobile'] as const

test('Problem pane, on every surface', async ($, on) => {
  const files: Files = {}
  world(on, files)

  for (const surface of SURFACES) {
    const mount = (title: string) =>
      $.ui.mount({
        plugin: PLUGIN,
        surface,
        component: 'Pane',
        requestId: 'mockinterview-problem',
        props: { ...PANE_PROPS, title },
      })

    // no session
    delete files['.mockinterview/session.json']
    let ui = await mount('Problem')
    expect(await ui.find({ type: 'Text', text: /No active session/ })).toBeDefined()
    await ui.unmount()

    // interview round, before go: no title, no id
    files['.mockinterview/session.json'] = sessionJson({ state: 'drawn' }, { title: null, started_at: null })
    files['.mockinterview/work/PROBLEM.md'] = '# LRU Cache\nSECRET'
    ui = await mount('Problem')
    expect(await ui.find({ type: 'Text', text: /Round 1 of 2 - say go when ready/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Level: senior/ })).toBeDefined()
    expect(await ui.find({ text: /LRU|SECRET|lc-c01/ })).toBeUndefined()
    await ui.unmount()

    // running: the statement as Markdown
    files['.mockinterview/session.json'] = sessionJson()
    ui = await mount('Problem')
    const md = await ui.find({ type: 'Markdown' })
    expect(md?.props.text).toBe('# LRU Cache\nSECRET')
    await ui.unmount()

    // running but no PROBLEM.md yet
    delete files['.mockinterview/work/PROBLEM.md']
    ui = await mount('Problem')
    expect(await ui.find({ type: 'Text', text: /PROBLEM\.md/ })).toBeDefined()
    await ui.unmount()
  }
})

test('Results pane, on every surface', async ($, on) => {
  const files: Files = {}
  world(on, files)

  for (const surface of SURFACES) {
    const mount = () =>
      $.ui.mount({
        plugin: PLUGIN,
        surface,
        component: 'Pane',
        requestId: 'mockinterview-results',
        props: { ...PANE_PROPS, title: 'Results' },
      })

    files['.mockinterview/session.json'] = sessionJson()
    let ui = await mount()
    expect(await ui.find({ type: 'Text', text: /No test run yet/ })).toBeDefined()
    await ui.unmount()

    files['.mockinterview/session.json'] = sessionJson(
      {},
      {
        hints_used: [{ rung: 'H1', cost: 5 }],
        last_run: {
          passed: 3,
          failed: 1,
          total: 4,
          by_category: { visible: '2/3', hidden: '1/1' },
          perf: { ran: false, ok: true, lines: [] },
          failures: [{ name: 'example-2', category: 'visible', shown: true, args: '[3]', expected: '1', got: '2' }],
        },
      },
    )
    ui = await mount()
    expect(await ui.find({ type: 'Text', text: /3 of 4 cases pass/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /visible: 2\/3/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /FAIL example-2 \[visible\]/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Hints used: H1 \(-5\)/ })).toBeDefined()
    await ui.unmount()
  }
})

test('Scorecard pane, on every surface', async ($, on) => {
  const files: Files = {}
  world(on, files)

  for (const surface of SURFACES) {
    const mount = () =>
      $.ui.mount({
        plugin: PLUGIN,
        surface,
        component: 'Pane',
        requestId: 'mockinterview-scorecard',
        props: { ...PANE_PROPS, title: 'Scorecard' },
      })

    files['.mockinterview/session.json'] = sessionJson()
    let ui = await mount()
    expect(await ui.find({ type: 'Text', text: /Not scored yet/ })).toBeDefined()
    await ui.unmount()

    files['.mockinterview/session.json'] = sessionJson({
      state: 'scored',
      scorecard: {
        total: 78.5,
        reading: '70 to 84: close',
        top_gap: 'testing before coding',
        rounds: [{ problem: 'lc-c01-lru-cache', score: 80, penalty: 5, ratings: { framing: 3 }, evidence: {} }],
      },
    })
    ui = await mount()
    expect(await ui.find({ type: 'Text', text: /Score: 78\.5 of 100/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /framing: 3 of 4/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Top gap: testing before coding/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a pane with a garbage session file still draws', async ($, on) => {
  world(on, { '.mockinterview/session.json': '{{{' })
  const ui = await $.ui.mount({
    plugin: PLUGIN,
    surface: 'terminal',
    component: 'Pane',
    requestId: 'mockinterview-results',
    props: { ...PANE_PROPS, title: 'Results' },
  })
  expect(await ui.find({ type: 'Text', text: /No active session/ })).toBeDefined()
  await ui.unmount()
})
