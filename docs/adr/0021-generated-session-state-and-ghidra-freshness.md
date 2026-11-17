# ADR-0021: The session hook generates the state of the work, a label names the Ghidra writer, and a stamp shows whether a Ghidra project is level

- **Status:** Accepted (user decision, 2026-11-17, spec/56-workflow-both-machines.md)
- **Date:** 2026-11-17
- **Amends:** [ADR-0003](0003-ghidra-mcp-first-one-writer.md), [ADR-0007](0007-agent-workflow.md), [ADR-0019](0019-issues-are-the-only-task-queue.md)
- **Amended by:** [ADR-0022](0022-function-hash-covers-function-starts.md) (points 8 and 9: the functions hash covers only the function starts)

## Context

Issue #56 makes the workflow run the same on the Mac and in WSL.

- `docs/STATUS.md` held a hand-written Active block. Each merge needed a follow-up commit to replace it. The block named the branch and the Ghidra writer by hand, so it was wrong on the machine that did not write it.
- The facts of the block already exist elsewhere: git (branch), GitHub (pull requests, issues, last merge) and the process list (running jobs).
- Each machine has its own Ghidra project, rebuilt from `config/symbols.txt` (ADR-0002). Nothing shows whether a project is level with the file after a merge on the other machine.
- The scripts that run Ghidra default `GHIDRA_HOME` to the Mac path, so a Ghidra-writer task in WSL needs an override for each of them.

## Decision

### Generated session state (R2)

1. `docs/STATUS.md` keeps the intro and the milestone table. It has no Active block. Git history keeps the old blocks.
2. `tools/session-start.sh` prints the state, one line or short list for each source:

   | Line | Source |
   | --- | --- |
   | Branch and uncommitted count | `git` |
   | ghidra-mcp up or down | `curl` to port 8089 |
   | Running processes | `pgrep` for the ghidra-mcp server, `analyzeHeadless` and `tools/delink.sh` |
   | Ghidra writer | `gh issue list --label ghidra-writer --state open --assignee '*'` |
   | Open pull requests | `gh pr list` |
   | Assigned open issues | `gh issue list --assignee @me` |
   | Next command | `agent-skills next` |
   | Last merged pull request | `gh pr list --state merged --limit 1` |
   | Open and active findings | `bodecomp.findings summary` |

3. The hook prints 40 lines or fewer and exits with 0. Each list has a cap. When `gh` or `agent-skills` is missing, offline or not signed in, the hook prints one line for the source and goes on.
4. The hook keeps each `gh` and `agent-skills` answer for 60 seconds in `~/.cache/bodecomp-hook/`. Measured on 2026-11-17 in WSL with `gh` online and no cache, the hook took 3.6 s, and 8.6 s in one other run. `agent-skills next` alone took 1.9 s. With the cache the hook took 0.14 s. The limit in the spec was 3 s.
5. The `ghidra-writer` label names the Ghidra writer. The Plan stage puts it on each task that changes the Ghidra project. The assignee of the open task is the lock. At most one open task with the label is assigned. The hook prints a warning when two are.
6. A Ghidra-writer task may change only what a tracked text file records. Any other change in Ghidra is scratch and is lost on a rebuild (ADR-0002).
7. The old Evidence line moves to the Verification section of the pull request. The hook prints the last merged pull request only.

### Ghidra freshness (R3)

8. `bodecomp.sync check` writes the git-ignored file `ghidra/.sync-stamp` when it ends with 0 differences both ways. The file holds the SHA-256 of `config/symbols.txt` and the SHA-256 of its `function` lines. No other command writes it.
9. The hook compares the stamp with the current `config/symbols.txt`, reads files only, and prints one line: level, no stamp, behind on functions (rebuild), or behind on names (`sync apply`, then `sync check`).
10. The scripts that run Ghidra find it on both machines from one shared default (Homebrew on the Mac, Linuxbrew in WSL). `GHIDRA_HOME` stays as an override. `.mcp.json` is untracked and git-ignored, and each machine keeps its own copy with its own path to `uv`.

Tasks T3 to T9 of issue #56 implement these points. T3 implements points 1 to 7. T7 adds the stamp line of point 9.

## Amendments

- ADR-0003: the Ghidra writer is named by the `ghidra-writer` label and its assignee on GitHub, not by an Owners line in `docs/STATUS.md`.
- ADR-0007: the SessionStart hook prints the generated state of point 2, not the Active block.
- ADR-0019: the Active block is gone. Its fields (Branch, Running, Owners, Evidence, Blockers, Next action) are replaced by the lines of point 2 and by the Verification section of the pull request.

## Consequences

- After a merge, `git status` is clean and no follow-up commit is needed.
- The state in the hook is as old as 60 seconds. An agent that must be sure, such as the `namer`, queries GitHub itself.
- The hook depends on `gh` and `agent-skills`. It still works without them.
