# Draft of the overnight prompt

Two drafts. Prompt A is for the repo after the tasks of [10-overnight-design.md](10-overnight-design.md), section 5, rows 1 to 4. Prompt B needs no change to the repo and has known gaps. Neither was run. The rehearsal of R10 is the test.

Both are one `/goal` command. `/goal` starts the first turn with the condition as the instruction, so no second prompt is needed ([09-claude-code.md](09-claude-code.md), section 2). The limit for a condition is 4,000 characters. Prompt A has 2588 and prompt B has 3770 (Computed, without the `/goal` word).

## How to start

    tmux new -s night
    cd ~/code/bustin-out-recomp
    claude --permission-mode auto --settings config/overnight-settings.json

Then paste the prompt. For prompt B, leave out `--settings`: the file does not exist yet. Change `8 hours`, `8h`, `480` and `410` for another length (410 is 85 percent of 480).

Before the night: the Ghidra project must be fresh. On 2026-11-24 the session hook prints "function starts changed, run tools/rebuild-ghidra.sh" and "ghidra-mcp: down". With that state both prompts stop in their first check, which is the intended result.

## Why the prompt is written this way

| Part | Reason | Source |
| --- | --- | --- |
| "Nobody will answer a question" | Runs ended with a question to a user who was not there | 08, section 4, item 1 |
| The clock is a command, and its output is printed in full | The judge of `/goal` reads only the conversation | 09, section 2 |
| The end state is one command's output | A condition needs one measurable end state and a stated check | 09, section 2 |
| Standing permissions name each action | In auto mode an approval covers one action unless it is granted as standing, and it must name the action | `https://code.claude.com/docs/en/permission-modes` "so a later action is blocked again unless you granted the approval as standing." |
| The "not permitted" list | The classifier treats a stated limit as a block signal. A compaction can drop it, so R5 repeats the list as deny rules | 09, section 4 |
| "Do not try the same action in another form" | Three blocks in a row stop an interactive auto-mode session | 09, section 3 |
| Rules by reference to `docs/WORKFLOW.md` | The lead can read a file again after a compaction. A long prompt is summarized | 09, section 5 |
| "Read it again after each compaction" | `AGENTS.md` is loaded again from disk, and other files are not | 09, section 5 |
| Stop rules with numbers (three batches, two starts) | A run with no stop rule repeats a broken step all night | 03, section 8 (dx-ball has none) |

## Prompt A (after R1 to R9 are built)

    /goal Work unattended for 8 hours on matcher batches, as docs/WORKFLOW.md ("An unattended run") and ADR-0023 say. Read that section first, and read it again after each compaction.

    Nobody will answer a question or grant a permission during this run. Never end a turn with a question. For a choice that the documents do not decide, take the option that changes less and write a "GUESS:" line in build/overnight/journal.md. For a thing that only the user can do, write a "USER:" line there and continue with other work.

    Steps:
    1. Run "uv run python -m bodecomp.overnight preflight". If it prints "preflight: fail", fix only what docs/WORKFLOW.md lets you fix (start the ghidra-mcp server), run it once more, and if it still fails run "uv run python -m bodecomp.overnight finish" and stop.
    2. Run "uv run python -m bodecomp.overnight start 8h".
    3. Repeat: run "uv run python -m bodecomp.overnight status" and print its output in full. If it prints "wrap up" or "remaining: 0m", go to step 4. Otherwise run one matcher batch as the section says: candidates, worktree from the run branch, one matcher, one reviewer, gate, merge into the run branch, push, journal line.
    4. Run "uv run python -m bodecomp.overnight finish" and print its output in full. Put the journal in the body of the pull request.

    Standing permissions for this run, which I grant now for every batch: create and remove git worktrees next to this checkout, commit, merge batch branches into the run branch match/night-<date> with a merge commit, push that run branch to origin, open one draft pull request for it, open issues labeled needs-triage, start tools/ghidra-mcp-headless.sh, and reset the run branch to the commit before a batch whose gate failed.

    Not permitted in this run: a push to main, a merge of the pull request, a force push, tools/rebuild-ghidra.sh, tools/delink.sh, tools/create-functions.sh, a write to the Ghidra project, names set, sync apply, a change to an issue's state label, more than one matcher at a time, and a change to any file that the section does not name.

    This goal is met when the conversation shows, after the last batch, the full output of "uv run python -m bodecomp.overnight finish" with the line "gate: pass" or "gate: fail" and the URL of the pull request. It is not met before the newest output of "uv run python -m bodecomp.overnight status" shows "wrap up" or "remaining: 0m", unless preflight failed twice, three batches in a row failed the gate, or the server failed to start twice. In each of those three cases the goal is met when the output of finish is shown with the reason.

## Prompt B (works with the repo as it is today)

Gaps of prompt B against the design: no deny rules, so the "not permitted" list is only text. No `status` command, so the stall of a matcher is not detected. No hook line, so after a compaction the lead depends on the goal text and the journal. The branch name `match/night-<date>` does not follow `docs/agents/workflow.md`. The prompt runs many batches in one session, which `docs/agents/workflow.md` line 5 does not allow today: the user's prompt is the permission for it.

    /goal Work unattended on matcher batches until 8 hours have passed since the start time that you record in step 1. Nobody will answer a question or grant a permission during this run. Never end a turn with a question.

    Rules: AGENTS.md, docs/WORKFLOW.md ("Matching", "A matcher's worktree", "End of a batch") and .claude/agents/matcher.md. Read them first and again after each compaction, and read build/overnight/journal.md after each compaction.

    Steps:
    1. If build/overnight/start does not exist: run "mkdir -p build/overnight && date +%s > build/overnight/start". If it exists, do not change it.
    2. Check the start state: no tracked file has an uncommitted change; "curl -s http://127.0.0.1:8089/check_connection" answers (if not, run tools/ghidra-mcp-headless.sh and check again); "uv run python -m bodecomp.sync freshness" reports no change; the gate "uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check" passes. If one check still fails, write the output to build/overnight/journal.md, print it and stop: the goal is then met. If all pass and the run branch does not exist, make the branch match/night-$(date +%F) from main and switch to it.
    3. Repeat. First print the elapsed time: echo "elapsed $(( ($(date +%s) - $(cat build/overnight/start)) / 60 )) of 480 minutes". At 410 minutes or more, go to step 4. Otherwise run one batch: "uv run python -m bodecomp.match candidates 20 --min-size 17"; a worktree from the run branch with the recipe of "A matcher's worktree"; one matcher agent; one reviewer agent; set back each function that the reviewer fails; merge the batch branch into the run branch with a merge commit; run the gate; add the row to docs/m4-results.md; write the findings of the reports to docs/FINDINGS.md; commit; "git push -u origin" the run branch; append one line to build/overnight/journal.md with the functions given, matched and parked. After the first push, open one draft pull request for the run branch.
    4. Run the gate and "uv run python -m bodecomp.ledger" one last time, commit, push, put the journal in the pull request body, and print the gate output, the count of matched and parked functions of the run and the pull request URL.

    When things go wrong: retry a failed tool once, then look in docs/FINDINGS.md and run "papercut find <words>", then skip the batch. If the gate fails after a merge and one repair does not fix it, reset the run branch to the commit before that merge, keep the batch branch, write a journal line and take the next batch. Stop the run with step 4 after three failed batches in a row or two failed starts of the server. For a choice that the documents do not decide, take the option that changes less and write a "GUESS:" line in the journal. For a thing that only I can do, write a "USER:" line and continue. If a permission is refused, do not try the same action in another form: write a "USER:" line and take the next batch.

    Standing permissions, granted now for every batch of this run: create and remove git worktrees next to this checkout, commit, merge batch branches into the run branch, push the run branch to origin, open one draft pull request, start tools/ghidra-mcp-headless.sh, reset the run branch as described above.

    Not permitted: a push to main, a merge of the pull request, a force push, tools/rebuild-ghidra.sh, tools/delink.sh, tools/create-functions.sh, any write to the Ghidra project, names set, sync apply, a change to an issue label, more than one matcher at a time.

    The goal is met when the conversation shows an elapsed line of 410 minutes or more and, after it, the output of step 4 with the gate result and the pull request URL, or when step 2 or the stop rule ended the run and its output is shown.

## After the night

1. `tmux attach -t night`: the last lines show the gate result and the pull request.
2. Read the pull request body: the `USER:` lines need an answer, and the `GUESS:` lines need a check.
3. `uv run python -m bodecomp.match --check` on the run branch, then review and merge (decision D1 of the design: the user merges for now).
4. Remove the night worktrees with `git worktree remove` and delete `build/overnight/` so that the next run starts a new clock.
