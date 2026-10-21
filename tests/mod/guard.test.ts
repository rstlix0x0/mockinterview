import { expect, test } from 'claude-code/testing'

import {
  commandTouchesPacks,
  decide,
  DENY_MESSAGE,
  isRunnerCall,
  normalizePath,
  touchesPacks,
  type GuardContext,
} from '../../hooks/lib/guard'
import { parseSession } from '../../hooks/lib/session'

const CTX: GuardContext = { cwd: '/work/proj', pluginRoot: '/plugins/mockinterview' }

function session(state: string, mode = 'interview') {
  return parseSession(JSON.stringify({ mode, state, level: 'senior', round: 0, rounds_total: 2 }))
}

test('normalizePath folds dots, joins relative paths and keeps ~', async () => {
  expect(normalizePath('/a/b/../c/./d', '/x')).toBe('/a/c/d')
  expect(normalizePath('sub/file.md', '/work/proj')).toBe('/work/proj/sub/file.md')
  expect(normalizePath('..\\up\\f', '/work/proj')).toBe('/work/up/f')
  expect(normalizePath('~/.mockinterview/packs/a.md', '/work/proj')).toBe('/~home/.mockinterview/packs/a.md')
  expect(normalizePath('/A/B//', '/x')).toBe('/a/b')
})

test('touchesPacks: built-in, user, project and packs_dir roots', async () => {
  expect(touchesPacks('/plugins/mockinterview/content/live-coding/lc-a01.md', CTX)).toBe(true)
  expect(touchesPacks('/plugins/mockinterview/content', CTX)).toBe(true)
  expect(touchesPacks('/plugins/mockinterview/content/knowledge/kb-cs.md', CTX)).toBe(true)
  expect(touchesPacks('/plugins/mockinterview/CONTENT/Live-Coding/x.md', CTX)).toBe(true)
  expect(touchesPacks('~/.mockinterview/packs/mine.md', CTX)).toBe(true)
  expect(touchesPacks('/Users/me/.mockinterview/packs', CTX)).toBe(true)
  expect(touchesPacks('.mockinterview/packs/team.md', CTX)).toBe(true)
  expect(touchesPacks('/plugins/mockinterview/content/../content/system-design/x.md', CTX)).toBe(true)
  const withDir: GuardContext = { ...CTX, packsDir: '/team/packs' }
  expect(touchesPacks('/team/packs/a.md', withDir)).toBe(true)
  expect(touchesPacks('/team/packs-other/a.md', withDir)).toBe(false)
})

test('touchesPacks: work dir, project files and other plugin files are fine', async () => {
  expect(touchesPacks('.mockinterview/work/solution.py', CTX)).toBe(false)
  expect(touchesPacks('/work/proj/.mockinterview/work/PROBLEM.md', CTX)).toBe(false)
  expect(touchesPacks('/work/proj/.mockinterview/session.json', CTX)).toBe(false)
  expect(touchesPacks('/work/proj/src/main.py', CTX)).toBe(false)
  expect(touchesPacks('/plugins/mockinterview/runner/mi.py', CTX)).toBe(false)
  expect(touchesPacks('/plugins/mockinterview/docs/authoring.md', CTX)).toBe(false)
  expect(touchesPacks('', CTX)).toBe(false)
})

test('isRunnerCall: only a bare runner invocation counts', async () => {
  expect(isRunnerCall('python3 /plugins/mockinterview/runner/mi.py run')).toBe(true)
  expect(isRunnerCall('python3 "/plugins/mockinterview/runner/mi.py" --data "${CLAUDE_PLUGIN_DATA}" status')).toBe(true)
  expect(isRunnerCall('python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" begin')).toBe(true)
  expect(isRunnerCall('FOO=1 python runner/mi.py list')).toBe(true)
  expect(isRunnerCall('python3 -I runner/mi.py status')).toBe(true)
  expect(isRunnerCall('cat content/live-coding/a.md')).toBe(false)
  expect(isRunnerCall('python3 runner/mi.py run && cat .mockinterview/packs/a.md')).toBe(false)
  expect(isRunnerCall('python3 runner/mi.py run; cat x')).toBe(false)
  expect(isRunnerCall('python3 runner/mi.py run | tee x')).toBe(false)
  expect(isRunnerCall('echo $(cat .mockinterview/packs/a.md) && python3 runner/mi.py')).toBe(false)
  expect(isRunnerCall('python3 solution.py')).toBe(false)
})

test('commandTouchesPacks matches spellings of the pack roots', async () => {
  expect(commandTouchesPacks('cat /plugins/mockinterview/content/live-coding/a.md', CTX)).toBe(true)
  expect(commandTouchesPacks('cat "${CLAUDE_PLUGIN_ROOT}/content/system-design/a.md"', CTX)).toBe(true)
  expect(commandTouchesPacks('ls ~/.mockinterview/packs', CTX)).toBe(true)
  expect(commandTouchesPacks('grep -r hidden .mockinterview/packs', CTX)).toBe(true)
  expect(commandTouchesPacks('cat .mockinterview/work/solution.py', CTX)).toBe(false)
  expect(commandTouchesPacks('python3 solution.py', CTX)).toBe(false)
  expect(commandTouchesPacks('ls', CTX)).toBe(false)
})

test('decide: refusals during a locked interview', async () => {
  const s = session('running')
  const pack = '/plugins/mockinterview/content/live-coding/lc-a01.md'
  expect(decide('Read', { file_path: pack }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Read', { file_path: '~/.mockinterview/packs/x.md' }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Glob', { pattern: '**/*.md', path: '/plugins/mockinterview/content' }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Glob', { pattern: '/plugins/mockinterview/content/**/*.md' }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Grep', { pattern: 'oracle', path: '.mockinterview/packs' }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Bash', { command: `cat ${pack}` }, CTX, s)).toBe(DENY_MESSAGE)
  expect(decide('Bash', { command: 'python3 runner/mi.py run && cat .mockinterview/packs/a.md' }, CTX, s)).toBe(DENY_MESSAGE)
  // drawn is locked as well
  expect(decide('Read', { file_path: pack }, CTX, session('drawn'))).toBe(DENY_MESSAGE)
  // a link that resolves into a pack root is caught through the extra paths
  expect(decide('Read', { file_path: '/tmp/innocent.md' }, CTX, s, [pack])).toBe(DENY_MESSAGE)
})

test('decide: the runner and the work folder stay allowed', async () => {
  const s = session('running')
  expect(decide('Bash', { command: 'python3 /plugins/mockinterview/runner/mi.py run --mode all' }, CTX, s)).toBeUndefined()
  expect(decide('Bash', { command: 'python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" status' }, CTX, s)).toBeUndefined()
  expect(decide('Read', { file_path: '.mockinterview/work/PROBLEM.md' }, CTX, s)).toBeUndefined()
  expect(decide('Read', { file_path: '/work/proj/.mockinterview/work/solution.py' }, CTX, s)).toBeUndefined()
  expect(decide('Glob', { pattern: '*.py', path: '.mockinterview/work' }, CTX, s)).toBeUndefined()
  expect(decide('Grep', { pattern: 'def ', path: '.mockinterview/work' }, CTX, s)).toBeUndefined()
  expect(decide('Bash', { command: 'cat .mockinterview/work/solution.py' }, CTX, s)).toBeUndefined()
  expect(decide('Read', { file_path: '/work/proj/src/app.py' }, CTX, s)).toBeUndefined()
})

test('decide: not locked means no refusal', async () => {
  const pack = '/plugins/mockinterview/content/live-coding/lc-a01.md'
  expect(decide('Read', { file_path: pack }, CTX, session('running', 'practice'))).toBeUndefined()
  expect(decide('Read', { file_path: pack }, CTX, session('finished'))).toBeUndefined()
  expect(decide('Read', { file_path: pack }, CTX, session('scored'))).toBeUndefined()
  expect(decide('Read', { file_path: pack }, CTX, session('abandoned'))).toBeUndefined()
  expect(decide('Read', { file_path: pack }, CTX, null)).toBeUndefined()
})

test('decide: other tools and odd arguments pass', async () => {
  const s = session('running')
  const pack = '/plugins/mockinterview/content/live-coding/lc-a01.md'
  expect(decide('Edit', { file_path: pack }, CTX, s)).toBeUndefined()
  expect(decide('Write', { file_path: pack }, CTX, s)).toBeUndefined()
  expect(decide('Read', {}, CTX, s)).toBeUndefined()
  expect(decide('Read', { file_path: 42 }, CTX, s)).toBeUndefined()
  expect(decide('Bash', {}, CTX, s)).toBeUndefined()
  expect(decide('Bash', { command: '' }, CTX, s)).toBeUndefined()
})
