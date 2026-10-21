// The Library tab: which packs exist and the command that starts each one.
// Pure, so it is unit-testable; register.tsx does the file-system walk.
//
// The frontmatter reader is a port of `parse_frontmatter` in
// runner/lib/packs.py (the runner stays the source of truth: a pack it
// refuses is refused again when the engineer runs the command).

export type PackType = 'live-coding' | 'system-design' | 'knowledge'

export type LibraryItem = {
  id: string
  title: string
  type: PackType
  levels: string[]
  minutes: number
  /** Which root the winning file came from: built-in, user, project, option. */
  root: string
}

export type LibraryGroup = { type: PackType; title: string; items: LibraryItem[] }

export type LibraryAction = 'practice' | 'teach'

type Meta = Record<string, unknown>

const TYPES: readonly PackType[] = ['live-coding', 'system-design', 'knowledge']
const GROUP_TITLES: Record<PackType, string> = {
  'live-coding': 'Live coding',
  'system-design': 'System design',
  knowledge: 'Knowledge',
}
const DEFAULT_MINUTES: Record<PackType, number> = {
  'live-coding': 30,
  'system-design': 45,
  knowledge: 0,
}
const LEVEL_ORDER = ['junior', 'mid', 'senior', 'staff']

function scalar(raw: string): unknown {
  const v = raw.trim()
  if (v.length >= 2 && v[0] === v[v.length - 1] && (v[0] === '"' || v[0] === "'")) {
    return v.slice(1, -1)
  }
  const low = v.toLowerCase()
  if (low === 'true') return true
  if (low === 'false') return false
  if (/^-?\d+$/.test(v)) return Number.parseInt(v, 10)
  return v
}

function stripComment(value: string): string {
  let quote: string | null = null
  for (let i = 0; i < value.length; i++) {
    const ch = value[i]
    if (quote !== null) {
      if (ch === quote) quote = null
    } else if (ch === '"' || ch === "'") {
      quote = ch
    } else if (ch === '#' && (i === 0 || value[i - 1] === ' ' || value[i - 1] === '\t')) {
      return value.slice(0, i).trimEnd()
    }
  }
  return value
}

/** The frontmatter of a pack file, or null where the runner would refuse it. */
export function parseFrontmatter(text: string): Meta | null {
  const lines = text.split('\n')
  if ((lines[0] ?? '').trim() !== '---') return null
  const end = lines.findIndex((line, i) => i > 0 && line.trim() === '---')
  if (end < 0) return null
  const meta: Meta = {}
  for (const line of lines.slice(1, end)) {
    if (line.trim() === '' || line.trimStart().startsWith('#')) continue
    const colon = line.indexOf(':')
    if (colon < 0) return null
    const key = line.slice(0, colon).trim()
    const value = stripComment(line.slice(colon + 1).trim())
    if (value.startsWith('[') && value.endsWith(']')) {
      const inner = value.slice(1, -1).trim()
      meta[key] = inner === '' ? [] : inner.split(',').map(scalar)
    } else {
      meta[key] = scalar(value)
    }
  }
  return meta
}

const listOf = (v: unknown): string[] =>
  (Array.isArray(v) ? v : v === undefined || v === null ? [] : [v]).map(String)

/** One list entry from a pack file's text, or null for a file to skip. */
export function itemFromText(text: string, root: string): LibraryItem | null {
  const meta = parseFrontmatter(text)
  if (meta === null) return null
  const id = typeof meta.id === 'string' && meta.id !== '' ? meta.id : null
  const type = TYPES.find(t => t === meta.type)
  if (id === null || type === undefined) return null
  const minutes =
    typeof meta.time_minutes === 'number' && meta.time_minutes > 0
      ? meta.time_minutes
      : DEFAULT_MINUTES[type]
  return {
    id,
    title: typeof meta.title === 'string' && meta.title !== '' ? meta.title : id,
    type,
    levels: listOf(meta.level),
    minutes,
    root,
  }
}

/** Items from every root, in precedence order: a later root wins on a shared id. */
export function mergeItems(items: readonly LibraryItem[]): LibraryItem[] {
  const byId = new Map<string, LibraryItem>()
  for (const item of items) byId.set(item.id, item)
  return [...byId.values()]
}

/** The three groups, in a fixed order, each sorted by id (the packs' own order). */
export function groupItems(items: readonly LibraryItem[]): LibraryGroup[] {
  return TYPES.map(type => ({
    type,
    title: GROUP_TITLES[type],
    items: items.filter(i => i.type === type).sort((a, b) => a.id.localeCompare(b.id)),
  }))
}

/** The dim details after a title: levels in order, minutes, a non-built-in root. */
export function itemDetail(item: LibraryItem): string {
  const levels = [...item.levels].sort((a, b) => LEVEL_ORDER.indexOf(a) - LEVEL_ORDER.indexOf(b))
  const parts: string[] = []
  if (levels.length > 0) parts.push(levels.join('/'))
  if (item.minutes > 0) parts.push(`${item.minutes}m`)
  if (item.root !== 'built-in') parts.push(item.root)
  return parts.join(' ')
}

/** Which buttons a row gets: problems can be practised or taught, documents taught. */
export function itemActions(item: LibraryItem): LibraryAction[] {
  return item.type === 'knowledge' ? ['teach'] : ['practice', 'teach']
}

/** The slash command a button puts in the prompt box. */
export function commandFor(item: LibraryItem, action: LibraryAction): string {
  return `/mockinterview:${action} ${item.id}`
}
