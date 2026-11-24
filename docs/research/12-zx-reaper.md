# zx-reaper

Source: the clone of ruguevara/zx-reaper at `~/git/ruguevara/zx-reaper`, HEAD `a0fb17b` (2026-10-30). Citations with the prefix `zx-reaper/` point into that clone. The PDF does not name this repo. The community list names it ([08-lists-and-experiments.md](08-lists-and-experiments.md)), and it was cloned because it is the only entry that calls itself a harness for a rebuild that is equal byte for byte.

## Summary

- It is a kit for ZX Spectrum games: annotated assembly that builds back to the original tape, then ports. It does not use Ghidra, REA or MCP.
- Its gate is one command with an exit code, and a parallel-safe form of it for subagents.
- It has no launcher, no hook, no CI and no limit of time or cost. A person starts the agent and types "continue" when it stalls.
- Its own run report records the failure that this research is about: agents that ran overnight stalled until the author came back.

## 1. What it is

- `zx-reaper/README.md:7` "An agent harness for analysing and porting ZX Spectrum 48K games, for"
- It takes ideas from REA and does not use it: `zx-reaper/README.md:287` "ideas from [REA](https://github.com/morluto/rea) and the reconstruction"
- No Ghidra: `zx-reaper/docs/method.md:50` "Ghidra and IDA know nothing of Spectrum loaders and give no source that builds"
- History (Computed): 134 commits from 2026-10-23 to 2026-10-30, 81 by the author name "Claude". Trailers name Claude Opus 5.5 on 79 lines.
- Agent files: `AGENTS.md`, `template/AGENTS.md` (copied into each game project) and 10 skills. No settings file, no hook, no subagent definition (Computed: `rg -n --hidden -g '!.git' -e PreToolUse -e PostToolUse -e SessionStart -e 'pre-commit' .` prints nothing).

## 2. The loop

A lead agent in an interactive session plans and reviews. Subagents on a cheaper model annotate in small batches.

- `zx-reaper/template/AGENTS.md:93` "Orchestration: the lead agent plans, classifies, relocates and reviews. Bulk" `zx-reaper/template/AGENTS.md:94` "annotation goes to subagents (cheaper model) in batches of 5"
- The queue is computed each time, not stored: `zx-reaper/tools/zxq.py:238` "Un-annotated entries, those with fewest un-annotated dependencies first." This is the same order as `docs/METHODOLOGY.md` ("Order of work": leaf functions first).
- The agent reads the disassembly through one tool and never as a whole file: `zx-reaper/tools/zxq.py:4` "The agent should read the disassembly through this tool, never whole."
- Each subagent edits only the files it was given: `zx-reaper/template/skills/zx-annotate/SKILL.md:9` "`tools/zxq.py next N`. Edit only those files. Other agents edit other files"

## 3. The gate

- The rule: `zx-reaper/template/AGENTS.md:11` "`make` must print `IDENTICAL` after every change you keep."
- The compare: `zx-reaper/template/Makefile:104` "@if cmp -s $< $(ORIG); then echo" and, when the files differ, `zx-reaper/template/Makefile:105` "exit 1; fi"
- A form for subagents that work at the same time. It builds in a private copy: `zx-reaper/tools/zxq.py:34` "`make verify` in a private copy (safe for"
- The exit code is what counts: `zx-reaper/docs/method.md:206` "Check the exit code of `make`, not its output."
- A self-test drives the whole kit with no agent: `zx-reaper/README.md:181` "`selftest/run.sh` builds a small fixture game and takes it through the whole"

Faults of the gate:

- Nothing makes the agent run it. No hook, no CI.
- One target hides a failure: `zx-reaper/template/Makefile:210` "@$(T)/zxq.py audit; true"
- A list that the skill calls part of the gate is only printed: `zx-reaper/tools/zxport.py:109` "print('never ran in any record (add an input that reaches them): ' + ', '.join(never))"
- The byte compare passed with a wrong address in the source: `zx-reaper/docs/the-hobbit-run.md:70` "the build ignores skool addresses: IDENTICAL anyway" The fix was a second check in the tool. A byte-equal build does not prove that the notes around the bytes are right.

## 4. Long runs

- State: `zx-reaper/docs/method.md:196` "State between sessions lives in git and `re/notes.md`; `make status` and `zxq.py next` tell where the work stopped."
- `/loop` is named as an idea only: `zx-reaper/docs/method.md:196` "Long work can run in a loop (`/loop`)"
- The stall rule, the only autonomy rule: `zx-reaper/template/AGENTS.md:108` "subagent that goes quiet: read its last step and resume it with a message;" `zx-reaper/template/AGENTS.md:109` "do not wait for the human, and do not start a duplicate."
- A size rule for subagent tasks: `zx-reaper/template/AGENTS.md:107` "to finish well within an hour (split a module of over ~1,500 lines). A"
- What happened in a real run: `zx-reaper/docs/the-hobbit-run.md:46` "The five agents still running overnight stalled (a watchdog stopped them between tool calls)" and `zx-reaper/docs/the-hobbit-run.md:80` "| all | five agents stalled overnight until the author said" What the watchdog is, the repo does not say. UNVERIFIED. Two commits of that night are 9 hours 25 minutes apart (Computed: `fffff8f` and `cc7a9a9`, 2026-10-24).
- Three cases where the agent asks the human: `zx-reaper/template/AGENTS.md:135` "## Ask the human when", for example `zx-reaper/template/AGENTS.md:140` "- a build difference persists after two attempts to explain it."
- The claim of a run with no human action is a statement of the author: `zx-reaper/docs/hungry-horace-run.md:30` "Human: no actions beyond setting the task." No transcript is in the repo. UNVERIFIED.
- No limit of time, turns, tokens or cost in code (Computed: a search for timeout, budget, max turns and deadline finds only a 10-second version probe in `tools/zxdoctor.py`).

## 5. What to take

| Mechanism | Verdict | Where it goes in this repo |
| --- | --- | --- |
| The stall rule: read the quiet subagent's last step, resume it, start no duplicate | Take | R2 (the stall line of `status`) and the new section of `docs/WORKFLOW.md` (R6) |
| A subagent task that ends well within an hour | Take as a measure | R10 measures the minutes of a batch. Issue #86 decides the batch size |
| A gate form that is safe for parallel agents | Already here | Each matcher worktree writes to its own `build/match` (`docs/WORKFLOW.md`, "A matcher's worktree") |
| A queue that is computed, not stored | Already here | `bodecomp.match candidates` |
| A self-test of the whole kit with no agent | Partly here | `pytest` on synthetic fixtures. The pre-flight of R4 adds the real inputs |
| "Ask the human" after two failed explanations | Replace | Park with the blocker class, as `.claude/agents/matcher.md` says, and go on |
| A gate that the agent is only told to run | Do not take | The lead runs the gate after each merge, and `finish` runs it at the end (R2, R6) |

The overnight stall in this repo's own report is the strongest evidence in the set for two parts of the design: the clock command with a stall line, and the rehearsal before the first night.
