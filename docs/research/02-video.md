# The video

"How to Reverse Engineer ANYTHING (Full Guide)", channel CyberFlow, `https://www.youtube.com/watch?v=DiEJJLDwgf4`, uploaded 2026-11-15, 9:57 long. The description and the automatic English captions were downloaded with yt-dlp on 2026-11-24. The transcript is not in this repo. [01-method.md](01-method.md) gives the command that downloads it again.

Citations are `[mm:ss]` and the words of the captions. The captions are automatic, so names are spelled as the captions spell them ("MorLudo" is morluto, "Toho 4" is Touhou 4). A time stamp is the start of a 15-second block.

The video is a survey with a sponsor block (04:45 to 06:00). It says nothing about how to run an agent for hours. Its use for this research is its list of projects and its list of caveats. Each claim below is checked against the clones.

## Chapters (from the description)

0:00 What Is REA? / 0:49 Crazy REA Projects / 3:05 How to Install REA / 3:29 How REA Works / 4:24 Is AI Reverse Engineering Worth It? / 5:56 Testing REA / 6:36 Independent Benchmark Results / 7:04 Fact-Checking Viral Claims / 7:43 Security Risks and Legal Issues / 8:50 Try It Yourself

## Claims and checks

| Time | Claim in the video | Check |
| --- | --- | --- |
| [00:15] "it has over 457,000" | REA has over 457,000 stars | Plausible. The GitHub API gave 476,638 on 2026-11-24 (`gh api repos/morluto/rea --jq .stargazers_count`). The REA README says `rea/README.md:314` "400,000 GitHub stars" |
| [00:45] "matched all 63 of its compiled bytes" | The official showcase matched one DX-Ball sound function | The REA README states it. No log of it is in the REA clone. UNVERIFIED |
| [01:00] "270 out of 270 functions and all 84,968" | The whole game matches | The ledgers in the dx-ball clone agree. The byte equality needs files that are not in git. See [03-dx-ball.md](03-dx-ball.md), section 5 |
| [01:00] "They had Codex drive REA through Ghidra across the whole game" | Codex did it | `dx-ball/README.md:4` "original executable and resources. Codex uses [REA](https://github.com/morluto/rea)" |
| [01:00] "On October 22nd, it was done" | Date | The last change to the match ledger is commit `ecfc475` of 2026-10-22 |
| [01:15] "They had Codex" and [01:30] "install REA, used it to untangle the whole thing" | The Claude slides editor was rebuilt with Codex and REA | The baocut clone does not name REA, Ghidra or reverse engineering. The slides package was removed on 2026-11-23. See [05-baocut.md](05-baocut.md). The community list files this as the author's own statement: `awesome/docs/is-it-rea.md:30` "**Claimed by the author, not in the README.** The REA part is one commit, not the whole repo." |
| [01:45] "A developer used Claude code with REA to take apart the original screensaver file" | Johnny Castaway in Rust | The README says so. The repo holds no Ghidra or REA output. See [06-open-scrantic-hexgrab.md](06-open-scrantic-hexgrab.md) |
| [02:00] "Someone patched the firmware of a Sony A6000 camera until it shot completely silently" | Firmware patch | `a6000/README.md:12` "con el firmware modificado **3.23** (parche de 2 bytes sobre Darwin)" (a 2-byte patch). See [07-a6000.md](07-a6000.md) |
| [02:30] "REA got eight out of nine fully right" | hexgrab report card | `hexgrab/docs/rea-findings.md:56` "**8 of 9 fully correct, 1 partly correct.**" The table grades 9 rows. 5 of the 11 findings in the same file have no row |
| [02:30] "They took Toho 4" | Touhou 4 showcase | The community list: `awesome/docs/is-it-rea.md:21` "**REA only for the showcase inspection.** The reconstruction is agent-produced with ReC98 as a base." |
| [03:00] "Setting it up is one command, npx rea-agent-setup" | Install command | Wrong. The command is `npx rea-agents setup`. See [04-rea-and-bun.md](04-rea-and-bun.md), section 6 |
| [03:00] "it shows you every change" | Setup shows changes first | `rea/AGENTS.md:11` "`rea setup` must show its planned changes and require approval before writing files or installing Hopper." |
| [03:30] "It hands your agent over 200 tools" | Tool count | Not counted in this research. Other sources give 207 for REA 6.5.0 (`a6000/docs/capture/rea-independent-milestone.md:13` "expone **207 herramientas**") and 153 for 6.4.0 (`rea-lab/writeups/2026-10-study-3/README.md:134` "rea 6.4.0 advertised 153 tools.") |
| [03:30] "It doesn't decompile anything itself" | REA drives other tools | `rea/README.md:225` "Deep native analysis uses Hopper, Ghidra, IDA or Kuna, depending on the target" |
| [04:00] "Every answer says where it found it and what it still doesn't know" | Evidence and unknowns | `rea/.agents/skills/reverse-engineer-anything/SKILL.md:413` "Every conclusion must distinguish observations, inferences, and unknowns." This is a rule for the agent, not a property of each answer |
| [04:00] "And the newest version, 6.9" | Version | The clone and the npm registry are at 6.10.1 on 2026-11-24 |
| [04:30] "It wasn't the agent. It was someone checking its work" | The check is what counts | Agrees with every repo in this set. See [README.md](README.md), "What the sources agree on" |
| [06:15] "28 minutes later, it spat out a recreation in Python" | Low Level's calculator demo | UNVERIFIED. No source for it is in this research |
| [06:30] "ran five pre-registered studies, 482 runs with Claude code" | The studies | Confirmed: 70 + 48 + 144 + 40 + 180 runs. See [08-lists-and-experiments.md](08-lists-and-experiments.md) |
| [06:30] "On 10 small Crack Me challenges, the agent solved 28 out of" | 28 of 30 with and without REA | Confirmed: `rea-lab/writeups/2026-10-study-1/README.md:28` "| Solved | 28/30 (93 %, 79 to 98 %) | 28/30 (93 %, 79 to 98 %) | 9/10 (90 %, 60 to 98 %) |" The 30 are runs: 10 programs, 3 runs each |
| [06:45] "And the REA runs cost about twice the time and money" | Cost | True for the three Claude studies with a no-REA arm (2.1 to 2.7 times, from the medians). The DeepSeek study gives about 1.2 times |
| [06:45] "it solved 11 out of 24 without REA and four with it" | Harder programs | Confirmed: `rea-lab/writeups/2026-10-study-2/README.md:35` "| Solved | 11/24 (46 %, 28 to 65 %) | 4/24 (17 %, 7 to 36 %) |" |
| [06:45] "The researcher says that gap isn't" | Not significant | Confirmed: `rea-lab/writeups/2026-10-study-2/README.md:45` "Of the 24 pairs, 13 disagree: in 10 only A solved, in 3 only B (exact McNemar, p = 0.092)." |
| [07:00] "It shines on one narrow question about a known part of a program" | Where REA helps | This is the community list's advice, not a study result: `awesome/README.md:248` "Use REA for targeted questions on a known surface, not open-ended exploration." |
| [07:15] "only one, DX Ball, says in its own repo that it used REA" | The list's check of six cases | `awesome/README.md:19` "only one, DX-Ball, says in its own repo that it used REA." |
| [07:15] "its developer also helps build REA" | Not independent | `awesome/README.md:125` "The author is also a contributor to REA, so this is a first-party case." The REA clone has 387 commits by the author name N0zoM1z0 (Computed: `git log --format=%an | sort | uniq -c`) |
| [07:15] "The Steam game turned into a Unity project in 30 minutes" | A claim with no code | `awesome/docs/x-posts.md:10` "the figure appears only in this README and is unverified)." |
| [07:30] "The DJI Home Security drone went massive" | DJI | UNVERIFIED. Neither list clone names DJI (`rg -n --hidden -g '!.git' -i 'dji|drone'` prints nothing) |
| [07:30] "And the Modern Warfare 2 de compilation used its" | MW2 used another pipeline | `awesome/README.md:189` "Author reports 17 agents over three months, 83% of functions byte-matched. Code is not public." |
| [08:00] "REA's own security notes say it's not a sandbox" | Not a sandbox | `rea/SECURITY.md:11` "REA is not a general-purpose sandbox or a multi-tenant authorization service." |
| [08:00] "Everything it finds goes to whatever AI model you're using" | Data leaves the machine | True of any agent session. Not checked against a REA document |

## What the video adds for the overnight design

1. Its three working examples have one thing in common: a check against the original that the agent cannot argue with. [04:30] "Every function compared against the original, every finding held up against Microsoft's real code". This repo has that check (`bodecomp.match`).
2. Its advice is to ask narrow questions: [08:45] "ask one narrow question, and check the answer against the original". A matcher batch does this per function.
3. It names no long-run method. Nothing in it supports the claim that a session can be left alone for a night.
