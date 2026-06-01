# Agent Token Tracker & Context Handoff

An open-source utility designed to solve **token tracking** and **context handoff** when migrating tasks or conversations between different AI agents, Large Language Models (LLMs), or development tools (e.g., Cursor, Windsurf, Copilot, Antigravity).

It provides:
1. **`ai_context.md`**: A universal markdown template you drop into any project workspace. It contains embedded system prompts directing any AI agent that opens the folder to read it, respect the workspace guidelines, and keep the task checklist and token usage ledger up-to-date.
2. **`token_handoff.py`**: A CLI tool and reusable Python library to estimate token counts (using `tiktoken` or robust heuristics), calculate usage costs across popular APIs (Gemini, OpenAI, Anthropic), and automatically maintain the markdown ledger.

---

## 🚀 Key Features

* 📦 **Zero-Config Import**: Simply copy `ai_context.md` into any directory. Modern agents scan directories on startup; the embedded prompt ensures they pick up your context.
* ⚖️ **Cross-Model Token Tracking**: Keep a single, unified log of tokens consumed and costs incurred across different model APIs.
* 📈 **Cost Calculation**: Automated cost tracking based on actual pricing matrices for Gemini 3.5, GPT-4o, Claude 3.5, and more.
* 🛠️ **CLI Transcript Parser**: Automatically extracts prompt and completion text from system JSONL logs (like workspace histories) to count the tokens of an entire session post-hoc.
* 🐍 **Reusable Python Library**: Integrate token logging directly into your custom agent frameworks.

---

## 📥 Installation

The script utilizes built-in Python libraries and can run with zero external dependencies using character/word token heuristics. For precise token counts matching OpenAI/Gemini models, install `tiktoken`:

```bash
pip install tiktoken
```

---

## 📖 Usage Guide

### 1. Initializing the Context Template
Copy the [ai_context.md](ai_context.md) file into your project repository. 
Inside, customize the **🎯 High-Level Goal** and **🛠️ System Rules & Preferences** to match your project context.

Any agent reading the folder will see the instructions at the top:
```markdown
<!--
SYSTEM INSTRUCTIONS FOR AI AGENTS:
1. You MUST read this file first upon entering the workspace.
2. Keep this file updated at the end of each session or milestone.
3. Log your token usage in the Token Ledger table below.
-->
```

---

### 2. Running as a CLI Tool
You can parse a transcript log file (JSONL format) to update your ledger automatically.

```bash
python token_handoff.py --log-path "/path/to/transcript.jsonl" --context-path "ai_context.md" --model "gemini-3.5-flash" --notes "Fitted main components"
```

If you don't have a log file and want to manually log token usage:
```bash
python token_handoff.py --context-path "ai_context.md"
```
*This triggers an interactive prompt where you can enter the model, input/output tokens, and notes.*

---

### 3. Integrating into your Python Agent Applications
Import the `TokenTracker` class to log token metrics at runtime:

```python
from token_handoff import TokenTracker

# Instantiate tracker (defaults to writing to 'ai_context.md')
tracker = TokenTracker(context_path="ai_context.md", default_model="gpt-4o")

# Option A: Log exact token numbers returned by LLM API responses
tracker.log_tokens(input_tokens=2540, output_tokens=812)

# Option B: Pass raw prompt/completion strings to estimate token usage automatically
tracker.log_text(
    prompt_text="Hello model, write a flask server.",
    response_text="Sure! Here is the code for the flask app..."
)

# Commit the accumulated tokens to the markdown ledger
tracker.update_ledger(model_name="gpt-4o", notes="API run for backend services")
```

---

## 💸 Supported Cost Matrix
The ledger computes costs dynamically based on the model provided. Included models:
* `gemini-3.5-flash` / `gemini-1.5-flash`
* `gemini-1.5-pro`
* `gpt-4o` / `gpt-4o-mini`
* `claude-3-5-sonnet`

To add custom models, modify the `PRICING` dictionary in `token_handoff.py`.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
