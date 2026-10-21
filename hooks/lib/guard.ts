// Spoiler guard: pure decision logic. FRICTION, NOT SECURITY.
//
// During an interview round the model must not read the pack files (they hold
// hidden tests, oracles and interviewer notes). The engineer owns the machine
// and can read them in a terminal, so this only stops accidental spoilers.
// Known gaps, all deliberate: a recursive Grep or Glob started from a parent
// folder, a Bash command that builds a path at run time, a link the engine
// cannot resolve, and any tool other than Read, Grep, Glob and Bash.

import { isInterviewLocked, type Session } from './session'

export const DENY_MESSAGE = 'Hidden during an interview round. Use the runner.'

export type GuardContext = {
  /** The session's working directory, absolute. */
  cwd: string
  /** This plugin's directory; its `content/` holds the built-in packs. */
  pluginRoot: string
  /** The optional `packs_dir` plugin option. */
  packsDir?: string | undefined
}

export type ToolArgs = Readonly<Record<string, unknown>>

/** Tools the guard looks at; every other tool passes untouched. */
export const GUARDED_TOOLS: ReadonlySet<string> = new Set(['Read', 'Grep', 'Glob', 'Bash'])

const slashes = (p: string): string => p.replace(/\\/g, '/')

/**
 * Textual normalisation (no file-system access): forward slashes, `.` and
 * `..` folded, relative paths joined to `cwd`, a leading `~` kept as a
 * pseudo-folder so `~/.mockinterview/packs` still matches, lower case (macOS
 * and Windows are case-insensitive).
 */
export function normalizePath(path: string, cwd: string): string {
  let p = slashes(path.trim())
  if (p === '~' || p.startsWith('~/')) p = `/~home${p.slice(1)}`
  else if (!p.startsWith('/') && !/^[A-Za-z]:\//.test(p)) p = `${slashes(cwd)}/${p}`
  const out: string[] = []
  for (const part of p.split('/')) {
    if (part === '' || part === '.') continue
    if (part === '..') out.pop()
    else out.push(part)
  }
  const joined = out.join('/')
  const prefix = /^[A-Za-z]:$/.test(out[0] ?? '') ? '' : '/'
  return `${prefix}${joined}`.toLowerCase()
}

const isUnder = (path: string, root: string): boolean =>
  path === root || path.startsWith(`${root}/`)

/** Folders that count as pack roots, normalised. */
function packRoots(ctx: GuardContext): string[] {
  const roots = [normalizePath(`${ctx.pluginRoot}/content`, ctx.cwd)]
  if (ctx.packsDir !== undefined && ctx.packsDir.trim() !== '') {
    roots.push(normalizePath(ctx.packsDir, ctx.cwd))
  }
  return roots
}

/**
 * Whether a path is a pack root or inside one: the plugin's `content/`, the
 * `packs_dir` option, or any `.mockinterview/packs` (user and project roots).
 * `.mockinterview/work/` is deliberately not a pack root.
 */
export function touchesPacks(path: string, ctx: GuardContext): boolean {
  if (path.trim() === '') return false
  const n = normalizePath(path, ctx.cwd)
  if (packRoots(ctx).some(root => isUnder(n, root))) return true
  if (/(^|\/)\.mockinterview\/packs(\/|$)/.test(n)) return true
  return /\/content\/(live-coding|system-design)(\/|$)/.test(n)
}

/**
 * A command that does nothing but run the runner, for example
 * `python3 "/x/runner/mi.py" run`. The runner enforces the interview rules
 * itself, so it is always allowed; a command that chains anything else to it
 * is not a runner call.
 */
export function isRunnerCall(command: string): boolean {
  if (/[;&|`\n]|\$\(/.test(command)) return false
  return /^\s*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*python3?(?:\.\d+)?\s+(?:-[A-Za-z]\s+)*["']?[^\s"']*runner\/mi\.py["']?(?:\s|$)/.test(
    slashes(command),
  )
}

/** Whether a shell command names a pack root. Substring match, best effort. */
export function commandTouchesPacks(command: string, ctx: GuardContext): boolean {
  const c = slashes(command).toLowerCase()
  const needles = [
    '.mockinterview/packs',
    '/content/live-coding',
    '/content/system-design',
    'claude_plugin_root}/content',
    'claude_plugin_root/content',
    `${slashes(ctx.pluginRoot).toLowerCase()}/content`,
  ]
  if (ctx.packsDir !== undefined && ctx.packsDir.trim() !== '') {
    needles.push(slashes(ctx.packsDir).toLowerCase().replace(/\/+$/, ''))
  }
  return needles.some(n => n !== '' && c.includes(n))
}

const text = (v: unknown): string | undefined =>
  typeof v === 'string' && v !== '' ? v : undefined

/** The file-system paths a tool call names, as written. */
export function pathArgs(tool: string, args: ToolArgs): string[] {
  const out: string[] = []
  if (tool === 'Read') {
    const p = text(args.file_path)
    if (p !== undefined) out.push(p)
  } else if (tool === 'Glob' || tool === 'Grep') {
    const p = text(args.path)
    if (p !== undefined) out.push(p)
    // A pattern or glob that is itself a path: `/plugin/content/**`.
    for (const key of tool === 'Glob' ? ['pattern'] : ['glob']) {
      const v = text(args[key])
      if (v !== undefined && /[\\/]/.test(v)) out.push(v)
    }
  }
  return out
}

/**
 * The verdict for one tool call: a refusal message, or undefined to let it
 * run. `extraPaths` are the same paths resolved through links by the caller.
 */
export function decide(
  tool: string,
  args: ToolArgs,
  ctx: GuardContext,
  session: Session | null,
  extraPaths: readonly string[] = [],
): string | undefined {
  if (!isInterviewLocked(session) || !GUARDED_TOOLS.has(tool)) return undefined
  if (tool === 'Bash') {
    const command = text(args.command)
    if (command === undefined || isRunnerCall(command)) return undefined
    return commandTouchesPacks(command, ctx) ? DENY_MESSAGE : undefined
  }
  const paths = [...pathArgs(tool, args), ...extraPaths]
  return paths.some(p => touchesPacks(p, ctx)) ? DENY_MESSAGE : undefined
}
