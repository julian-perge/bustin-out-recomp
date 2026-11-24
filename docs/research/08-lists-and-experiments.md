# The community list and the REA experiments

Sources:

- AIshihzong/awesome-reverse-engineer-anything at `~/git/AIshihzong/awesome-reverse-engineer-anything`, HEAD `a395116` (2026-11-23). Prefix `awesome/`.
- maruti-md/ai-reverse-engineer-anything at `~/git/maruti-md/ai-reverse-engineer-anything`, HEAD `55f9ff0` (2026-10-26). Prefix `maruti/`.
- pablodiazjorge/rea-lab at `~/git/pablodiazjorge/rea-lab`, HEAD `8576606`. Prefix `rea-lab/`. The PDF does not name this repo. It was cloned for this research because it holds the experiments.

## Summary

- The repo that the PDF lists under "REA research, independent experiments" (maruti-md) holds no experiments. It is a copy of the community list at an older commit.
- The experiments are in pablodiazjorge/rea-lab: five studies, 482 runs. None found that REA raised the solve rate of Claude Code, and the REA runs cost about twice as much in the Claude studies.
- The community list checks which tool a project says it used. It does not check that a result is true.
- Neither list repo has a loop to copy. The rea-lab harness does: it ran hundreds of agent sessions with no person present, with a time limit, a cost limit, a deny-by-default permission mode and a restart that skips finished runs.

## 1. The maruti-md repo is a copy

- Evidence: `git rev-parse HEAD^{tree}` in the maruti-md clone prints `e0d7be6b0c2decb9badc377e7b5dc8c6d248b153`. The awesome clone has two commits with that tree, `55f9ff0` and `8426819`, both of 2026-10-26 (Computed: `git log --format='%h %T'` in the awesome clone).
- It holds only a summary of the studies: `maruti/README.md:172` "Five preregistered studies, 482 runs, and the most decision-relevant evidence in this list."
- The list had the result of study 2 wrong for four days. Commit `4dad8a8` "Correct the rea-lab summary, refresh REA's star count, add two candidates" fixed it. Use the primary source for numbers.

## 2. The community list

### What its verdicts mean

- A tag records a statement by the author: `awesome/AGENTS.md:21` "`REA` is a claim *that the author made*. `Confirmed` in `docs/is-it-rea.md`" and `awesome/AGENTS.md:22` "means *we found the statement*. Neither means the case is good, and neither"
- The rule for the tag: `awesome/AGENTS.md:17` "Do not tag a case `REA` unless the project's own README, the author's post,"
- The list could not read the posts it cites: `awesome/docs/is-it-rea.md:7` "X posts could not be opened from our environment, so for them we rely on the third-party case record"
- The list never runs a build or a compare. Each number in it is copied from a project or a post. UNVERIFIED for each such number.

### Its verdicts on the projects of this research

| Project | The list's verdict | Note |
| --- | --- | --- |
| dx-ball | `awesome/docs/is-it-rea.md:20` "**Confirmed.** One function is byte-matched; the full game is not finished." | Out of date. The dx-ball README claims all 270 functions since 2026-10-22 ([03-dx-ball.md](03-dx-ball.md)). The list also notes: `awesome/README.md:125` "The author is also a contributor to REA, so this is a first-party case." |
| baocut | `awesome/docs/is-it-rea.md:30` "**Claimed by the author, not in the README.** The REA part is one commit, not the whole repo." | Agrees with [05-baocut.md](05-baocut.md) |
| open-scrantic | Not in the list | `rg -n --hidden -g '!.git' -i 'scrantic|castaway|johnny'` prints nothing in both clones |
| a6000-fw-decomp | `awesome/docs/is-it-rea.md:52` "**Confirmed in AGENTS.md.**" | The list reads a project's agent file as evidence of the tool |
| hexgrab | `awesome/README.md:140` ".NET 10 colour picker written from REA's findings on PowerToys' shipped binaries. MIT." | Confirmed as a statement of the README |
| Touhou 4 | `awesome/docs/is-it-rea.md:21` "**REA only for the showcase inspection.** The reconstruction is agent-produced with ReC98 as a base." | |
| Steam game to Unity | `awesome/docs/x-posts.md:10` "the figure appears only in this README and is unverified)." | A post with no code |
| DJI drone | Not in the list | `rg -n --hidden -g '!.git' -i 'dji|drone'` prints nothing in both clones |
| Modern Warfare 2 | `awesome/README.md:189` "Author reports 17 agents over three months, 83% of functions byte-matched. Code is not public." | The only entry that claims byte matching by many agents over months. No code, no log |

### Other leads in the list

- ruguevara/zx-reaper: `awesome/README.md:190` "Agent harness (Claude Code or Codex) that turns ZX Spectrum 48K games into annotated asm that rebuilds byte for byte," This is the only entry that calls itself a harness for byte-exact work. [12-zx-reaper.md](12-zx-reaper.md) has the analysis of its clone.
- Rewrites that are checked against recorded behavior at each step: `awesome/README.md:213` "every piece is replayed against the recording before it moves on, until the app is pure Rust." with the limit `awesome/README.md:213` "It can only catch what the recording covers."
- Static recompilation ports with many Claude commits (they are not matching decompilations): `awesome/README.md:201` "More than 3,000 of its about 7,300 commits are co-authored by Claude" (jhaizhou-ops/S2Arm). The list gives one sentence per project and no loop details. Each is a lead to read, not a result.

### How the list itself is run by an agent

- One `AGENTS.md`, two CI workflows, and a validator script. No hook, no handoff file, no stop rule.
- The validator warns where `AGENTS.md` says it enforces: `awesome/scripts/validate_list.py:438` "does not state a license" and `awesome/scripts/validate_list.py:453` "is tagged REA but has no row" are warnings, and the script exits 0 unless it has errors. A rule that a gate only prints is not a gate.
- A dated number is required for anything that goes stale: `awesome/AGENTS.md:89` "Anything countable goes stale weekly. When you write one:"

## 3. The rea-lab experiments

### Setup

- `rea-lab/README.md:46` "All studies used rea 6.4.0, Claude Code 2.1.296 and the models named in each; later versions may behave differ"
- The agent ran headless: `rea-lab/writeups/2026-10-study-1/README.md:13` "Claude Code 2.1.296 in headless mode (`claude -p`), `claude-sonnet-5-5` with medium effort."
- Condition A has command-line tools only. Condition B adds REA over MCP with Ghidra.
- No model grades the answers: `rea-lab/writeups/2026-10-study-1/README.md:21` "No LLM judge. An oracle, checked against every real binary, decides whether the proposed input is accepted."
- Each study has a plan that was committed first, in the same repo. No outside registry holds it, and one person planned and ran the studies.

### Results

| Study | Task | Runs | Without REA | With REA | Test |
| --- | --- | ---: | --- | --- | --- |
| 1 | 10 small crackmes, 3 runs each | 70 | 28/30 solved, median 23 s, 0.10 USD | 28/30 solved, 54 s, 0.25 USD | McNemar p = 1 |
| 2 | 8 larger programs with decoys | 48 | 11/24 solved, 87 s, 0.24 USD | 4/24 solved, 184 s, 0.50 USD | McNemar p = 0.092 |
| 3 | Find a described function in 4 open-source programs | 144 | 71/72 right, 27 s, 0.08 USD | 68/72 right, 74 s, 0.19 USD | McNemar p = 0.375 |
| 4 | Study 3 tasks with a DeepSeek model | 40 | 20/20 right, 272 s, 0.04 USD | 19/20 right, 332 s, 0.05 USD | McNemar p = 1 |
| 5 | REA with no skill, the official skill, an improved skill | 180 | no such arm | 52/60, 55/60, 52/60 right | The improved skill cost 1.14 times the official one |

Sources of the rows:

- Study 1: `rea-lab/writeups/2026-10-study-1/README.md:19` "Three repetitions per challenge in A and B, one in C: 70 runs, in a shuffled order.", `rea-lab/writeups/2026-10-study-1/README.md:33` "| Median time | 23 s | 54 s | 55 s |", `rea-lab/writeups/2026-10-study-1/README.md:36` "| Median equivalent cost | 0.10 USD | 0.25 USD | 0.28 USD |", `rea-lab/writeups/2026-10-study-1/README.md:38` "**H1, A against B: no large effect detected.** Of the 30 pairs, only two disagree, one each way (exact McNemar, p = 1)"
- Study 2: `rea-lab/writeups/2026-10-study-2/README.md:35` "| Solved | 11/24 (46 %, 28 to 65 %) | 4/24 (17 %, 7 to 36 %) |", `rea-lab/writeups/2026-10-study-2/README.md:40` "| Median time | 87 s | 184 s |", `rea-lab/writeups/2026-10-study-2/README.md:43` "| Median equivalent cost | 0.24 USD | 0.50 USD |", `rea-lab/writeups/2026-10-study-2/README.md:45` "Of the 24 pairs, 13 disagree: in 10 only A solved, in 3 only B (exact McNemar, p = 0.092)."
- Study 3: `rea-lab/writeups/2026-10-study-3/README.md:36` "| Correct | 71/72 (99 %, 93 to 100 %) | 68/72 (94 %, 87 to 98 %) |", `rea-lab/writeups/2026-10-study-3/README.md:41` "| Median time | 27 s | 74 s |", `rea-lab/writeups/2026-10-study-3/README.md:44` "| Median equivalent cost | 0.08 USD | 0.19 USD |"
- Study 4: `rea-lab/writeups/2026-10-study-4/README.md:26` "| Correct | 20/20 (100 %, 84 to 100 %) | 19/20 (95 %, 76 to 99 %) |", `rea-lab/writeups/2026-10-study-4/README.md:30` "| Median time | 272 s | 332 s |"
- Study 5: `rea-lab/writeups/2026-10-study-5/README.md:27` "| Correct, all at the exact start | 52/60 (87 %, 76 to 93 %) | 55/60 (92 %, 82 to 96 %) | 52/60 (87 %, 76 to 93 %) |", `rea-lab/writeups/2026-10-study-5/README.md:36` "the Hodges-Lehmann ratio of C2's cost over C1's is 1.140"
- Total: 70 + 48 + 144 + 40 + 180 = 482 runs. 292 of them compare REA with no REA.

### Limits that the author states

- `rea-lab/writeups/2026-10-study-1/README.md:71` "- One agent and one model; nothing here speaks for other agents yet."
- `rea-lab/writeups/2026-10-study-1/README.md:72` "- 30 pairs detect only large effects."
- `rea-lab/writeups/2026-10-study-1/README.md:73` "- The cost is Claude Code's own estimate at list prices, not money spent."
- In study 2 neither side could run code: `rea-lab/writeups/2026-10-study-2/README.md:96` "- Neither condition could run an interpreter, by design; that removes the brute-force route that most failures needed."
- In study 3 the side without REA was already at 99 percent: `rea-lab/writeups/2026-10-study-3/README.md:138` "- The calibration target was not met: A answered 99 %, so most pairs agree and only a large effect could show."

### What the studies do not test

They compare REA over Ghidra with `llvm-objdump` and text tools, on crackmes and on "find this function" questions. They do not test ghidra-mcp, a matching decompilation, or a task where the agent can compile and compare. So they do not say whether REA would help this repo. They do say that a larger tool surface costs tokens on every turn.

## 4. What the studies say about an unattended session

These come from the write-ups and the harness, and each bears on the design in [10-overnight-design.md](10-overnight-design.md).

1. Tell the agent that nobody will answer. Three runs ended with a question to the user, so the prompt got this line: `rea-lab/bench/conditions.ts:146` "'Nobody will answer questions or grant more permissions during this run: when you cannot go further, return your best" The reason: `rea-lab/writeups/2026-10-study-2/README.md:72` "three runs ended with a question to the user, which nobody can answer in an unattended run, so the prompt says so."
2. A denied common command can end a run. `rea-lab/writeups/2026-10-study-1/README.md:59` "A denied `awk` made an agent stop instead of analysing, so common text filters were allowed." For this repo: test the permission rules of a run before the night (R10 of [10-overnight-design.md](10-overnight-design.md)).
3. Text inside the target can mislead a stuck agent. `rea-lab/writeups/2026-10-study-2/README.md:84` "Text in a target is untrusted input, and the agent needs to treat it so." For this repo: strings in `default.xbe` are data.
4. Tool schemas cost tokens on each request. `rea-lab/writeups/2026-10-study-3/README.md:134` "rea 6.4.0 advertised 153 tools." and, with tool search off, `rea-lab/writeups/2026-10-study-4/README.md:15` "127,161 input tokens on the first request with rea, against 7,903 with tool search on." For this repo: `docs/WORKFLOW.md` starts the ghidra-mcp bridge with `--no-lazy` because of F-0023, so every tool group is registered. The cost of that in a long session is not measured here.
5. Large tool results go to a file, and the agent must be allowed to read it: `rea-lab/docs/adr/0018-benchmark-isolation.md:7` "which cut the agent off from its own results."
6. Most of the cost is cache writes of the growing conversation: `rea-lab/writeups/2026-10-study-5/README.md:42` "Cache writes make about 70 % of every condition's cost:" This agrees with ADR-0010 of this repo, which cut batch sizes because agent context grew.
7. The answer check must be a program. Graders had faults that were found later, and the fix was to grade the saved transcripts again: `rea-lab/bench/README.md:68` "After a grader fix, `node bench/regrade.ts --study <name>` grades a study again from its saved transcripts, without re"
8. A safety classifier stopped many crackme runs (`rea-lab/writeups/2026-10-study-1/README.md:31` "| Runs with a safety classifier stop | 7/30 | 17/30 | 6/10 |"). The author ties this to the task type: `rea-lab/writeups/2026-10-study-3/README.md:94` "The safety classifier stops of studies 1 and 2 went with crackme tasks, not with reverse engineering itself." Whether game decompilation work meets such stops is UNVERIFIED.

### The harness

- Flags of each run: `rea-lab/docs/adr/0018-benchmark-isolation.md:5` "Claude Code runs with `--print --output-format stream-json --verbose --no-session-persistence --setting-sources user -"
- Permission mode: `rea-lab/docs/adr/0018-benchmark-isolation.md:5` "`--permission-mode dontAsk`, so anything the run's own settings do not allow is denied instead of prompting."
- Limits of each run: `rea-lab/writeups/2026-10-study-2/README.md:110` "--timeout-min 30 --max-budget-usd 5"
- A timeout kills the whole process tree, the MCP server and the Ghidra JVM included (same ADR, line 5).
- After a machine restart: `rea-lab/writeups/2026-10-study-2/README.md:89` "the harness skipped the finished runs and repeated each cut run from the start."
- Tools are pinned: `rea-lab/README.md:69` "`tools.json` | Tool versions, download URLs and SHA-256 hashes |"
- The harness is for many short, separate runs (30 minutes at most). It is not one long session. Its agents never commit: `rea-lab/AGENTS.md:51` "- Agents never commit or push."
