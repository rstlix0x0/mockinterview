# mockinterview

Practice software-engineering interviews inside Claude Code. An **Interviewer** runs timed live-coding and system-design rounds, a **Teacher** explains problems and concepts, and a Python runner checks your code by running it, not by reading it. You can add your own problems as plain Markdown files.

Think of it as a small, local, open-source cousin of TestGorilla or Codility, with a patient coach attached. Nothing leaves your machine except what Claude Code itself sends to the model.

> **Status: 0.2.0, early.** The plugin layer is the product. The optional pane and timer (a *mod*) use Claude Code's early-access Mods API and may break between releases. See [Limits](#honest-limits).

> **Supported languages: Python and JavaScript.** Live-coding solutions are written in Python (3.11 or newer, the default) or JavaScript (Bun, or Node 18 or newer). Say "in JavaScript" when you start, or set the `default_language` option. Go and Rust are planned; see [docs/languages.md](docs/languages.md). System-design rounds involve no code, so they are not affected.

## Install

You need Claude Code, and Python 3.11 or newer on your path as `python3`.

**Terminal** (inside a Claude Code session):

```text
/plugin marketplace add rstlix0x0/mockinterview
/plugin install mockinterview@mockinterview
```

Or in one step (Claude Code v2.1.275 or later):

```text
/plugin install mockinterview --marketplace rstlix0x0/mockinterview
```

**Shell** (no session needed):

```bash
claude plugin marketplace add rstlix0x0/mockinterview
claude plugin install mockinterview@mockinterview
```

On Claude Code v2.1.292 or later one command does both: `claude plugin install mockinterview --marketplace rstlix0x0/mockinterview`.

**Desktop app**: the desktop app's local sessions read the same plugin settings as the terminal on the same computer. Add the marketplace once with the shell command above, then in the **Code** tab click **+**, choose **Add plugins** (or **Plugins**, then **Browse plugins**), select *Mock Interview* and pick a scope.

After installing, run `/reload-plugins` or start a new session. Type `/mockinterview:` and the five skills appear. The plugin uses `userConfig` options, so it needs Claude Code v2.1.271 or later.

## Quick start

| Command | What it does |
|---|---|
| `/mockinterview:interview [level]` | A timed mock interview: 2 to 3 rounds drawn for your level. You do not choose the problems |
| `/mockinterview:practice [problem-id]` | Practise one problem you choose, with a friendly partner and optional scorecard |
| `/mockinterview:teach [id or topic]` | Be taught a problem, a pattern or a study document, then be quizzed |
| `/mockinterview:add-problem` | Write your own problem or document, guided, with lint and self-test |
| `/mockinterview:progress` | Your history, weak tags and the next three drills |

A first session:

1. Open a folder where you want to work and start Claude Code.
2. Run `/mockinterview:interview` and tell it your level.
3. Say "go". The clock starts and you get the problem.
4. Write your solution in **your own editor**, in `.mockinterview/work/solution.py` (`solution.js` for JavaScript). Say "run my tests" when you want them run.
5. Say "I'm done". After the last round you get a scorecard and a short debrief.

## What is in the box

- **57 live-coding problems** in Python, from micro-tasks to senior design-style problems (hash maps, graphs, dynamic programming, parsers, class design), each with visible, edge, hidden, fuzz and performance tests.
- **16 system-design problems** (URL shortener to LLM gateway) with clarifying answers, reference designs, probes, curveballs and a reference estimate.
- **6 knowledge documents**: CS fundamentals, live-coding and system-design study guides, estimation, building blocks, simulations.
- Estimation checker, design linter and six small simulations for testing claims (caching, hashing, queues, rate limits, fan-out, booking races).

Not in 0.2.0: concurrency exercises, debugging exercises, SQL problems, the multiple-choice bank, and a behavioural round for staff candidates. The pack format is ready for them; they are on the list.

## How a session works

| Mode | Who picks the problem | Hints | Scoring |
|---|---|---|---|
| Interview | The runner, at random for your level, hidden until "go", no re-roll | Yes, one rung at a time, each costs points | Always |
| Practice | You | Yes, same costs | Optional |
| Teach | You | Not applicable: it is a lesson | None |

Levels are junior, mid, senior and staff. Loops: junior two coding rounds; mid and senior two coding rounds and a design round; staff two design rounds and a coding round. Content for senior is the deepest; thinner pools fall back to the adjacent level, and the interviewer tells you.

Scores use a 0 to 4 rubric per dimension (framing, approach, implementation, quality, testing, communication, adaptability for coding; scoping, estimation, architecture, deep dives, reliability, communication for design). Implementation is computed from your test results; the rest is rated by an independent scorer agent from the interviewer's notes, with one line of evidence each. The 85 / 70 / 55 reading scale is this project's own calibration, not an industry standard.

## The pane (optional mod)

If your Claude Code supports mods, `mockinterview` adds a pane beside the chat with the problem statement, the last test results and the scorecard, a countdown in the status line, and guards that stop you from reading hidden pack files by accident during an interview. Options (`/config`): `pane_auto_open`, `strict_guard`. Toggle the pane with `/mockinterview-pane`.

The pane's **Library** tab lists every live-coding problem, design problem and knowledge document from all pack roots. A problem has *Practice* and *Teach* buttons, a document *Teach*: a press puts `/mockinterview:practice <id>` or `/mockinterview:teach <id>` in the prompt box, and you press Enter to start. The list is hidden during an interview round, where the runner picks the problems.

The mod reads the session files the runner writes; it never owns state. Without it, everything works the same through the conversation. The mod runs with Claude Code's access, so as with any plugin, install from sources you trust.

## Add your own problems

A problem is one Markdown file: frontmatter, a statement, tests, a reference solution and interviewer notes. Run `/mockinterview:add-problem` for a guided version, or read [docs/authoring.md](docs/authoring.md). Where packs live:

| Root | Path |
|---|---|
| Built-in | `content/` in the plugin |
| User | `~/.mockinterview/packs/` |
| Project | `<project>/.mockinterview/packs/` |
| Option | the *Extra packs folder* plugin option |

The user and project folders are optional: create them only if you want to add content. A pack with tests contains Python that the runner executes; packs outside the built-in folder are refused until you run `mi.py trust` on their root. Read a teammate's pack before you trust it.

## Requirements and permissions

- Claude Code with plugin support (v2.1.271 or later) and Python 3.11 or newer; the runner uses only the standard library.
- Solutions are Python or JavaScript. JavaScript needs `bun` or `node` on your PATH; `mi.py langs` shows what was found. In an interview round a solution may use only the standard library (Node builtins for JavaScript, and no packages in `package.json`); practice and teach allow any installed package.
- The skills call the runner through the Bash tool. To avoid a permission prompt on every call, you can allow just the runner in `.claude/settings.json`:

```json
{ "permissions": { "allow": ["Bash(python3 *runner/mi.py *)"] } }
```

## Privacy

Everything is local: sessions and work files live in `.mockinterview/` inside your project, history and the trust list live in the plugin's data folder under `~/.claude/plugins/data/`. The plugin never uploads anything and never edits your `.gitignore`; add `.mockinterview/` to it yourself if you do not want to commit your practice files.

## Honest limits

- **Guards are friction, not security.** You own the machine and can read any file. The guard only prevents accidental spoilers.
- **The mod is early access.** It depends on the Mods API, which changes between releases. How it behaves in the Desktop app, VS Code and mobile is not verified yet; the terminal is the primary target. The plugin layer does not depend on it.
- **Python and JavaScript** for solutions; the runner itself is Python. Problem statements show Python names and types: in JavaScript the names are camelCase (`two_sum` is `twoSum`), as the stub in the work file shows.
- **The scorer is an AI judgement** for everything except test results. It cites evidence, and you can disagree with it.
- **Staff behavioural round** is not included yet.
- Problems are classic patterns written for this project; the `source` field of each pack says whether it is original, adapted or third-party.

## Contributing

Issues and pull requests are welcome, especially new packs, fixes to tests that are wrong, and ports of the runner to other languages. Run `python3 runner/mi.py lint --all` and `python3 runner/mi.py selftest --all` before sending a pack. Do not copy text from commercial platforms or a company's real interview questions.

## License

MIT. See [LICENSE](LICENSE). What the content is based on, and whose names appear in it, is in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
