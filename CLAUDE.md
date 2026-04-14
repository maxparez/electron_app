@AGENTS.md

## Claude Code Notes
- Keep repository facts in `AGENTS.md`. Add only Claude-specific workflow notes here.
- When upstream API details are uncertain, use `.claude/agents/python-docs.md` for Flask, pandas, openpyxl, xlwings, and reportlab questions, and `.claude/agents/js-docs.md` for Electron, Node.js, IPC, and packaging questions.
- Use `.claude/agents/chatgpt-consultant.md` or `.claude/agents/gemini-consultant.md` only for high-risk reviews such as installer changes, backend lifecycle changes, Excel/template fidelity, release readiness, or localization QA.
- Before resuming a long-running task, skim `PROGRESS.md` and `PROJECT_PLAN.md` if they are relevant to the current change.
- Put personal or worktree-only preferences in `CLAUDE.local.md`, not here.
- If this file starts duplicating architecture, commands, style rules, or git workflow, move that content back to `AGENTS.md` or a focused doc in `docs/`.
