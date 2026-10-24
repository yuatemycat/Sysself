# Qoder & CodeBuddy Agent Harness Specifications

## Qoder & CodeBuddy Invariants
Both Qoder and CodeBuddy utilize event-driven lifecycle hooks (`SessionStart`, `PostToolUse`) and `.qoder/mcp.json` / `.codebuddy/settings.json` configurations:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "code-review-graph update --skip-flows --repo .",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### System Prompt Directive:
```markdown
You are an autonomous engineering assistant integrated via Qoder/CodeBuddy.
Your edits trigger background knowledge graph updates. Keep tool executions fast, deterministic, and bounded.
```
