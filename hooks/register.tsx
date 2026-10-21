// mockinterview mod: a view over the runner's session file, plus a spoiler guard.
//
// The runner (runner/mi.py) is the single source of truth. This module only
// READS `.mockinterview/session.json` and `.mockinterview/work/PROBLEM.md`
// (relative to the session's working directory) and draws them. It never
// writes, never runs the runner and registers no tools: `$.process` is
// documented as CLI only, so the plugin layer must work without it.
//
// Early-access API: see docs/design.md, sections 9 and 16.

import type { EngineInterface, PluginOptions, Register } from 'claude-code'

import { decide, GUARDED_TOOLS, pathArgs, type GuardContext } from './lib/guard'
import {
  problemBlocks,
  resultsBlocks,
  scorecardBlocks,
  type Block,
} from './lib/format'
import {
  isActive,
  isInterviewLocked,
  parseSession,
  statusText,
  type Session,
} from './lib/session'

const SESSION_FILE = '.mockinterview/session.json'
const PROBLEM_FILE = '.mockinterview/work/PROBLEM.md'
const POLL_MS = 1000
const STORE_KEY = 'autoOpenedSession'

// A "tab" is a pane: with more than one pane open, each pane's title is a tab.
const PANES = [
  { id: 'mockinterview-problem', title: 'Problem', blocks: 'problem' },
  { id: 'mockinterview-results', title: 'Results', blocks: 'results' },
  { id: 'mockinterview-scorecard', title: 'Scorecard', blocks: 'scorecard' },
] as const

type Engine = EngineInterface

// Files are read through `$.fs`; a missing file is not an error here.
async function readText($: Engine, path: string): Promise<string | null> {
  try {
    const text = await $.fs.read(path)
    return typeof text === 'string' ? text : null
  } catch {
    return null
  }
}

async function loadSession($: Engine): Promise<Session | null> {
  return parseSession(await readText($, SESSION_FILE))
}

async function openPanes($: Engine): Promise<boolean> {
  let isPlaced = false
  for (const pane of PANES) {
    const opened = await $.ui.open({ id: pane.id, title: pane.title })
    if (opened.isPlaced) isPlaced = true
  }
  return isPlaced
}

async function closePanes($: Engine): Promise<void> {
  for (const pane of PANES) await $.ui.close({ id: pane.id })
}

async function hasOpenPane($: Engine): Promise<boolean> {
  const ids: readonly string[] = PANES.map(p => p.id)
  return (await $.ui.panes()).some(p => ids.includes(p.id))
}

function optionFlag(options: PluginOptions, key: string): boolean {
  return options[key] !== false // unset or unknown counts as on
}

function optionText(options: PluginOptions, key: string): string | undefined {
  const v = options[key]
  return typeof v === 'string' && v !== '' ? v : undefined
}

/** The guard's verdict for one tool call. Any failure here means "allow". */
async function guardVerdict(
  $: Engine,
  options: PluginOptions,
  tool: string,
  args: Readonly<Record<string, unknown>>,
): Promise<string | undefined> {
  if (!optionFlag(options, 'strict_guard') || !GUARDED_TOOLS.has(tool)) return undefined
  try {
    const session = await loadSession($)
    if (!isInterviewLocked(session)) return undefined
    const ctx: GuardContext = {
      cwd: await $.session.cwd(),
      pluginRoot: $.plugin.root,
      packsDir: optionText(options, 'packs_dir'),
    }
    // Also judge where each path really lands, so a link into a pack root
    // does not slip through. Unresolvable paths simply add nothing.
    const real: string[] = []
    for (const path of pathArgs(tool, args)) {
      try {
        const stat = await $.fs.stat(path, { resolve: true })
        if (stat.realPath !== undefined) real.push(stat.realPath)
      } catch {
        // not there yet, or not resolvable: the spelled path was already judged
      }
    }
    return decide(tool, args, ctx, session, real)
  } catch {
    return undefined
  }
}

type TickState = {
  lastKey: string
  lastStatus: string | undefined
  isTicking: boolean
}

// One poll: refresh the status line, redraw if a file changed, and open the
// panes once for a new active session. Display only, so any failure is skipped.
async function tick($: Engine, options: PluginOptions, state: TickState): Promise<void> {
  if (state.isTicking) return
  state.isTicking = true
  try {
    const text = await readText($, SESSION_FILE)
    const session = parseSession(text)

    const status = statusText(session, await $.clock.now())
    if (status !== state.lastStatus) {
      state.lastStatus = status
      $.ui.status(status)
    }

    // Redraw only when a file changed; the timer itself lives in the status line.
    const problem = session?.state === 'running' ? await readText($, PROBLEM_FILE) : null
    const key = `${text ?? ''}\u0000${problem ?? ''}`
    if (key !== state.lastKey) {
      state.lastKey = key
      $.ui.invalidate('ui.render')
    }

    // A new active session opens the panes once; closing them stays closed.
    if (isActive(session) && optionFlag(options, 'pane_auto_open')) {
      const seen = await $.store.get(STORE_KEY)
      if (seen !== session.id) {
        await $.store.set(STORE_KEY, session.id)
        await openPanes($)
      }
    }
  } catch {
    // skipped
  } finally {
    state.isTicking = false
  }
}

export const register: Register = (on, options) => {
  // Module variables are lost on a reload; everything here is re-derived from
  // the files on the next tick, so that costs at most one extra redraw.
  const state: TickState = { lastKey: '', lastStatus: undefined, isTicking: false }
  let timer: { cancel: () => void } | undefined

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mi-pane',
      description: 'Show or hide the mockinterview pane (problem, results, scorecard)',
    })

    // Open at start only for a session that is already running or drawn.
    const session = await loadSession($)
    if (isActive(session) && optionFlag(options, 'pane_auto_open')) {
      await $.store.set(STORE_KEY, session.id)
      await openPanes($)
    }

    timer?.cancel()
    timer = $.clock.every(POLL_MS, () => {
      void tick($, options, state)
    })
    void tick($, options, state)

    return next(e)
  })

  on('command.run', { command: 'mi-pane' }, async $ => {
    if (await hasOpenPane($)) {
      await closePanes($)
      return { text: 'mockinterview pane closed.' }
    }
    const isPlaced = await openPanes($)
    return {
      text: isPlaced
        ? 'mockinterview pane opened.'
        : 'mockinterview pane is open but waiting for room: widen the terminal.',
    }
  })

  for (const pane of PANES) {
    on('ui.render', { component: 'Pane', requestId: pane.id }, async ($, e) => {
      const { Box, Text, Markdown, Code } = $.ui.resolve(e)
      const session = await loadSession($)

      let blocks: Block[]
      if (pane.blocks === 'problem') {
        const problem = session?.state === 'running' ? await readText($, PROBLEM_FILE) : null
        blocks = problemBlocks(session, problem)
      } else if (pane.blocks === 'results') {
        blocks = resultsBlocks(session)
      } else {
        blocks = scorecardBlocks(session)
      }

      return (
        <Box flexDirection="column">
          {blocks.map(block => {
            switch (block.kind) {
              case 'markdown':
                return <Markdown text={block.text} />
              case 'code':
                return <Code source={block.text} />
              case 'title':
                return <Text bold>{block.text}</Text>
              case 'dim':
                return <Text dimColor>{block.text}</Text>
              case 'good':
                return <Text color="success">{block.text}</Text>
              case 'bad':
                return <Text color="error">{block.text}</Text>
              case 'warn':
                return <Text color="warning">{block.text}</Text>
              default:
                return <Text>{block.text}</Text>
            }
          })}
        </Box>
      )
    })
  }

  // The guard has no `.catch`: if it throws or overruns, the call goes on.
  // Failing open is intended; the guard must never block a session by crashing.
  on('tool.call', async ($, e, next) => {
    const tool = String(e.tool)
    if (!GUARDED_TOOLS.has(tool)) return next(e)
    const args = e as unknown as Readonly<Record<string, unknown>>
    const refusal = await guardVerdict($, options, tool, args)
    return refusal === undefined ? next(e) : { deny: refusal }
  })
}
