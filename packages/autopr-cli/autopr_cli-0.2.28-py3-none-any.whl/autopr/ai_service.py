import os
import openai
import re
import json

try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"OpenAI SDK Initialization Error: {e}")
    print("Please ensure your OPENAI_API_KEY environment variable is set correctly.")
    client = None


def get_commit_message_suggestion(diff: str) -> str:
    if not client:
        return "[OpenAI client not initialized. Check API key.]"
    if not diff:
        return "[No diff provided to generate commit message.]"

    try:
        prompt_message = (
            f"Write a short, conventional one-line commit message for the following git diff:\n\n"
            f"```diff\n{diff}\n```\n\n"
            f"Start with a type (e.g., feat:, fix:, docs:, refactor:). Keep it under 72 characters. "
            f"Use simple, clear English. Avoid symbols and markdown."
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You generate clear, conventional git commit messages."},
                {"role": "user", "content": prompt_message},
            ],
            max_tokens=100,
        )
        suggestion = response.choices[0].message.content.strip()

        for pattern in [r"^```[a-z]*\n(.*?)\n```$", r"^```(.*?)```$", r"^`(.*?)`$"]:
            match = re.match(pattern, suggestion, re.DOTALL)
            if match:
                suggestion = match.group(1).strip()
                break

        return suggestion
    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        return "[Error communicating with OpenAI API]"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "[Error generating commit message]"


def get_pr_description_suggestion(commit_messages: list[str]) -> tuple[str, str]:
    if not client:
        return "[OpenAI client not initialized]", "Set OPENAI_API_KEY."
    if not commit_messages:
        return "[No commit messages provided]", "Cannot generate PR description."

    commits_str = "\n".join(f"- {msg}" for msg in commit_messages)
    prompt = (
        f"Given the following commits:\n{commits_str}\n\n"
        "Generate a PR title and body.\n"
        "Title should be one line.\n"
        "Body should summarize the purpose of the changes in simple, clear language.\n"
        "Avoid jargon. Write like you're explaining to a teammate."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "You write helpful PR titles and descriptions in everyday developer language."},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        title, body = content.strip().split("\n", 1) if "\n" in content else (content.strip(), "")

        title = title.replace("`", "").replace("\"", "")
        body = re.sub(r"^```[a-zA-Z0-9_-]*\n(.*?)\n```$", r"\1", body, flags=re.DOTALL).strip()
        return title.strip(), body.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "[Error retrieving PR description]", ""


def get_pr_review_suggestions(pr_changes: str) -> list[dict[str, str | int]]:
    if not client:
        return [{"path": "error", "line": 0, "suggestion": "[OpenAI client not initialized]"}]
    if not pr_changes:
        return [{"path": "error", "line": 0, "suggestion": "[No PR changes provided]"}]

    prompt = f"""You are a friendly and helpful code reviewer. Give clear, practical feedback in simple words.
Look for:
- Code that's hard to read
- Bugs or confusing logic
- Performance issues
- Missing comments or bad naming

For each suggestion, give:
- path (string)
- line (number)
- suggestion (string)

Return a JSON array like:
[
  {{ "path": "src/main.py", "line": 42, "suggestion": "Consider renaming this variable for clarity." }}
]

PR Changes:
```diff
{pr_changes}
```

Suggestions:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            temperature=0.5,
            max_tokens=1800,
            messages=[
                {"role": "system", "content": "You give simple, developer-friendly code review suggestions in JSON format."},
                {"role": "user", "content": prompt},
            ],
        )

        suggestions_text = response.choices[0].message.content.strip()
        parsed = json.loads(suggestions_text)

        if isinstance(parsed, list):
            return [s for s in parsed if validate_suggestion(s)]
        if isinstance(parsed, dict) and "suggestions" in parsed:
            return [s for s in parsed["suggestions"] if validate_suggestion(s)]
        if validate_suggestion(parsed):
            return [parsed]

        return [{"path": "error", "line": 0, "suggestion": "[Invalid AI response format]"}]
    except Exception as e:
        print(f"Error generating review suggestions: {e}")
        return [{"path": "error", "line": 0, "suggestion": f"[Exception: {e}]"}]


def validate_suggestion(s) -> bool:
    return (
        isinstance(s, dict) and
        isinstance(s.get("path"), str) and
        isinstance(s.get("suggestion"), str) and
        (
            isinstance(s.get("line"), int) or
            (isinstance(s.get("line"), str) and s.get("line").isdigit())
        )
    )
