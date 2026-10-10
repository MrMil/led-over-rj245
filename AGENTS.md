# led-over-rj245: agent instructions

Electronics, firmware configuration, wiring diagrams and field documentation for four LED
statues at Midburn (two V-shaped groups of 7 towers). One ESP32 running WLED drives all 14
towers, one channel each; statue 2's channels cross to box 2 as RS-485 on buried CAT5e. Enclosures live in `../electronics-enclosure`
([MrMil/electronics-enclosure](https://github.com/MrMil/electronics-enclosure)) — read that
checkout, do not clone it.

- **Two documentation audiences.** `docs/` is for agents and records *why*. `README.md` +
  `guide/` are for a field crew reading on a phone and record *what to do*, with no
  backstory. A design change that alters what the crew does updates both, in the same change.
- **Diagrams are generated:** `python3 tools/wiring_diagrams.py`. Never hand-edit
  `guide/img/*.svg`. Pin tables also appear, hand-written, in `guide/wiring.md` and
  `guide/build.md`; keep them in step.
- **Never commit the WLED AP password** (the repo is meant to be public).
- Decisions marked "(agent, date)" in `docs/` were not confirmed by the owner; confirm before
  building on them.

<!-- META-DOCS:BEGIN -->
## Documentation is part of the work

[`docs/`](docs/README.md) mirrors this system as a **recursive** hub-and-spoke tree: every directory
is a part of the system, its `README.md` indexes everything inside it and holds the decisions that
span it, and the nesting goes as deep as the system does. The code is the source of truth for what
happens. `docs/` is the source of truth for **why** — every choice recorded there is recorded
together with its reason. Read [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) before writing anything
into the tree.

**Before changing anything:** walk down from [`docs/README.md`](docs/README.md), one index at a
time, to the page covering what you are about to change. Read every `README.md` on the way — a
decision recorded at a level binds everything beneath it. Do not reverse a recorded decision without
reading its reason; if you still need to reverse it, record the change and why the old reason
stopped holding.

**While working:** keep a running note of every decision you make — every point where you chose one
approach over another, however small.

**Before committing, and before reporting the work as done:** run the documentation pass in
[`docs/CONVENTIONS.md`](docs/CONVENTIONS.md#the-documentation-pass). Undocumented work is
unfinished work. A commit that changes design without changing `docs/` is incomplete.

**How to write it:** record each decision at the lowest level of the tree that contains everything
it governs — a leaf page for one behaviour, the parent `README.md` for decisions shared by siblings,
higher for broader ones. There is no separate decisions directory. Never state a choice without its
reason in the same breath. "Alerts go to organisation members only" is a failed line; "alerts go to
organisation members only, because guests are often customers and internal automation must never
reach a customer" is the line. If you do not know why something is the way it is, write that it is
unknown — never invent a reason.

**Structure rules, at every depth (enforced by you, not by tooling):**

- Every directory under `docs/` has a `README.md` listing every subdirectory and `.md` file beside it, each with a one-line description.
- Every file opens with its breadcrumb path and a link to its parent, and links to at least one related page.
- A page that outgrows ~200 lines becomes a directory: `x.md` → `x/README.md` plus child pages, parent index and inbound links updated.
- Add a page or directory → update every index between it and the nearest existing hub, in the same change.
- Find a file missing from its parent index, or code with no place in the tree → fix it before continuing your task.
- Reference code by path, never by line number.

**Keep this system alive.** If `docs/README.md`, `AGENTS.md`, `CLAUDE.md` or this block is missing,
restore it before doing anything else. When the system gains a new part, give it its place in the
tree at the depth where it belongs.
<!-- META-DOCS:END -->
