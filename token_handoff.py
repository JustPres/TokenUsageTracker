#!/usr/bin/env python3
"""
Token Tracking & Handoff Automation Utility
Works as:
1. A CLI tool to parse session logs (JSONL) and update `ai_context.md`
2. A reusable Python library for logging LLM token usage and managing context state.
"""

import os
import re
import json
import datetime
import argparse

# Cost per 1M tokens (Input, Output) in USD
PRICING = {
    "gemini-3.5-flash": (0.075, 0.30),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-3-5-sonnet": (3.00, 15.00),
    "default": (1.00, 3.00) # conservative fallback
}

def count_tokens(text: str) -> int:
    """
    Estimates token count of text.
    Uses `tiktoken` if installed (cl100k_base); otherwise falls back
    to robust word-count (1.33 tokens/word) and char-count heuristics.
    """
    if not text:
        return 0
    
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Fallback heuristic: 1 word ≈ 1.33 tokens; 4 characters ≈ 1 token.
        # We take the max of these two estimators for safety.
        words = text.split()
        est_by_words = int(len(words) * 1.33)
        est_by_chars = len(text) // 4
        return max(est_by_words, est_by_chars, 1)

def get_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Calculates cost of tokens based on model name."""
    model_key = model_name.lower()
    # Find matching model or use default
    rates = PRICING["default"]
    for key, val in PRICING.items():
        if key in model_key:
            rates = val
            break
            
    input_cost = (input_tokens / 1_000_000.0) * rates[0]
    output_cost = (output_tokens / 1_000_000.0) * rates[1]
    return input_cost + output_cost

class TokenTracker:
    """
    Reusable library class to track token usage, maintain checklist,
    and update `ai_context.md` in any Python application.
    """
    def __init__(self, context_path: str = "ai_context.md", default_model: str = "gemini-3.5-flash"):
        self.context_path = context_path
        self.default_model = default_model
        self.cumulative_input = 0
        self.cumulative_output = 0

    def log_tokens(self, input_tokens: int, output_tokens: int):
        """Manually log token counts."""
        self.cumulative_input += input_tokens
        self.cumulative_output += output_tokens

    def log_text(self, prompt_text: str, response_text: str):
        """Log text content, automatically estimating token usage."""
        self.cumulative_input += count_tokens(prompt_text)
        self.cumulative_output += count_tokens(response_text)

    def update_ledger(self, model_name: str = None, notes: str = "Automated run update"):
        """Updates the markdown ledger file with current session's token log."""
        if not model_name:
            model_name = self.default_model

        if not os.path.exists(self.context_path):
            print(f"Warning: Context file {self.context_path} not found. Creating a new one.")
            self._create_empty_context()

        with open(self.context_path, 'r', encoding='utf-8') as f:
            content = f.read()

        today = datetime.date.today().isoformat()
        cost = get_cost(model_name, self.cumulative_input, self.cumulative_output)
        
        # Format tokens and cost
        in_str = f"{self.cumulative_input:,}"
        out_str = f"{self.cumulative_output:,}"
        cost_str = f"${cost:.4f}" if cost > 0 else "$0.00"

        new_row = f"| {today} | {model_name} | {in_str} | {out_str} | {cost_str} | {notes} |\n"

        # Regex to locate table and headers
        # We look for a line starting with '| Date | Agent/Model |' and its separator line
        pattern = r"(\| Date \| Agent/Model \|[^\n]+\n\| :?---[^\n]+\n)"
        match = re.search(pattern, content)
        if match:
            # Insert the new row directly below the separator line
            header_and_separator = match.group(1)
            content = content.replace(header_and_separator, header_and_separator + new_row)
            print(f"Updated Token Ledger in {self.context_path}.")
        else:
            # Fallback if no table exists: append to end
            content += f"\n\n## 📊 Token Usage Ledger\n\n| Date | Agent/Model | Input Tokens (est) | Output Tokens (est) | Cumulative Cost | Notes |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n" + new_row
            print(f"Appended new Token Ledger table to {self.context_path}.")

        with open(self.context_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_empty_context(self):
        default_content = """<!--
SYSTEM INSTRUCTIONS FOR AI AGENTS:
1. You MUST read this file first upon entering the workspace.
2. Keep this file updated at the end of each session.
-->

# Project AI Context & Token Ledger

## 🎯 High-Level Goal
Context placeholder.

## 📊 Token Usage Ledger

| Date | Agent/Model | Input Tokens (est) | Output Tokens (est) | Cumulative Cost | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
        with open(self.context_path, 'w', encoding='utf-8') as f:
            f.write(default_content)


def parse_transcript(jsonl_path: str):
    """
    Parses a workspace transcript JSONL file and counts tokens
    segregated by input (prompts/system) and output (agent responses).
    """
    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"Transcript file not found: {jsonl_path}")

    input_text = []
    output_text = []

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                source = data.get("source")
                step_type = data.get("type")
                content = data.get("content", "")
                
                # Extract text from tool calls if present
                tool_calls_text = ""
                tool_calls = data.get("tool_calls")
                if tool_calls:
                    tool_calls_text = json.dumps(tool_calls)

                # Segregate into inputs (user request, system instructions, tool outputs/errors)
                # and outputs (model reasoning, responses, tool proposals)
                if source == "USER_EXPLICIT" or source == "SYSTEM":
                    input_text.append(content)
                elif source == "MODEL":
                    if step_type in ("PLANNER_RESPONSE", "SUGGEST_CHANGES"):
                        output_text.append(content)
                        if tool_calls_text:
                            output_text.append(tool_calls_text)
                        # If thinking log is saved in thinking metadata
                        thinking = data.get("thinking", "")
                        if thinking:
                            output_text.append(thinking)
                    else:
                        # Execution of tools or run command output is system feedback (input to model)
                        input_text.append(content)
            except Exception as e:
                # Silently skip bad lines
                pass

    total_in = sum(count_tokens(t) for t in input_text)
    total_out = sum(count_tokens(t) for t in output_text)
    return total_in, total_out


def main():
    parser = argparse.ArgumentParser(description="Parse session transcripts and update AI context ledgers.")
    parser.add_argument("--log-path", help="Path to transcript.jsonl", default=None)
    parser.add_argument("--context-path", help="Path to ai_context.md", default="ai_context.md")
    parser.add_argument("--model", help="LLM model name used", default="gemini-3.5-flash")
    parser.add_argument("--notes", help="Custom note for ledger row", default="Analyzed session log")
    
    args = parser.parse_args()

    # If log-path is specified, compute tokens from JSONL transcript
    if args.log_path:
        print(f"Parsing transcript at: {args.log_path}")
        try:
            total_in, total_out = parse_transcript(args.log_path)
            print(f"Calculation details:")
            print(f"  Input Tokens: {total_in:,}")
            print(f"  Output Tokens: {total_out:,}")
            
            tracker = TokenTracker(context_path=args.context_path, default_model=args.model)
            tracker.log_tokens(total_in, total_out)
            tracker.update_ledger(model_name=args.model, notes=args.notes)
        except Exception as e:
            print(f"Error parsing transcript: {e}")
    else:
        # Prompt for manual token insertion if no log provided
        print("No log path provided. Running interactive tracking helper.")
        model_name = input("Enter model name (e.g. gpt-4o, gemini-3.5-flash) [gemini-3.5-flash]: ").strip() or "gemini-3.5-flash"
        try:
            in_t = int(input("Enter input tokens: ").strip() or 0)
            out_t = int(input("Enter output tokens: ").strip() or 0)
            notes = input("Enter notes: ").strip() or "Manual entry"
            
            tracker = TokenTracker(context_path=args.context_path, default_model=model_name)
            tracker.log_tokens(in_t, out_t)
            tracker.update_ledger(model_name=model_name, notes=notes)
        except ValueError:
            print("Invalid token counts. Please enter integers.")

if __name__ == "__main__":
    main()
