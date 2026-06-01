<!--
SYSTEM INSTRUCTIONS FOR AI AGENTS:
1. You MUST read this file first upon entering the workspace to understand the project context, requirements, rules, and task progress.
2. Keep this file updated at the end of each session, milestone, or task execution.
3. Update the Task Checklist (e.g., [x] for done, [/] for in-progress, [ ] for pending).
4. Log your token usage in the Token Ledger table below after completing your turn or session. If you cannot get exact numbers, estimate them (1 word ≈ 1.33 tokens) and note it.
-->

# Project AI Context & Token Ledger

## 🎯 High-Level Goal
Implement a robust token tracking and context handoff system for developers and AI agents.

## 🛠️ System Rules & Preferences
- **Platform/OS**: Windows (PowerShell)
- **Primary Language**: Python 3.x
- **Token Count Standard**: Use `tiktoken` (cl100k_base / o200k_base) or a fallback character/word-based estimation (1 word ≈ 1.33 tokens).
- **Process Guidelines**: 
  - Minimize external dependencies where possible.
  - Always keep the `ai_context.md` updated at the end of execution.

## 📊 Token Usage Ledger

| Date | Agent/Model | Input Tokens (est) | Output Tokens (est) | Cumulative Cost | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-01 | gemini-3.5-flash | 2,458 | 5,764 | $0.0019 | Initial handoff validation |

## 📋 Task Checklist
- [x] Create `ai_context.md` template in the workspace root
- [x] Create `token_handoff.py` script in the workspace root
- [x] Test python script and parse the current `transcript.jsonl` to calculate token metrics
- [x] Verify that `ai_context.md` gets updated correctly by the script
- [/] Create `walkthrough.md` summarizing the changes and instructions for transfer

## 📂 Active Workspace Files
- [ai_context.md](ai_context.md): This context and tracking file.
- [token_handoff.py](token_handoff.py): Automation script to parse logs and update this context ledger.
