# baocut

Source: the clone of JimLiu/baocut at `~/git/JimLiu/baocut`, HEAD `72f6b2c8` (2026-11-23). Citations with the prefix `baocut/` point into that clone. Most agent rules in this repo are in Chinese. Repo documents here are ASCII only, so a Chinese line is cited as path and line with an English translation in parentheses and no quote. A line cited that way was read, and the quote check does not cover it.

## Summary

- The repo is a video editor that agents drive. It is not a reverse engineering project, and it has no Ghidra, REA or MCP analysis setup.
- The video's claim is about a slides editor that lived in this repo for 44 days and was removed on 2026-11-23. The repo never names REA.
- The repo has no mechanism for long unattended work. Its one stop rule tells the agent to stop and ask a human.
- Two things are worth taking: the design text of a stall watchdog for the product's own "bot mode", and a rule to archive unmerged work before deleting it.

## 1. What it is

- `baocut/README.md:8` "The video editor built for agents."
- `baocut/package.json:5` "BaoCut: an AI video agent with an editable video at the center"
- History (Computed): 1,683 commits from 2026-10-07 to 2026-11-23.
- REA, Ghidra, "reverse engineer" and "decompile" appear in no file and in no commit message (Computed: `git log --all -i -E --grep='ghidra|reverse[ -]engineer|decompil|deobfuscat|\bREA\b' --format='%h %s'` prints nothing).
- The slides editor came in with commit `b8585e0c` "feat(slides): create, edit and annotate slides from agent sessions" (2026-10-10). Its body says the runtime is "adapted from the Claude" Slides implementation. Commit `351fed54` "feat(artifacts): integrate Open Artifact and remove built-in slides, docs and design editors" (2026-11-23) removed it.
- The removed package's notes describe restoring minified JavaScript, not analyzing a binary (`baocut/351fed54^:packages/design-runtime/README.md:50`: some identifiers were bound wrongly when the code was restored from compressed code). A count of matched functions in the same file (line 61: 19,111 of 20,463) has no script or log in any tree. UNVERIFIED.
- Which agent did that restoration is UNVERIFIED. No file or commit names it. The community list has the claim only from the author's post ([08-lists-and-experiments.md](08-lists-and-experiments.md)).
- Models: 127 trailer lines name Claude Opus 5.5, the first on 2026-10-31 (Computed: `git log --format=%B | rg -c "Co-Authored-By: Claude Opus 5.5"`). Codex shows only as branch names and one line: `baocut/.agents/skills/bcut-release/references/traditional-release.md:77` "open it in the Codex browser when useful"

## 2. Agent setup

- One `AGENTS.md` of 51 lines and exactly 6,000 bytes (Computed). The file sets its own cap (`baocut/AGENTS.md:9`: keep the root file short, at most 80 lines and 6 KB). No test enforces the cap.
- One release skill: `baocut/.agents/skills/bcut-release/SKILL.md:3` "description: Release BaoCut Electron desktop apps through GitHub Actions tags by default"
- `.claude/` holds only `launch.json`. No hook, no settings file, no subagent definition, no `CLAUDE.md` (Computed by listing the tracked files).
- Subagents worked in worktrees: `baocut/AGENTS.md:51` "`.claude/worktrees/agent-*`" and `baocut/.gitignore:21` ".claude/worktrees/"

Rules that bear on autonomy:

- Each task that changes files ends with a commit (`baocut/AGENTS.md:43`: an implementation task that changes files must create a git commit before the final reply).
- The agent chooses its checks (`baocut/AGENTS.md:46`: review the final diff before the commit and run a fitting amount of verification for the risk).
- A check that cannot run is reported, not retried (`baocut/docs/development-workflow.md:82`: when a check needs a toolchain, model, credential or platform that is missing, report the skipped item and the reason).
- Complex or irreversible work stops for a human (`baocut/docs/development-workflow.md:99`: complex or irreversible, stop and confirm). An unattended run cannot follow this rule.
- A skill forbids a silent fallback: `baocut/.agents/skills/bcut-release/SKILL.md:22` "Do not silently fall back to traditional packaging after an Actions failure."
- Unmerged worktree work gets an archive tag before removal (`baocut/AGENTS.md:51`: tag it `archive/<worktree name>` first).

## 3. Gates

- CI only: `baocut/.github/workflows/tests.yml:41` "run: npm run typecheck", `baocut/.github/workflows/tests.yml:49` "run: npm test" and `baocut/.github/workflows/tests.yml:93` "run: cargo test --locked --workspace"
- CI runs after a push. No hook runs before a commit.
- A check that the docs list is off in CI: `baocut/.github/workflows/tests.yml:87` "# TODO: re-enable `cargo fmt --all -- --check` once the whole tree has been"

## 4. Long runs

- Cadence (Computed): 78 percent of gaps between commits are under 30 minutes. The longest run of non-bot commits with every gap under 30 minutes is 6.9 hours and 60 commits. Almost all commits carry the human's name, so the agent's share cannot be measured.
- Not found: a resume file, a handoff note, a retry rule, a time or budget limit.

The product's "bot mode" has a design for unattended agent threads (`docs/design/bot-mode/bot-mode-technical-design.md`). It is design text for the product. That the developers ran their own coding agents under it is UNVERIFIED.

- A watchdog scans once a minute (line 674).
- A thread with no progress for `stallMinutes`, 20 by default, is stalled (line 676).
- A job that runs for twice its expected time with no new progress is hung (line 677).
- At 80 percent of the budget the thread gets one warning (line 678).
- A stalled thread is told to read its working notes and to change its approach (line 680).
- Each thread has a notes file inside its working folder, so the sandbox lets the agent write it with no approval: `baocut/docs/design/bot-mode/bot-mode-technical-design.md:470` "`files/.threads/<threadId>/working-notes.md`"

## 5. What to take

| Mechanism | Verdict | Where it goes in this repo |
| --- | --- | --- |
| "No progress for N minutes" as the stall signal | Take | The `status` command of [10-overnight-design.md](10-overnight-design.md) (R2) prints the minutes since the last commit on the run branch |
| One warning at 80 percent of the budget | Take | The same command prints `wrap up` at 85 percent of the time |
| A notes file that the agent can write with no approval | Take | `build/overnight/journal.md` (R3) |
| Archive tag before deleting unmerged work | Take | R6, step 4: a batch that fails the gate gets an `archive/` tag |
| "Stop and confirm" for irreversible work | Replace | R7: write a `USER:` line to the journal and take the next batch |
| The agent chooses its checks | Do not take | This repo's gate is fixed (`AGENTS.md`, "Every task") |
