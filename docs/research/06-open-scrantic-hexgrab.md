# open-scrantic and hexgrab

Sources: the clones of glauberlima/open-scrantic (`~/git/glauberlima/open-scrantic`, HEAD `c47652c`) and iammukeshm/hexgrab (`~/git/iammukeshm/hexgrab`, HEAD `511c580`). Citations use the prefixes `open-scrantic/` and `hexgrab/`.

Neither repo has a loop, a queue, a hook or a resume file. They are in this research for one mechanism each: how open-scrantic lets a check pass with no data, which is a fault to avoid, and how hexgrab scores findings against ground truth.

## open-scrantic

### What it is

- `open-scrantic/AGENTS.md:7` "A reverse-engineered Rust reimplementation of" the 1992 Johnny Castaway screensaver. It reads the user's original files at run time: `open-scrantic/AGENTS.md:10` "Never commit screensaver data"
- History (Computed): 128 commits from 2026-10-16 to 2026-11-12, 92 of them on three days. 111 commits carry a Claude trailer (Sonnet 5.5 on 109 trailer lines). 30 commits carry a `Claude-Session` line with 10 distinct session IDs.
- The first commit holds the finished engine in 22 files: `ab74bc4` "feat: reimplement Johnny Castaway engine in Rust". How the analysis went before it is UNVERIFIED.

### Agent setup

- `open-scrantic/CLAUDE.md:5` "@AGENTS.md" is the whole `CLAUDE.md`, the same pattern as this repo (ADR-0015).
- Two nested `CLAUDE.md` files hold notes for one folder each (`src/assets/CLAUDE.md`, `src/engine/CLAUDE.md`), so they load only when the agent works there.
- Rules: `open-scrantic/AGENTS.md:15` "Code comments cite original addresses" and `open-scrantic/AGENTS.md:39` "reproduce the original 16-bit arithmetic"
- No rule about autonomy, stopping or asking (Computed: `rg --hidden -n -i 'autonom|unattended|keep going|stop|budget|ask' AGENTS.md CLAUDE.md src/assets/CLAUDE.md src/engine/CLAUDE.md` finds no such rule).
- `.recomp.json` is a catalog card for a web site, not agent configuration: `31e94ce` "docs: add .recomp.json so the project is listed on recomp.fyi (#8)". `.codegraph/` holds one ignore file for a local code index: `open-scrantic/.codegraph/.gitignore:1` "# CodeGraph data files" How an agent uses that index is UNVERIFIED.

### Reverse engineering evidence

- No Ghidra file, no REA file, no disassembly listing and no MCP configuration is in the repo (Computed: `rg --hidden -n -i 'ghidra|mcp' -g '!.git' .` prints nothing).
- REA is named in prose only: `open-scrantic/README.md:346` "[REA: Reverse Engineer Anything](https://rea.tools/), a reverse-engineering toolkit"
- The analysis lives on as address comments and one notes file: `open-scrantic/docs/ENGINE.md:51` "Catalog of 80 scenes at `DS:1756`" Every address is UNVERIFIED from the repo.
- The notes record dead ends and limits: `open-scrantic/docs/ENGINE.md:143` "**Ruled out.**" and `open-scrantic/docs/ENGINE.md:141` "(static analysis; the original was not run)"

### The gate, and its fault

- Local gate: `open-scrantic/CONTRIBUTING.md:22` "cargo clippy --all-targets", `open-scrantic/CONTRIBUTING.md:23` "cargo fmt --check", `open-scrantic/CONTRIBUTING.md:24` "OPEN_SCRANTIC_DATA=/path/to/install cargo test"
- The tests that need the original files pass when the files are absent: `open-scrantic/AGENTS.md:26` "data-dependent tests silently pass without it"
- CI never sets the variable (Computed: `rg -n 'OPEN_SCRANTIC_DATA' .github/workflows` prints nothing). So in CI every such test returns early and passes.
- The check against the original is a section of the pull request form that a person fills in: `open-scrantic/.github/PULL_REQUEST_TEMPLATE.md:5` "## How it was checked against the original"
- A snapshot tool writes images and nothing compares them: `open-scrantic/examples/snapshot.rs:1` "//! Headless run: steps the engine with a fixed wall clock and saves PNG snapshots."

### For this repo

This repo has the same shape of risk. `docs/METHODOLOGY.md` ("Testing the tools") says that the tests which compile with VC71 are skipped when `tools/xdk/` and `tools/wibo` are not set up. In a new worktree those folders are absent until the links of `docs/WORKFLOW.md` ("A matcher's worktree") exist. A green `pytest` there proves less than it seems to. The pre-flight step of the overnight design (R4) fails the run when the inputs are missing, so a skip cannot pass for a check.

## hexgrab

### What it is

- A small Windows color picker written from REA findings about the PowerToys Color Picker: `hexgrab/README.md:9` "hexgrab is a learning project."
- 2 commits, 4 hours 53 minutes apart, on 2026-10-12 and 2026-10-13 (Computed). No trailer and no model name. The findings file names the agent: `hexgrab/docs/rea-findings.md:3` "Investigation done 2026-10-12 with REA 6.4.0"
- No agent instruction file, no CI and no hook (Computed: `git ls-files | rg -i 'agents|claude|cursor|codex|skill|prompt|github|workflow|pre-commit'` prints nothing).

### The report card method

The method is in `docs/rea-findings.md`.

1. State the findings from the binaries only: `hexgrab/docs/rea-findings.md:23` "## Findings (from binaries only)"
2. Name the ground truth, the public source at the same version: `hexgrab/docs/rea-findings.md:42` "## Scorecard vs real source (microsoft/PowerToys @ v0.98.0, MIT)"
3. Make one row per claim with the source location and a verdict: `hexgrab/docs/rea-findings.md:44` "| REA claim | Source | Verdict |"
4. Count: `hexgrab/docs/rea-findings.md:56` "**8 of 9 fully correct, 1 partly correct.**"
5. Use the source only for grading: `hexgrab/docs/rea-findings.md:58` "The public source was only used to grade REA."

The one miss: `hexgrab/docs/rea-findings.md:50` "Partly - the module handles it, the runner registers it" The author's cause: the binary that registers the hotkey was not analyzed (`hexgrab/docs/rea-findings.md:56` "The miss is a classic static-analysis blind spot"). This is the author's statement of the cause.

Weak points, all from the file itself:

- 5 of the 11 findings have no row in the table (lines 29, 35, 36, 39 and 40), for example `hexgrab/docs/rea-findings.md:35` "- **Low-level mouse hook**" The README says more than the table shows: `hexgrab/README.md:11` "because its source is public I could check every REA finding against the real code."
- The claim that missed is not in the findings list. It appears first in the table. So it was written at grading time.
- One row counts as correct although REA did not find its numbers: `hexgrab/docs/rea-findings.md:53` "counts not recovered from call edges alone"
- The PowerToys source is not in the repo, so no verdict can be checked from the clone. UNVERIFIED.
- The end-to-end script has no exit statement, so a failed check does not change its exit code: `hexgrab/tests/e2e/hexgrab-e2e.ps1:33` "function Check($name, $ok, $detail)"

### For this repo

This repo has a ground truth of the same kind for names and types: the GameCube decomp (daftblazer/bustin-out-decomp). The hexgrab method, done strictly, is a cheap test of an agent's analysis:

1. The agent writes its claims about a function first, with addresses, to a file.
2. A second step compares each claim with the donor source and gives a verdict.
3. Every claim gets a row. A claim with no row counts as not checked.

`.claude/agents/matcher.md` already has a rule of this kind for parked functions: compile the donor's form and report its score (F-0093, F-0101). The overnight design does not add a new scorecard. It keeps that rule and has the reviewer fail a park with no donor score, as `.claude/agents/reviewer.md` already does.
