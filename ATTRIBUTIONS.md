# Attributions

`mockinterview` is released under the [MIT License](LICENSE). This file says what the content is based on, what it is not, and whose names appear in it.

## Code

The runner (`runner/`) uses only the Python standard library. The mod (`hooks/`) uses only the Claude Code mods API. No third-party code is bundled or copied.

## Problems (`content/live-coding/`, `content/system-design/`)

- The problems are **classic, widely taught interview patterns** (for example Two Sum, Valid Brackets, Word Break, a URL shortener, a rate limiter). Patterns and problem names are common knowledge and not owned by anyone.
- The statements, tests, reference solutions, interviewer notes, hints and estimates were **written for this project**. The `source` field of every pack says `adapted`, meaning an original write-up of a well-known pattern. None of the text, tests or notes is taken from a commercial platform, a book or a company's real interview questions.
- A few statements refer to a common convention by name, for example the level-order list format used by many tree problems. That is a reference to a convention, not copied text.
- If you believe a pack is too close to a protected work, please open an issue and it will be rewritten or removed.

## Study documents (`content/knowledge/`)

- The six documents are summaries and guides. Statements that carry a number in square brackets come from the sources in that document's own **References** section, which lists the title, publisher and link of each one. They are mostly interview-preparation guides and blogs, so treat them as summaries of what interviews ask, not as standards.
- Complexity tables, algorithm code and general explanations without a citation reflect standard computer-science knowledge. The numbers and demonstrations come from running the tools in `runner/tools/`, not from the sources.
- Papers and books named there (for example the consistent hashing paper by Karger et al. and the Dynamo paper by DeCandia et al.) are cited and linked, not reproduced. They belong to their authors and publishers.
- Anyone who wants to read further should use those references and the textbooks the documents recommend.

## How it was made

The plugin was designed and directed by Hiraq (rstlix0x0) and built with the help of Claude, an AI assistant made by Anthropic. The content was drafted with that help and then checked by running it: every pack passes `lint`, and every reference solution passes its own tests (`selftest`).

## Names and trademarks

LeetCode, TestGorilla, Codility, HackerRank, Grokking, DesignGurus, Hello Interview, PracHub, Exponent and AlgoDaily are names of their respective owners. They appear only to describe the kind of practice this plugin offers or to cite a source. This project is not affiliated with, endorsed by or sponsored by any of them. "Claude" and "Claude Code" are products of Anthropic, and this project is not an official Anthropic product.

## Icon

The plugin icon (`.claude-plugin/icon.png`) is an original drawing made for this project: a command prompt inside a timer ring. It is covered by the same MIT License as the rest of the repository.
