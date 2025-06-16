# Tool Prompts Directory

This directory contains detailed context prompts for complex tools.

## Usage

When a tool needs additional context beyond its docstring, create a file named `{tool_name}.txt` here.

## Example

For a tool named `downtime_RCA_tool`, create:
```
src/prompts/tools/downtime_RCA_tool.txt
```

The agent can then call `get_tool_context("downtime_RCA_tool")` to get detailed usage information.

## File Naming Convention

- File name must match tool name exactly
- Use `.txt` extension
- Example: `analyze_maintenance_patterns_tool.txt`

## Content Format

Tool prompt files should include:
- Detailed description of what the tool does
- When to use this tool vs alternatives
- Input parameter guidance
- Expected output format
- Usage examples
