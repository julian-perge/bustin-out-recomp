# REA and the bun setup of rea-agents

Source: the clone of morluto/rea at `~/git/morluto/rea`, HEAD `789ca0412` (2026-11-24), package version 6.10.1. Citations with the prefix `rea/` point into that clone. Bun facts cite the bun docs pages, fetched on 2026-11-24 (the pages show Bun v1.4.5). Nothing was installed and no REA, npm or bun command was run, so each statement about what bun does with this package is from documents, and the ones marked UNVERIFIED need one run to confirm.

## Summary

- REA is an MCP server and a CLI. It starts Ghidra headless, read-only, in a temporary project, and deletes the project when the session ends.
- REA has no layer that keeps an agent session going: no hook, no handoff file, no time budget, no stop rule. Its loop is the text of one skill.
- REA is not a replacement for ghidra-mcp in this repo. It has no XBE loader lane, and it has no tool that sets a type, a struct or a prototype. It can open a copy of an existing Ghidra project read-only, which is the one route to this repo's `ghidra/BustinOut.gpr`.
- The package installs with bun. It has no install script of its own. Its one optional native dependency, `frida`, has an install script that bun skips by default, and Ghidra analysis does not use frida.
- `rea setup` writes an absolute runtime path and an absolute script path into `~/.claude.json`. It does not write `npx` or `bunx`.
- The command in the video, `npx rea-agent-setup`, does not exist. The command is `rea-agents setup`.

## 1. What REA is

- `rea/package.json:5` "Reverse engineer anything from your terminal or agent with one CLI and MCP server."
- Scope: `rea/AGENTS.md:5` "REA is a local-only reverse-engineering tool with shared CLI/MCP workflows."
- Engines: `rea/README.md:225` "Deep native analysis uses Hopper, Ghidra, IDA or Kuna, depending on the target"
- History (Computed): 10,157 commits, 5,513 of them in 2026-10 and 3,825 in 2026-11 up to the 24th. About 2,030 commit bodies carry a Claude Opus 5.5 co-author trailer and 273 a Cursor Agent trailer. A trailer names a co-author. It does not show how much of a change the agent wrote.
- The maintainers keep their own agent settings out of git: `rea/.gitignore:25` "# Local agent tooling" So the clone does not show how they run their agents.
- A human owns each pull request: `rea/CONTRIBUTING.md:82` "Every PR must have a human owner who"

## 2. What REA ships for an agent

- One skill, `reverse-engineer-anything`, and four maintainer skills in `.agents/skills/`. The skill installed on this machine is an older copy: its text names `rea-agents@6.3.0` (`~/.claude/skills/reverse-engineer-anything/SKILL.md`, line 32), and the skill warns about such drift: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:27` "a skill installed from repository main may describe capabilities absent from"
- Plugin manifests for Claude Code, Codex and Cursor. The Claude Code plugin starts the server with node: `rea/.claude-plugin/plugin.json:21` "node" The Cursor entry uses npx: `rea/mcp.json:4` "npx"
- No hook, no slash command and no subagent definition (Computed: `rg --hidden -n '"hooks"|hooks\.json|SessionStart|PreToolUse|PostToolUse|"Stop"' .claude-plugin .codex-plugin .cursor-plugin .agents mcp.json server.json package.json AGENTS.md` prints nothing).

Skill rules that matter for an unattended session:

- Do not run setup or diagnostics first: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:25` "proceed directly to the target. Do not run diagnostics or setup before every"
- Do not repeat a call that cannot give a new result: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:379` "identical analysis or rejected call without a changed input or resolved blocker."
- After a timeout, do not send the same call again: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:36` "If the host times out without a REA result, do not repeat the unchanged call or"
- Label each conclusion: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:413` "Every conclusion must distinguish observations, inferences, and unknowns."
- For broad work, write a checklist first: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:428` "1. Turn the request into a checklist of questions and the evidence each answer"
- Keep a ledger: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:450` "7. Keep a concise finding ledger linking each conclusion to Evidence IDs,"
- Stop rule: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:454` "Before finishing, revisit the original checklist. Mark each question as"
- One rule asks a human: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:322` "ask which app before searching for artifacts." A prompt that names the target avoids it.

## 3. How REA configures and drives Ghidra

- REA does not install Ghidra or Java: `rea/docs/getting-started/installation.md:1410` "installs, upgrades, or modifies Ghidra or Java."
- Supported versions: `rea/docs/getting-started/installation.md:1196` "It accepts Ghidra 12.x (>=12.2) and the 64-bit full JDK declared by that installation"
- Paths come from two variables: `rea/docs/getting-started/installation.md:1289` "export GHIDRA_INSTALL_DIR=/absolute/path/to/ghidra_12.2_PUBLIC" and `rea/docs/getting-started/installation.md:1290` "export JAVA_HOME=/absolute/path/to/jdk-25"
- An explicit variable wins, also when it is wrong: `rea/docs/getting-started/installation.md:1381` "`GHIDRA_INSTALL_DIR` always takes precedence, including when it is invalid;"
- The run is headless, read-only, and the project is deleted: `rea/src/ghidra/GhidraLauncher.ts:1097` "-readOnly" and `rea/src/ghidra/GhidraLauncher.ts:1098` "-deleteProject"
- The bridge is a Ghidra post-script that stays alive: `rea/src/ghidra/GhidraLauncher.ts:1197` "options.bridgeScriptPath,"
- On Linux the bridge listens on a Unix socket: `rea/bridge/ghidra/ReaGhidraBridge.java:329` "ServerSocketChannel.open(StandardProtocolFamily.UNIX)"
- One program per session: `rea/docs/getting-started/installation.md:1533` "One session contains exactly one imported Program;" One request at a time: `rea/src/ghidra/GhidraRequestQueue.ts:32` "FIFO that admits one Ghidra Program request at a time."
- The heap setting: `rea/docs/getting-started/installation.md:1887` "nonempty setting in this order: `GHIDRA_HEADLESS_MAXMEM`, `GHIDRA_MAXMEM`, then"
- The startup deadline: `rea/docs/getting-started/installation.md:1466` "The provider startup deadline is 330,000 ms by default for import, analysis,"
- The client has its own, separate deadline: `rea/docs/reference/mcp-contracts.md:1851` "| Individual tool call | The client bounds its wait, including cold engine startup."
- Function starts that analysis misses can be given in a file: `rea/docs/getting-started/installation.md:1828` "export REA_GHIDRA_SEED_FILE=/absolute/path/to/seeds.tsv"

Where analysis state lives:

1. Default: nowhere. Each session imports and analyzes again: `rea/docs/getting-started/installation.md:1463` "In the default fresh-import mode, operations begin only after default auto-analysis completes." Edits end with the session: `rea/docs/getting-started/installation.md:1273` "session metadata edits leave executable bytes unchanged and are discarded on close."
2. An opt-in checkpoint keeps the analyzed program between processes: `rea/docs/getting-started/installation.md:1632` "export REA_GHIDRA_CHECKPOINT_DIR=/absolute/rea-checkpoints" It is keyed by the target hash: `rea/docs/getting-started/installation.md:1650` "Storage is separated by target SHA-256 and analysis-profile identity, including" A first analysis that did not finish cannot resume: `rea/docs/getting-started/installation.md:1668` "auto-analysis cannot resume midway. This does not restore a whole REA"
3. An existing Ghidra project can be the input. REA opens a copy: `rea/docs/getting-started/installation.md:1735` "and runs `-process <program> -noanalysis -readOnly`. Ghidra never opens or saves" The names in it are the caller's: `rea/docs/getting-started/installation.md:1748` "prior annotations or edits are caller-project state, not fresh REA discoveries."
4. The evidence ledger is in memory on the MCP connection: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:486` "history remain in memory on the same MCP connection. End the investigation with" It can be saved: `rea/.agents/skills/reverse-engineer-anything/SKILL.md:487` "`reset_investigation`; supply `save_path` to checkpoint the complete bundle before"

Limits for this repo:

- No XBE lane (Computed: `rg -n -i "xbe loader|XbeLoader|\.xbe\b|xbox" src bridge docs/providers docs/getting-started .agents` prints nothing). A GameCube DOL lane exists: `rea/docs/ghidra-dol.md:3` "This lane imports 32-bit big-endian PowerPC GameCube/Wii DOL images through" So REA can read the GameCube donor binary directly, and the Xbox binary only through route 3 above. Route 3 with this repo's project is UNVERIFIED: it was not run.
- No tool sets a type, a struct, a prototype or a comment (Computed: `rg -n -i "create_struct|set_function_prototype|set_data_type|apply_data_type|rename_function|set_comment" bridge/ghidra/ReaGhidraBridge.java` prints nothing). This repo's `namer` agent needs ghidra-mcp for that.
- REA matches functions between two binaries by name and bytes: `rea/docs/native-function-matching.md:3` "`match_native_functions` pairs two existing `list_procedures` Evidence inventories." It has no tool that compiles source and compares it with the original. That loop is in the showcase repos, not in REA.

## 4. Long work and recovery

REA recovers the Ghidra and MCP layers. It has nothing above them.

- A resumable export of all pseudocode is the one batch job with a journal: `rea/docs/guides/native/native-investigation.md:320` "`decompile-journal.jsonl` keeps earlier attempts and" One bad function does not stop it: `rea/docs/guides/native/native-investigation.md:341` "One function's decompiler error or deadline is counted and does not stop" Five write failures in a row stop it: `rea/docs/guides/native/native-investigation.md:358` "After five consecutive functions whose files" One run holds the output folder: `rea/docs/guides/native/native-investigation.md:355` "One run at a time holds an output directory,"
- A dropped connection gets one retry: `rea/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md:92` "- MCP connection dropped: retry that call once only when it is safe to repeat" Then the skill asks a human: `rea/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md:94` "it fails again, tell the user REA's connection failed and ask them to restart"
- A capacity error means wait, not restart: `rea/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md:105` "wait for the active admission to finish, then retry within the reported"
- The only text about an unattended run: `rea/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md:186` "requested operation. In an unattended run, continue through an authorized CLI" and `rea/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md:189` "call, silently broaden approvals, or rewrite MCP effects as read-only."
- Not found: a resume file for the agent, a time or token limit, a stop rule, a retry cap per target, a rule for a blocked target (Computed: `rg -n -i "handoff|hand-off|wall-clock|token budget|overnight|autonomous|long-running" AGENTS.md CONTRIBUTING.md .agents` finds only the lines above and the evidence export text).

## 5. Security statements

- `rea/SECURITY.md:11` "REA is not a general-purpose sandbox or a multi-tenant authorization service."
- A target is data: `rea/SECURITY.md:22` "an input for static inspection does not authorize commands embedded in that"
- Limits are per operation: `rea/SECURITY.md:85` "operation-specific. They are not a universal CPU, memory, disk or wall-time"
- For a hostile target: `rea/SECURITY.md:83` "isolated account, VM or restricted environment when handling hostile targets."

## 6. Bun setup

### State of this machine on 2026-11-24

| Item | Value | Needed |
| --- | --- | --- |
| Node | 26.13.1 | `rea/package.json:47` "^22.23.4 || ^24.22.1 || >=26.12.1" |
| bun | 1.4.5 | 1.2.17 or later for `rea update`: `rea/docs/getting-started/installation.md:585` "Bun 1.2.17 or later, which introduced `bun info`. The updater checks `bun --version`" |
| JDK | Temurin 25.0.5 | `rea/docs/getting-started/installation.md:1204` "JDK 25 or newer and sets no maximum. The bridge is verified with Ghidra 12.2" |
| Ghidra | 12.2 (Linuxbrew) | 12.2 or a later 12.x |
| `rea` on PATH | no | |
| `mcpServers` in `~/.claude.json` | `github`, `hermes` | setup adds `rea` |
| REA skill | installed, older copy | setup replaces it |

### Commands

Run them in a shell where `node` is on `PATH`. They were not run for this research.

```bash
# The Ghidra folder is the one that holds support/analyzeHeadless.
# In this repo, tools/env.sh resolves the same folder as GHIDRA_HOME.
export GHIDRA_INSTALL_DIR="$(brew --prefix)/Cellar/ghidra/12.2/libexec"
export JAVA_HOME="$HOME/.sdkman/candidates/java/current"

bun add --global rea-agents          # installs to ~/.bun/install/global, links ~/.bun/bin/rea
rea --version
rea doctor --provider ghidra --json  # look for healthy: true

rea setup --client claude_code --dry-run --json   # read the plan: paths, backups, changes
rea setup --client claude_code --yes --json       # apply
# restart Claude Code, then:
rea doctor --client claude_code --json
```

Remove it with `rea uninstall` and then `bun remove --global rea-agents`. The form of the second command is UNVERIFIED (the bun page for `remove` was not read).

### What the package is

- Two bin names, one file: `rea/package.json:43` "scripts/rea.mjs" The file starts with `rea/scripts/rea.mjs:1` "#!/usr/bin/env node"
- The command for setup: `rea/README.md:26` "npx rea-agents setup" A bin named `rea-agent-setup` does not exist (Computed: `rg --hidden -n -i "rea-agent-setup|rea-agents-setup" . --glob "!CHANGELOG.md" --glob "!third_party" --glob "!tests"` prints nothing). The video's command (03:00 in [02-video.md](02-video.md)) is wrong.
- Lifecycle scripts in `package.json`: `prepare`, `prepack` and `prepublishOnly` only. There is no `preinstall`, `install` or `postinstall` (Computed with grep over `package.json`).
- `prepare` does nothing in an installed package: `rea/scripts/prepare.mjs:25` "// Published installs omit source and development dependencies."
- One optional dependency has an install script: `rea/package-lock.json:7676` "node_modules/frida" with `rea/package-lock.json:7680` "hasInstallScript" What that script does is UNVERIFIED, because it is not in the clone.
- REA loads frida only for instrumentation tools: `rea/src/frida/FridaInstrumentationManager.ts:161` "(async () => (await import(" Nothing under `src/ghidra` names frida (Computed: `rg -l -i frida src/ghidra` prints nothing).
- No native build runs at install on Linux. The one compiled addon is for Windows: `rea/native/windows/README.md:3` "REA ships one Windows x64 Node-API 8 addon. Users do not compile it or install"
- The published package (`https://registry.npmjs.org/rea-agents/latest`, read on 2026-11-24) has version 6.10.1, the same bins and engines, 10,490 files and 186,235,240 bytes unpacked. It bundles all 43 dependencies and carries a shrinkwrap file. The release workflow publishes that tarball: `rea/.github/workflows/release.yml:411` "npm publish .cache/verified-package/package.tgz --ignore-scripts"
- `patches/` and `.npmrc` are for contributors. The patch is for a development dependency: `rea/scripts/lib/release-proposal.mjs:13` "patches/release-please+17.11.2.patch" `.npmrc` has one line: `rea/.npmrc:1` "engine-strict=true" Neither is in the `files` list of `package.json` (lines 50 to 122), so neither reaches an installed copy.

### What setup writes

- For Claude Code: `rea/docs/getting-started/installation.md:231` "`mcpServers.rea` in `~/.claude.json` and installs the bundled skill under" and `rea/docs/getting-started/installation.md:232` "`~/.claude/skills`, so every project that Claude Code opens can call REA. To"
- The entry holds absolute paths: `rea/docs/getting-started/installation.md:220` "directly: its absolute JavaScript runtime and entry script, followed by `mcp`"
- The Ghidra and JDK paths that setup sees go into the entry: `rea/docs/getting-started/installation.md:1325` "Java, or Python. It preserves valid detected Ghidra/JDK settings in agent" So export the two variables before setup.
- Setup shows a plan and asks: `rea/docs/getting-started/installation.md:53` "After selection, review the plan's exact paths and changes and approve before" Whether the plan is a line diff is UNVERIFIED.
- It keeps other entries and makes a backup: `rea/docs/getting-started/installation.md:72` "Agent configuration writes preserve unrelated entries and comments," and `rea/docs/getting-started/installation.md:73` "create backups, stage changes in a private directory, and verify their result."
- Flags: `rea/src/cli/setupCommands.ts:126` "Print the resolved plan without applying it" (`--dry-run`), `rea/src/cli/setupCommands.ts:71` "Approve user-owned setup actions without prompting" (`--yes`), `rea/src/cli/setupCommands.ts:91` "Agent integration to configure; repeat for multiple agents" (`--client`).
- `--yes` without a client does not select clients: `rea/docs/getting-started/installation.md:150` "`--yes` is limited to existing REA-owned registrations; it does not select all"
- Setup writes no hook and no permission rule (Computed: `rg -n -i "hooks" src/application/Setup*.ts src/application/SupportedClients.ts` prints nothing).
- Other clients: Codex `~/.codex/config.toml`, Cursor `~/.cursor/mcp.json`, Gemini CLI `~/.gemini/settings.json` (`rea/docs/getting-started/installation.md:2116` "`~/.cursor/mcp.json`. `rea setup --client cursor` remains the direct"; the Codex and Gemini paths are from `src/application/SupportedClients.ts`, lines 311 and 617).
- This registers REA for every project (user scope). To limit it to this repo, do not run setup. Add an entry to this repo's untracked `.mcp.json` by hand, in the form the docs give: `rea/docs/getting-started/installation.md:2154` "/absolute/path/to/node" and `rea/docs/getting-started/installation.md:2155` "/absolute/path/to/rea/scripts/rea.mjs", then `mcp`, with `GHIDRA_INSTALL_DIR` and `JAVA_HOME` in `env`. With the bun install, the script is `~/.bun/install/global/node_modules/rea-agents/scripts/rea.mjs` (UNVERIFIED by a run).

### What `install.sh` does

It is an npm installer and cannot use bun (Computed: `rg -n -i bun install.sh` prints nothing). It checks for curl, node and npm, reads the latest release tag from the GitHub API (`rea/install.sh:133` "https://api.github.com/repos/$REPOSITORY/releases/latest"), runs `npm install --global rea-agents@<version>` with a user prefix on Linux (`rea/install.sh:147` "install_args+=(--prefix"), checks `rea --version`, and starts `rea setup` when a terminal is present. Its flags: `rea/install.sh:71` "Usage: install.sh [--version VERSION] [--dry-run] [--no-setup] [--no-prompt] [--verbose]" With bun, skip it.

### npm to bun

| REA docs | bun | Note |
| --- | --- | --- |
| `npm install --global rea-agents` | `bun add --global rea-agents` | REA names both: `rea/README.md:275` "For a CLI installed with `npm install --global` or `bun add --global`:" |
| `npx rea-agents setup` | `bunx rea-agents setup` | REA names it: `rea/docs/getting-started/installation.md:2201` "With Bun, `bunx rea-agents setup` (or `bunx rea-agents@latest setup`) is the" Use the global install for setup (difference 3) |
| `npx -y rea-agents@latest doctor --provider ghidra --json` | `bunx rea-agents@latest doctor --provider ghidra --json` | Leave out `-y`. That bunx accepts it is UNVERIFIED |
| `rea update` | `rea update` | The updater calls bun for a bun install, with scripts off: `rea/src/application/Update.ts:116` "--ignore-scripts" |
| `curl ... install.sh | bash` | `bun add --global rea-agents` | The script is npm only |

### Differences that matter for this package

1. Bun skips install scripts of dependencies. `https://bun.sh/docs/pm/lifecycle` "Bun does not execute arbitrary lifecycle scripts by default, unlike other npm clients." Effect here: only the `frida` script is skipped, and Ghidra work does not need frida. To run it later: `https://bun.sh/docs/pm/cli/pm` "To run scripts for untrusted dependencies and add to trustedDependencies" (`bun pm trust frida` in `~/.bun/install/global`).
2. `bunx` runs this bin under Node, because of its first line. `https://bun.sh/docs/pm/bunx` "If an executable is marked with #!/usr/bin/env node, Bun spins up a node process to execute the file." So Node must stay installed. Do not pass `--bun`: REA tests Node only (`rea/docs/getting-started/installation.md:2217` "refuses to start the helper rather than running it unlimited. CI tests Node.js").
3. Setup records the paths of the process that ran it. From `bunx` that is a script in bun's cache, which REA calls fragile: `rea/docs/getting-started/installation.md:2171` "before running setup again. A global installation provides a more durable path." So install globally first, then run `rea setup`.
4. Global bins go to `~/.bun/bin` (`https://bun.sh/docs/pm/cli/pm` "To print the path to the global bin directory:") and the package goes to `~/.bun/install/global`. Put `~/.bun/bin` on `PATH` before setup. On this machine `bun` is a Linuxbrew binary, and whether `~/.bun/bin` is on the `PATH` of the fish shell and of Claude Code's bash is UNVERIFIED.
5. The MCP entry that setup writes has no `npx` in it, so nothing needs a change for bun. The plugin route is different: its manifest hardcodes `node`, and the Cursor file hardcodes `npx` (section 2). Use the setup route.
6. The tarball bundles its dependencies and has a shrinkwrap file. The bun pages read for this research do not say how bun treats either. UNVERIFIED. The direct dependencies are exact versions, so those stay the same. Deeper versions can differ from what REA tested.
7. Bun may not enforce the `engines` range, and that is UNVERIFIED. REA checks the Node version itself at start: `rea/scripts/rea.mjs:22` "const unsupportedRuntime = unsupportedRuntimeMessage("

### After the install

- Check that the PTY package for Linux x64 arrived: `rea doctor --json` reports missing parts. Whether bun installs the right optional platform package is UNVERIFIED.
- The first Ghidra call imports the binary and can take minutes. The docs give one WSL2 number: `rea/docs/reference/mcp-contracts.md:1915` "A controlled Linux x64/WSL2 fixture took about 64 seconds for its first" For `default.xbe` through an existing project, set `REA_GHIDRA_PROJECT_PATH` and `REA_GHIDRA_PROGRAM_NAME` (section 3, route 3).

## 7. What this means for the overnight run

- REA adds a second Ghidra process next to ghidra-mcp. Both read the same project files. REA works on a copy, so the two do not share a lock. The copy costs disk and start time on each session.
- The overnight design in [10-overnight-design.md](10-overnight-design.md) does not need REA. ghidra-mcp already gives the matcher its read tools, and the writes go through `bodecomp.sync`.
- The one REA use with a clear gain is the GameCube donor: REA has a DOL lane, and this repo has no Ghidra project of the GameCube binary. Trying it is a separate task. It is not part of the overnight run.
- The REA skill rules in section 2 are worth copying into `.claude/agents/matcher.md` whether or not REA is installed. See R8 in the design.
