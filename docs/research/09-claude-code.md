# Claude Code facts for an unattended run

Source: the official Claude Code documentation at `https://code.claude.com/docs/en/`, fetched as Markdown on 2026-11-24. Each fact gives the page and a quote. Markdown links and code marks are removed from the quotes. Claude Code on this machine is version 2.1.331 (`claude --version`), which is later than every version that the quotes name.

This page holds only the facts that the design in [10-overnight-design.md](10-overnight-design.md) uses. Two facts change what this repo does today, and they come first.

## 1. Two settings in this repo that do not do what they seem to do

The working tree of the main checkout has an uncommitted change to `.claude/settings.json`. It adds `"defaultMode": "auto"` under `permissions` and a `sandbox` block with `"autoAllowBashIfSandboxed": true` (`git diff .claude/settings.json` on 2026-11-24).

1. `defaultMode: auto` has no effect in a project file. `https://code.claude.com/docs/en/settings` "permissions.defaultMode values auto and bypassPermissions don't take effect from project or local settings; set them in user or managed settings instead, or pass --permission-mode for one session."
2. The sandbox block does not turn the sandbox on. The switch is a different key. `https://code.claude.com/docs/en/permission-modes` "To turn the sandbox on from a settings file instead, set sandbox.enabled and sandbox.autoAllowBashIfSandboxed to true" With no `sandbox.enabled`, the default applies: `https://code.claude.com/docs/en/settings-reference` "Default: unset, so Claude Code runs commands without a sandbox"

So a session in this repo starts in Manual mode with no sandbox, with or without that change. R5 of the design says what to set and where.

## 2. What keeps a session going

Three mechanisms exist. `https://code.claude.com/docs/en/goal` "Three approaches keep the current session running between prompts."

### `/goal`

- `https://code.claude.com/docs/en/goal` "After each turn, a model checks whether the condition holds."
- It is a Stop hook made for one session: `https://code.claude.com/docs/en/goal` "/goal is a wrapper around a session-scoped prompt-based Stop hook."
- The judge reads the conversation and nothing else: `https://code.claude.com/docs/en/goal` "It doesn't run commands or read files independently, so write the condition as something Claude's own output can demonstrate."
- A good condition has `https://code.claude.com/docs/en/goal` "One measurable end state" and `https://code.claude.com/docs/en/goal` "A stated check". The limit is `https://code.claude.com/docs/en/goal` "The condition can be up to 4,000 characters."
- Time: `https://code.claude.com/docs/en/goal` "To bound how long a goal runs, include a turn or time clause in the condition, such as or stop after 20 turns. Claude reports progress against that clause each turn and the evaluator judges it from the conversation." So the clock must appear in the conversation. The judge does not read a clock.
- It does not grant permissions: `https://code.claude.com/docs/en/goal` "A goal doesn't change your permission mode."
- It stops by itself when the agent makes no progress: `https://code.claude.com/docs/en/goal` "If Claude keeps answering the evaluator without making progress (no tool use for several turns in a row), Claude Code stops the loop, prints a warning, and returns control to you with the goal still set."
- It ends on "impossible": `https://code.claude.com/docs/en/goal` "the evaluator judged that the condition can never be satisfied."
- It survives a restart of the session: `https://code.claude.com/docs/en/goal` "When you resume a session, Claude Code restores a goal that was still active when the session ended." and `https://code.claude.com/docs/en/goal` "Claude Code carries the condition over but resets the turn count, timer, and token-spend baseline."
- `/clear` removes it: `https://code.claude.com/docs/en/goal` "Running /clear to start a new conversation also removes any active goal."

### Background work and the goal

- `https://code.claude.com/docs/en/goal` "If a subagent or a background shell command is still running when a turn ends, Claude Code skips the evaluation for that turn."
- `https://code.claude.com/docs/en/goal` "When the background work finishes, Claude Code delivers the result to Claude as a new turn"
- After 30 minutes of waiting the lead gets a check-in: `https://code.claude.com/docs/en/goal` "Once background work has kept the goal waiting for 30 minutes, a check-in is due."
- In an interactive session there are at most three such check-ins while nobody types: `https://code.claude.com/docs/en/goal` "Claude Code starts at most three idle check-ins per goal between your prompts." The intervals are 30 minutes, then 1 hour, then 2 hours (same paragraph), so three check-ins cover 3.5 hours of one unbroken wait. A matcher batch is far shorter than that. A subagent that hangs for hours is the case to guard against, with `maxTurns` (section 6).

### Errors and usage limits

- `https://code.claude.com/docs/en/goal` "After three automatic retries, the goal pauses instead." This is for failures that tend to clear, such as an overloaded server.
- A usage limit pauses the goal, and the session continues after the reset: `https://code.claude.com/docs/en/goal` "If the session is waiting to continue automatically when a usage limit resets, Claude resumes work toward the goal then."
- That waiting is a feature of interactive sessions: `https://code.claude.com/docs/en/interactive-mode` "Automatic continue is on by default in interactive sessions signed in with a claude.ai subscription."
- The machine must stay awake: `https://code.claude.com/docs/en/interactive-mode` "if it slept for more than about 30 minutes and the limit reset while it slept", a person must press Enter.
- ADR-0010 of this repo records that five namer batches used up a 5-hour usage window in about an hour. So a usage limit during an 8-hour run is likely, and the wait counts against the 8 hours.

### A Stop hook of your own

- A command hook can block the stop: `https://code.claude.com/docs/en/hooks` "Prevents Claude from stopping, continues the conversation"
- It gets these fields: `https://code.claude.com/docs/en/hooks` "Stop hooks receive stop_hook_active, last_assistant_message, background_tasks, and session_crons."
- A loop guard exists: `https://code.claude.com/docs/en/hooks` "Claude Code applies an 8-consecutive-continuation cap: after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn. The count of consecutive continuations resets each time Claude calls a tool."
- A hook gets no clock. The common input fields are `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir`, `permission_mode`, `effort` and `hook_event_name` (the table under "Common input fields" on the hooks page). A script reads the time itself.

The design uses `/goal` and no Stop hook. Section 2 of the design gives the reason.

## 3. Interactive session or `claude -p`

| Question | Interactive session | `claude -p` |
| --- | --- | --- |
| A usage limit | Waits and continues (above) | Not stated on the pages read. UNVERIFIED |
| Auto mode blocks an action 3 times in a row or 20 times in all | `https://code.claude.com/docs/en/permission-modes` "auto mode pauses and Claude Code resumes prompting." The session then waits for a person | `https://code.claude.com/docs/en/permission-modes` "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't stop the run." |
| Background subagents when the lead's turn ends | The session stays open | `https://code.claude.com/docs/en/headless` "Claude Code stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result." The cap is `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, and `0` removes it |
| Goal check-ins | Also while idle | `https://code.claude.com/docs/en/goal` "In a non-interactive session, such as one started with -p, this is the only way Claude Code delivers check-ins." (at the end of a turn) |
| With no mode given | The mode of the settings | `https://code.claude.com/docs/en/permission-modes` "Calls needing approval are denied unless you approve them with an allow rule, hook, canUseTool callback, or --permission-prompt-tool." |
| `/goal` | Works | `https://code.claude.com/docs/en/goal` "Setting a goal with -p runs the loop to completion in a single invocation:" |

The 10-minute cap of `-p` is the cause of the open papercut on this machine, "claude -p stops a background subagent 10 minutes after the lead's last turn". The documentation is the evidence.

The design uses an interactive session in a terminal multiplexer, because the usage limit is the most likely interruption and only the interactive session is documented to wait for it. The cost is the first row of auto mode: three blocked actions in a row stop the night. R5 lowers that risk with allow and deny rules.

## 4. Permissions for a night

- Auto mode: `https://code.claude.com/docs/en/auto-mode-config` "lets Claude Code run without routine permission prompts by routing tool calls through a classifier that blocks what it judges irreversible, destructive, or aimed outside your environment."
- What it trusts by default: `https://code.claude.com/docs/en/auto-mode-config` "By default, the classifier trusts only the working directory and the current repo's configured remotes." The reference clones in `~/git` and the scratch folder in `~/tmp` are outside the working directory.
- A push of a branch and a pull request pass: `https://code.claude.com/docs/en/permission-modes` "Pushing to any branch of the repository you're working in and creating a pull request that matches your request run without a prompt"
- A limit that is stated only in the prompt can be lost: `https://code.claude.com/docs/en/permission-modes` "Boundaries are not stored as rules. The classifier re-reads them from the transcript on each check, so a boundary can be lost if context compaction removes the message that stated it." The fix is on the same page: `https://code.claude.com/docs/en/permission-modes` "To keep the boundary from being lost, add a deny rule instead."
- `https://code.claude.com/docs/en/permission-modes` "Deny rules block in every mode, including bypassPermissions."
- A subagent in the background that needs a permission asks in the lead's session: `https://code.claude.com/docs/en/sub-agents` "When a background subagent reaches a tool call that needs permission, Claude Code surfaces the prompt in your main session and names the subagent that is asking." With nobody there, that subagent waits. The matcher and the reviewer need allow rules for what they run.
- The sandbox works on this platform: `https://code.claude.com/docs/en/sandboxing` "The sandbox runs on macOS, Linux, and WSL2." `bubblewrap` 0.11.1 and `socat` 1.8.1.1 are installed here (`dpkg -l bubblewrap socat`). Whether the VC71 compiler under wibo, `uv`, `gh` and the ghidra-mcp bridge run inside the sandbox is UNVERIFIED. It was not tried.

## 5. Context over 8 hours

- Compaction keeps the entry file: `https://code.claude.com/docs/en/memory` "Project-root CLAUDE.md survives compaction: after /compact, Claude re-reads it from disk and re-injects it into the session."
- The session-start hook of this repo runs again after a compaction (the row "SessionStart hooks that match the compact source" in the table "What survives compaction" on the `context-window` page: Claude Code runs them and adds their output to the compacted context). `.claude/settings.json` gives the hook no matcher, so it matches every source. ADR-0007 already relies on this.
- Text that a hook added earlier is only summarized (same table, row "Context that hooks added earlier"). So state that must survive has to be printed again by the hook, or read again from a file.
- Background subagents survive a compaction (same table: they keep running).
- A "Compact instructions" section in `CLAUDE.md` is not on the pages read. Whether Claude Code gives such a section a special role is UNVERIFIED.

## 6. Subagents

- Custom subagents start in the background: `https://code.claude.com/docs/en/sub-agents` "With nothing configured, a subagent other than web-fetch that Claude spawns from your main conversation starts in the background."
- The frontmatter of an agent file accepts, among others, `model`, `tools`, `maxTurns`, `permissionMode`, `background` and `isolation` (the table "Supported frontmatter fields").
- `maxTurns`: `https://code.claude.com/docs/en/sub-agents` "Maximum number of agentic turns before the subagent stops. When the subagent reaches the limit, Claude Code returns its output marked as partial, and Claude can resume it to continue."
- At most 20 run at one time: `https://code.claude.com/docs/en/sub-agents` "By default, when 20 subagents are running in a session, spawning another with the Agent tool fails with Concurrent subagent limit reached"
- A worktree that Claude Code makes for a subagent starts from the default branch, not from the lead's branch: `https://code.claude.com/docs/en/worktrees` "Subagent worktrees use the same base branch as --worktree, so they branch from your repository's default branch unless worktree.baseRef is set to" `"head"`. This repo makes matcher worktrees by hand (`docs/WORKFLOW.md`, "A matcher's worktree"), from the branch it names, so this default does not apply. Keep it that way. `isolation: worktree` in `.claude/agents/matcher.md` would start each matcher from `main` and without the five links to the ignored inputs.
- A subagent that an API error cuts off returns what it has: `https://code.claude.com/docs/en/sub-agents` "the Agent tool returns that partial output with a note that the subagent was cut off and didn't finish its task."

## 7. Timers that are not the driver

- `https://code.claude.com/docs/en/scheduled-tasks` "Tasks are session-scoped." A self-paced `/loop` picks `https://code.claude.com/docs/en/scheduled-tasks` "a delay between one minute and one hour".
- These fit polling, not a work loop. The design does not use them.

## 8. Guidance from Anthropic on long runs

The post "Effective harnesses for long-running agents" (`https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`) was fetched on 2026-11-24 and read. Its text has typographic quotes, so it is given here in other words and not quoted.

- It says that compaction alone is not enough for a long task.
- Its first session writes a setup script, a progress file (`claude-progress.txt`) and a first git commit. Each later session makes one step of progress and leaves the state in that file and in git.
- It keeps a JSON list of features, each with a `passes` field. The agent may change only that field, and must not remove or edit a test.
- Its subject is a web application built over many context windows by the Agent SDK. It does not test a decompilation, and it gives no figure for hours without a person.

The points agree with what this repo already does: `config/functions.csv` is the list, `bodecomp.match` is its only writer, and the session hook prints the state.
