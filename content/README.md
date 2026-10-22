# Built-in content

This folder ships with the plugin; installing the plugin is all it takes to get it. Formats are described in `docs/authoring.md`.

| Folder | Count | What |
|---|---|---|
| `live-coding/` | 57 | Live-coding problems for any language, tiers A (junior), B (junior to mid) and C (senior), each with a typed signature, visible, edge and hidden test cases with expected values, a Python reference solution and interviewer notes |
| `system-design/` | 16 | Design problems S1 to S16 with interviewer notes, a reference design and a reference estimate |
| `knowledge/` | 6 | Study guides and reference documents |

Each pack carries the code it had in the original practice kit as `legacy_id` (A1, B12, C3, S5). The study guides refer to problems by those codes.

## Deferred

These parts of the original kit need special checkers and are **not** in this release:

| Tier | What | Why deferred |
|---|---|---|
| D | Concurrency exercises (bounded blocking queue, ordered parallel map, single-flight) | Need thread stress harnesses |
| E | Debugging snippets (E1 to E8) | Need a "find and fix against a specification" checker |
| F | SQL questions (F1 to F12) | Need an SQLite result checker |
| G | Multiple-choice knowledge bank (G1 to G47) | Need a quiz runner |
| Estimation drills D1 to D6 | Reference assumptions are in the appendix of `knowledge/kb-estimation.md` | No separate pack type yet |

## Live-coding packs

| Code | Pack id | Title | Minutes |
|---|---|---|---|
| A1 | `lc-a01-two-sum` | Two Sum | 10 |
| A2 | `lc-a02-valid-brackets` | Valid Brackets | 10 |
| A3 | `lc-a03-roman-numeral-to-integer` | Roman Numeral to Integer | 10 |
| A4 | `lc-a04-group-anagrams` | Group Anagrams | 15 |
| A5 | `lc-a05-parse-one-csv-line` | Parse One CSV Line | 20 |
| A6 | `lc-a06-rotate-a-matrix` | Rotate a Matrix | 15 |
| A7 | `lc-a07-top-k-words` | Top K Words | 15 |
| A8 | `lc-a08-count-primes` | Count Primes Below N | 10 |
| A9 | `lc-a09-validate-ipv4` | Validate an IPv4 Address | 10 |
| A10 | `lc-a10-fizzbuzz` | FizzBuzz | 10 |
| A11 | `lc-a11-valid-palindrome` | Valid Palindrome | 10 |
| A12 | `lc-a12-single-number` | Single Number | 10 |
| A13 | `lc-a13-maximum-subarray-sum` | Maximum Subarray Sum | 15 |
| A14 | `lc-a14-spiral-matrix` | Spiral Matrix | 20 |
| A15 | `lc-a15-house-robber` | House Robber | 15 |
| A16 | `lc-a16-stack-with-minimum` | Stack With Minimum | 15 |
| B1 | `lc-b01-longest-unique-substring` | Longest Substring Without Repeating Characters | 25 |
| B2 | `lc-b02-merge-intervals` | Merge Intervals | 20 |
| B3 | `lc-b03-top-k-frequent-elements` | Top K Frequent Elements | 20 |
| B4 | `lc-b04-number-of-islands` | Number of Islands | 25 |
| B5 | `lc-b05-course-order` | Course Order (Lexicographically Smallest Topological Sort) | 30 |
| B6 | `lc-b06-tree-max-path-sum` | Binary Tree Maximum Path Sum | 35 |
| B7 | `lc-b07-coin-change` | Coin Change (Fewest Coins) | 25 |
| B8 | `lc-b08-longest-increasing-subsequence` | Longest Strictly Increasing Subsequence | 30 |
| B9 | `lc-b09-word-break` | Word Break | 25 |
| B10 | `lc-b10-search-rotated-array` | Search in a Rotated Sorted Array | 25 |
| B11 | `lc-b11-minimum-window-substring` | Minimum Window Substring | 40 |
| B12 | `lc-b12-running-median` | Running Median | 30 |
| B13 | `lc-b13-word-ladder` | Word Ladder | 40 |
| B14 | `lc-b14-edit-distance` | Edit Distance | 30 |
| B15 | `lc-b15-generate-balanced-parentheses` | Generate Balanced Parentheses | 20 |
| B16 | `lc-b16-network-delay-time` | Network Delay Time | 30 |
| B17 | `lc-b17-trapping-rain-water` | Trapping Rain Water | 30 |
| B18 | `lc-b18-min-meeting-rooms` | Minimum Meeting Rooms | 25 |
| B19 | `lc-b19-linked-list-cycle-entry` | Linked List Cycle Entry | 25 |
| B20 | `lc-b20-reverse-k-groups` | Reverse Nodes in k-Groups | 35 |
| B21 | `lc-b21-validate-a-binary-search-tree` | Validate a Binary Search Tree | 25 |
| B22 | `lc-b22-lowest-common-ancestor` | Lowest Common Ancestor of a Binary Tree | 30 |
| B23 | `lc-b23-daily-temperatures` | Days Until a Warmer Temperature | 25 |
| B24 | `lc-b24-combination-sum` | Combination Sum | 25 |
| B25 | `lc-b25-connected-components` | Connected Components | 20 |
| B26 | `lc-b26-merge-k-sorted-lists` | Merge K Sorted Lists | 25 |
| B27 | `lc-b27-kth-largest` | K-th Largest Element | 25 |
| B28 | `lc-b28-longest-palindrome` | Longest Palindromic Substring | 30 |
| B29 | `lc-b29-decode-ways` | Decode Ways | 25 |
| B30 | `lc-b30-sliding-window-maximum` | Sliding Window Maximum | 30 |
| C1 | `lc-c01-lru-cache` | LRU Cache | 30 |
| C2 | `lc-c02-transactional-kv-store` | In-Memory Key-Value Store with Nested Transactions | 40 |
| C3 | `lc-c03-sliding-window-rate-limiter` | Sliding-Window Rate Limiter | 35 |
| C4 | `lc-c04-task-scheduler` | Task Scheduler with Dependencies and Workers | 45 |
| C5 | `lc-c05-access-log-analytics` | Access-Log Analytics | 40 |
| C6 | `lc-c06-arithmetic-expression-evaluator` | Arithmetic Expression Evaluator | 40 |
| C7 | `lc-c07-in-memory-file-system` | In-Memory File System | 45 |
| C8 | `lc-c08-http-path-router` | HTTP Path Router | 45 |
| C9 | `lc-c09-spreadsheet-evaluator` | Spreadsheet Formula Evaluator | 45 |
| C10 | `lc-c10-search-suggestions` | Search Suggestions | 35 |
| C11 | `lc-c11-priority-job-queue` | Priority Job Queue with Retries and Dead Letters | 50 |

## System-design packs

| Code | Pack id | Title | Minutes |
|---|---|---|---|
| S1 | `sd-s01-url-shortener` | URL shortener | 40 |
| S2 | `sd-s02-distributed-rate-limiter` | Distributed rate limiter | 40 |
| S3 | `sd-s03-distributed-key-value-store` | Distributed key-value store | 45 |
| S4 | `sd-s04-news-feed` | News feed (social timeline) | 45 |
| S5 | `sd-s05-chat-service` | Chat service | 45 |
| S6 | `sd-s06-notification-system` | Notification system | 40 |
| S7 | `sd-s07-web-crawler` | Web crawler | 40 |
| S8 | `sd-s08-search-autocomplete` | Search autocomplete (typeahead) | 35 |
| S9 | `sd-s09-file-storage-and-sync` | File storage and sync | 45 |
| S10 | `sd-s10-video-streaming` | Video streaming platform | 45 |
| S11 | `sd-s11-ride-hailing-nearby-search` | Ride hailing and nearby search | 45 |
| S12 | `sd-s12-ticket-sales-flash-crowd` | Ticket sales under a flash crowd | 45 |
| S13 | `sd-s13-distributed-job-scheduler` | Distributed job scheduler | 45 |
| S14 | `sd-s14-metrics-monitoring-platform` | Metrics and monitoring platform | 45 |
| S15 | `sd-s15-llm-gateway-and-retrieval` | LLM gateway and retrieval platform | 45 |
| S16 | `sd-s16-payment-processing` | Payment processing (optional) | 45 |

## Knowledge documents

- `kb-cs-fundamentals`
- `kb-live-coding-study-guide`
- `kb-system-design-study-guide`
- `kb-estimation`
- `kb-building-blocks`
- `kb-simulations`

Content is MIT licensed with the rest of the repository. The problems are classic patterns, rewritten for this plugin.
