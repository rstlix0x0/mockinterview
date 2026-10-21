import { expect, test } from 'claude-code/testing'

import {
  commandFor,
  groupItems,
  itemActions,
  itemDetail,
  itemFromText,
  mergeItems,
  parseFrontmatter,
  type LibraryItem,
} from '../../hooks/lib/library'

// The shape of a real pack's frontmatter (content/live-coding/lc-a01-two-sum.md).
const TWO_SUM = [
  '---',
  'id: lc-a01-two-sum        # stable forever',
  'title: Two Sum',
  'type: live-coding',
  'level: [junior, mid]',
  'tags: [hash-map, array]',
  'time_minutes: 10',
  'runs_code: true',
  '---',
  '',
  '## Statement',
  'id: not-frontmatter',
].join('\n')

function item(over: Partial<LibraryItem> = {}): LibraryItem {
  return {
    id: 'lc-x',
    title: 'X',
    type: 'live-coding',
    levels: ['mid'],
    minutes: 20,
    root: 'built-in',
    ...over,
  }
}

test('parseFrontmatter reads the runner subset: scalars, lists, comments, quotes', async () => {
  const meta = parseFrontmatter(TWO_SUM)
  expect(meta?.id).toBe('lc-a01-two-sum')
  expect(meta?.level).toEqual(['junior', 'mid'])
  expect(meta?.time_minutes).toBe(10)
  expect(meta?.runs_code).toBe(true)

  const quoted = parseFrontmatter('---\ntitle: "A # not a comment"\nlevel: []\n# a comment line\n---\n')
  expect(quoted?.title).toBe('A # not a comment')
  expect(quoted?.level).toEqual([])
})

test('parseFrontmatter refuses what the runner refuses', async () => {
  expect(parseFrontmatter('# no frontmatter\n')).toBeNull()
  expect(parseFrontmatter('---\nid: x\n')).toBeNull()
  expect(parseFrontmatter('---\nid x\n---\n')).toBeNull()
})

test('itemFromText keeps the list fields and skips files without an id or a known type', async () => {
  expect(itemFromText(TWO_SUM, 'built-in')).toEqual({
    id: 'lc-a01-two-sum',
    title: 'Two Sum',
    type: 'live-coding',
    levels: ['junior', 'mid'],
    minutes: 10,
    root: 'built-in',
  })
  expect(itemFromText('---\ntitle: No id\ntype: knowledge\n---\n', 'user')).toBeNull()
  expect(itemFromText('---\nid: q-1\ntype: quiz\n---\n', 'user')).toBeNull()
  expect(itemFromText('plain text', 'user')).toBeNull()
})

test('itemFromText falls back like the runner: title to id, minutes by type', async () => {
  const sd = itemFromText('---\nid: sd-x\ntype: system-design\nlevel: senior\n---\n', 'project')
  expect(sd?.title).toBe('sd-x')
  expect(sd?.minutes).toBe(45)
  expect(sd?.levels).toEqual(['senior'])
  const kb = itemFromText('---\nid: kb-x\ntype: knowledge\n---\n', 'option')
  expect(kb?.minutes).toBe(0)
})

test('mergeItems lets a later root win on a shared id', async () => {
  const merged = mergeItems([
    item({ id: 'lc-a', title: 'Built-in A' }),
    item({ id: 'lc-b' }),
    item({ id: 'lc-a', title: 'Team A', root: 'project' }),
  ])
  expect(merged).toHaveLength(2)
  expect(merged.find(i => i.id === 'lc-a')?.title).toBe('Team A')
})

test('groupItems keeps the three groups in order, each sorted by id, empty ones included', async () => {
  const groups = groupItems([
    item({ id: 'lc-b02' }),
    item({ id: 'kb-notes', type: 'knowledge' }),
    item({ id: 'lc-a01' }),
  ])
  expect(groups.map(g => g.title)).toEqual(['Live coding', 'System design', 'Knowledge'])
  expect(groups[0].items.map(i => i.id)).toEqual(['lc-a01', 'lc-b02'])
  expect(groups[1].items).toHaveLength(0)
  expect(groups[2].items.map(i => i.id)).toEqual(['kb-notes'])
})

test('itemDetail orders levels and names a non-built-in root', async () => {
  expect(itemDetail(item({ levels: ['senior', 'junior'], minutes: 15 }))).toBe('junior/senior 15m')
  expect(itemDetail(item({ levels: [], minutes: 0, type: 'knowledge', root: 'user' }))).toBe('user')
})

test('problems offer practice and teach, documents teach only; commands name the skill and id', async () => {
  expect(itemActions(item())).toEqual(['practice', 'teach'])
  expect(itemActions(item({ type: 'system-design' }))).toEqual(['practice', 'teach'])
  expect(itemActions(item({ type: 'knowledge' }))).toEqual(['teach'])
  expect(commandFor(item({ id: 'lc-a01-two-sum' }), 'practice')).toBe('/mockinterview:practice lc-a01-two-sum')
  expect(commandFor(item({ id: 'kb-estimation' }), 'teach')).toBe('/mockinterview:teach kb-estimation')
})
