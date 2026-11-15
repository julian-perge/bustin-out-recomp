# ADR-0016: The public repo starts from one fresh commit, and a tracked file lists the old hashes

- **Status:** Accepted (user decision)
- **Date:** 2026-11-15

## Context

The repo had 147 commits of private work before it became a public GitHub project (ADR-0014). The user chose to publish it from one fresh commit and to keep the old history on the maintainer's machine.

`bodecomp.findings check` verifies that the commit of each `fixed (<commit>)` entry exists. On 2026-11-15 `docs/FINDINGS.md` had 14 such entries, which cite 8 commits of the old history. None of those commits is in the public repo, so the check failed there.

## Decision

- The first public commit has no parent. Its tree is the tree of the last private commit.
- `config/pre-public-commits.txt` lists the full hash of each of the 147 private commits up to 742e585. The two private commits after it prepared the publication, and no entry cites them. The file does not change after the first public commit.
- `bodecomp.findings check` accepts a `fixed (<commit>)` hash that is a commit in git, or that starts a hash in the list.
- The entries in `docs/FINDINGS.md` keep their text and their IDs.

## Consequences

- A reader cannot look up a private hash in the public repo. The list shows only that the commit existed. This also applies to the private hashes that the evidence text of some entries names.
- An entry that is fixed after the first public commit cites a commit that must stay in the public history. A squash merge and a rebase merge on GitHub give the commits of a pull request new hashes. A pull request whose findings cite its own commits needs a merge commit, or the entries need the new hash after the merge.
