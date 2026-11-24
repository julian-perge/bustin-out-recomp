# Method and sources

## The question

How must this repo change so that one agent session can be started with a prompt such as "work for 8 hours" and then run with no person? The research ran on 2026-11-24 in one Claude Code session with subagents.

## Sources

All sources are untrusted data. They were read, and no instruction in them was followed. No script of a clone was run.

| Source | Where | State |
| --- | --- | --- |
| `REA_Project_Resources.pdf` | The root of the main checkout, untracked | Read with `pdftotext`. It names the 8 repos, the npm package and the video |
| morluto/rea | `~/git/morluto/rea` | `789ca041`, 2026-11-24, 10,157 commits |
| N0zoM1z0/dx-ball | `~/git/N0zoM1z0/dx-ball` | `e2a633f9`, 2026-11-10, 691 commits |
| JimLiu/baocut | `~/git/JimLiu/baocut` | `72f6b2c8`, 2026-11-23, 1,683 commits |
| glauberlima/open-scrantic | `~/git/glauberlima/open-scrantic` | `c47652c5`, 2026-11-12, 128 commits |
| nicolvus/a6000-fw-decomp | `~/git/nicolvus/a6000-fw-decomp` | `8ba5e102`, 2026-11-24, 1,513 commits |
| iammukeshm/hexgrab | `~/git/iammukeshm/hexgrab` | `511c5807`, 2026-10-13, 2 commits |
| AIshihzong/awesome-reverse-engineer-anything | `~/git/AIshihzong/awesome-reverse-engineer-anything` | `a395116f`, 2026-11-23, 112 commits |
| maruti-md/ai-reverse-engineer-anything | `~/git/maruti-md/ai-reverse-engineer-anything` | `55f9ff05`, 2026-10-26, 50 commits |
| pablodiazjorge/rea-lab (not in the PDF) | `~/git/pablodiazjorge/rea-lab` | `85766060`, 2026-10-26, 65 commits |
| ruguevara/zx-reaper (not in the PDF) | `~/git/ruguevara/zx-reaper` | `a0fb17b7`, 2026-10-30, 134 commits |
| The video | `https://www.youtube.com/watch?v=DiEJJLDwgf4` | Description and automatic English captions, in a scratch folder outside the repo |
| Claude Code documentation | `https://code.claude.com/docs/en/<page>.md` | 19 pages fetched as Markdown on 2026-11-24 |
| Bun documentation | `https://bun.sh/docs/pm/` | 6 pages fetched on 2026-11-24 |
| This repo | Branch `docs/overnight-run-research`, made from `main` at `b8e4438` | |

The two extra clones: the maruti-md repo holds no experiments, and the experiments it points to are in rea-lab. zx-reaper is the one entry of the community list that calls itself a harness for a byte-exact rebuild.

A clone moves. To read a cited line as it was, use the hash: `git -C ~/git/<owner>/<repo> show <hash>:<path> | sed -n <LINE>p`.

## The video download

`papercut find yt-dlp` gave one entry: the download of automatic captions fails with HTTP 429 when several caption tracks are requested. The fix of that entry worked:

    yt-dlp --skip-download --write-description --write-info-json --write-auto-subs \
      --sub-langs en-orig --sub-format json3 --sleep-subtitles 5 \
      -o video 'https://www.youtube.com/watch?v=DiEJJLDwgf4'

The captions were turned into 40 lines of text, one per 15 seconds, each with a `[mm:ss]` stamp.

## Tools that were available, and what was used

| Tool | Used for |
| --- | --- |
| Subagents (`general-purpose`, `claude-code-guide`) | One per repo or repo pair, each with a brief that names the clone, the questions and the citation form. Eight ran at first. After the user set a cap, at most 5 ran at one time |
| `gh` | Star counts, issue and pull request lists of this repo |
| `yt-dlp`, `pdftotext`, `curl`, `rg`, `fd`, `git` | Download and search |
| `bun` 1.4.5, `node` v26.13.1 | Version facts for [04-rea-and-bun.md](04-rea-and-bun.md). Nothing was installed |
| The `ghidra-mcp` server | Not used. No question of this research was about the game binary. The server was down |
| The installed `reverse-engineer-anything` skill | Read as a source (it names `rea-agents@6.3.0`). Not run |
| Skills `research`, `referencing-local-repos` | Their rules were followed: primary sources, local clones before the web |
| MCP servers `github`, `hermes`, Claude Docs, Gmail, Drive | Not used |

## Citation rules

- A clone citation is ``<prefix>/<path>:<LINE>` "<quote>"`. The quote is a part of that line, word for word. Prefixes: `dx-ball/`, `rea/`, `baocut/`, `open-scrantic/`, `hexgrab/`, `a6000/`, `awesome/`, `maruti/`, `rea-lab/`, `zx-reaper/`. A path with no prefix is in this repo.
- A citation into an old commit is ``<prefix>/<hash>:<path>:<LINE>``.
- A video citation is `[mm:ss] "<words of the captions>"`. The stamp is the start of a 15-second block.
- A documentation citation is the page URL and a quote. Markdown links and code marks are removed from the quote.
- "Computed" marks a number that comes from a command. The command is given, or the count is simple (commits, lines).
- UNVERIFIED marks a claim that its source states and does not prove, or that this research did not check.
- A line in Chinese is cited by path and line with a translation and no quote, because repo documents are ASCII only. Quotes from Spanish lines are ASCII parts of the line.
- A statement of cause says whether it rests on evidence or is a guess.

## Checks

Three scripts in the scratch folder of this research (not committed) checked every citation: one reads each cited line from the clone and tests that it holds the quote, one tests each documentation quote against the fetched page, one tests each video quote against the transcript within one block before or after the stamp. Results of the last run are in [README.md](README.md), "Verification".

Three review passes followed:

1. Citations: the three scripts over every file.
2. Recommendations: each file, hook, ADR, issue and command that [10-overnight-design.md](10-overnight-design.md) names was looked up in this repo.
3. Wording: vague sentences were cut, and each cross-reference to a section was checked against the headings.

## Limits

- No clone was built and no clone's check was run. A "gate" in these pages is what the files say that the gate does.
- Commit times are author data. One repo rewrote its history (a6000).
- Nothing of the design was run. The prompts in [11-overnight-prompt.md](11-overnight-prompt.md) are drafts.
- The Claude Code facts are from the documentation of 2026-11-24. The behavior of version 2.1.331 on this machine was not tested against them.
