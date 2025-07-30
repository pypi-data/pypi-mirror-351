# Task List Code Review MCP Server

An MCP server tool designed for **AI coding agents** (Cursor, Claude Code, etc.) to automatically generate comprehensive code review context when completing development phases.

**Version**: 0.2.1 - Enhanced with scope-based reviews, dual tool architecture, AI-powered code analysis, and configurable model management.

## 🚀 Quick Start

### Try It First (No Installation Required)

**Recommended**: Test the tool with uvx before deciding to install globally:

```bash
# Set your Gemini API key (get one at https://ai.google.dev/gemini-api/docs/api-key)
export GEMINI_API_KEY=your_key_here

# Run directly without installing anything (uvx handles everything)
uvx task-list-code-review-mcp /path/to/your/project

# Output: Generates both context and AI review files automatically
# - code-review-context-{scope}-{timestamp}.md
# - code-review-comprehensive-feedback-{timestamp}.md
```

### Install Globally (If You Like It)

```bash
# Install from PyPI
pip install task-list-code-review-mcp

# Now available as a command
task-list-code-review-mcp /path/to/your/project
```

## ✨ Key Features

### Smart Scope Detection
- **All phases complete** → Automatically generates comprehensive full-project review
- **Phases in progress** → Reviews most recently completed phase
- **Manual override** → Target specific phases or tasks

### AI-Powered Code Review
- **Gemini Integration**: Uses Gemini 2.5 Flash/Pro for intelligent code analysis
- **Thinking Mode**: Deep reasoning about code quality and architecture
- **Web Grounding**: Looks up current best practices and technology information
- **Comprehensive Analysis**: Covers security, performance, testing, and maintainability

### Flexible Architecture
- **Context Generation**: Creates structured review context from git changes and task progress
- **AI Review**: Separate tool for generating AI-powered feedback from context files
- **Model Configuration**: Easy model switching and alias management via JSON config

## 📖 Basic Usage

### CLI Usage

```bash
# Smart Default: Auto-detects project completion status
# - If all phases complete: Reviews entire project  
# - If phases in progress: Reviews most recent completed phase
uvx task-list-code-review-mcp /path/to/project

# Review entire project (force full scope)
uvx task-list-code-review-mcp /path/to/project --scope full_project

# Review specific phase by number
uvx task-list-code-review-mcp /path/to/project --scope specific_phase --phase-number 2.0

# Generate context only (skip AI review)
uvx task-list-code-review-mcp /path/to/project --context-only

# Use different Gemini model
GEMINI_MODEL=gemini-2.5-pro uvx task-list-code-review-mcp /path/to/project
```

### MCP Server Integration

**Claude Desktop/Cursor Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "task-list-reviewer": {
      "command": "uvx",
      "args": ["task-list-code-review-mcp"],
      "env": {
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

**Usage in Claude Desktop:**
```
Human: Generate a code review context for my project at /Users/myname/projects/my-app

Claude: I'll generate a code review context using smart scope detection.

[Tool Use: generate_code_review_context]
{
  "project_path": "/Users/myname/projects/my-app"
}

[Tool Result] Successfully generated: code-review-context-full-project-20241201-143052.md
```

## 🛠 Advanced Configuration

### Environment Variables

**Core Configuration:**
- `GEMINI_API_KEY`: Required for Gemini integration
- `MAX_FILE_SIZE_MB`: Maximum file size to read in MB (default: 10)
- `MAX_FILE_CONTENT_LINES`: Max lines per file (default: 500)
- `MAX_FILE_TREE_DEPTH`: Tree depth limit (default: 5)

**Model Configuration:**
- `GEMINI_MODEL`: Model for code review (default: `gemini-2.0-flash`)
  - Use aliases: `gemini-2.5-pro`, `gemini-2.5-flash`
  - Or full names: `gemini-2.5-pro-preview-05-06`
- `GEMINI_TEMPERATURE`: AI creativity (default: 0.5, range: 0.0-2.0)

### Security Best Practices
**API Key Protection:**
```bash
# Secure .env file permissions
chmod 600 ~/.task-list-code-review-mcp.env
chmod 600 .env

# Never commit .env files to version control
echo ".env" >> .gitignore
```

### Model Configuration File (model_config.json)

The tool uses a JSON configuration file (`src/model_config.json`) to manage model aliases and capabilities, making it easy to update when Google releases new model versions:

```json
{
  "model_aliases": {
    "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash": "gemini-2.5-flash-preview-05-20"
  },
  "model_capabilities": {
    "url_context_supported": [
      "gemini-2.5-pro-preview-05-06",
      "gemini-2.5-flash-preview-05-20",
      "gemini-2.0-flash"
    ],
    "thinking_mode_supported": [
      "gemini-2.5-pro-preview-05-06",
      "gemini-2.5-flash-preview-05-20"
    ]
  },
  "defaults": {
    "model": "gemini-2.0-flash",
    "summary_model": "gemini-2.0-flash-lite"
  }
}
```

**Capabilities Auto-Detection:**
- **URL Context**: Enhanced web content understanding
- **Thinking Mode**: Advanced reasoning for complex problems  
- **Web Grounding**: Up-to-date information from search

**Usage Examples:**
```bash
# Use simple alias names instead of complex preview model names
review-with-ai context.md --model gemini-2.5-pro
GEMINI_MODEL=gemini-2.5-flash uvx task-list-code-review-mcp /project
```

**Updating for New Models:**
When Google releases new versions, simply update the JSON file:
```json
{
  "model_aliases": {
    "gemini-2.5-pro": "gemini-2.5-pro-preview-06-07"  // Updated version
  }
}
```

**Fallback Behavior:**
- Missing JSON file → Uses built-in defaults
- JSON parsing errors → Logs warning and continues
- Invalid model names → Falls back to environment/config defaults

## 🔧 MCP Tools Reference

### generate_code_review_context

**Primary tool for generating code review context with flexible scope options.**

**Scope Options:**

| Scope | Description | Output Pattern |
|-------|-------------|----------------|
| `recent_phase` | **Smart Default**: Reviews recent phase OR full project if all complete | `*-recent-phase-*` or `*-full-project-*` |
| `full_project` | Reviews all completed phases | `*-full-project-*` |
| `specific_phase` | Reviews specific phase (requires `phase_number`) | `*-phase-X-Y-*` |
| `specific_task` | Reviews specific task (requires `task_number`) | `*-task-X-Y-*` |

**MCP Usage Examples:**
```javascript
// Smart default - auto-detects completion status
await use_mcp_tool({
  server_name: "task-list-code-review-mcp",
  tool_name: "generate_code_review_context",
  arguments: {
    project_path: "/absolute/path/to/project"
  }
});

// Review specific phase
await use_mcp_tool({
  server_name: "task-list-code-review-mcp",
  tool_name: "generate_code_review_context",
  arguments: {
    project_path: "/absolute/path/to/project",
    scope: "specific_phase",
    phase_number: "2.0"
  }
});
```

### generate_ai_code_review

**Standalone tool for generating AI-powered code reviews from existing context files.**

```javascript
await use_mcp_tool({
  server_name: "task-list-code-review-mcp",
  tool_name: "generate_ai_code_review",
  arguments: {
    context_file_path: "/path/to/code-review-context-*.md",
    model: "gemini-2.5-pro"
  }
});
```

## 🔄 Workflow Integration for AI Agents

### Smart Completion Detection

The tool automatically detects project completion status:

**Project Complete Workflow:**
```
AI Agent: "I've completed the final phase. Let me generate a code review."
Tool detects: All phases (1.0-7.0) complete → Full project review
Output: code-review-context-full-project-{timestamp}.md
```

**Mid-Development Workflow:**
```
AI Agent: "I've completed Phase 2.0 of 5.0. Let me generate a review."
Tool detects: Phases in progress → Recent completed phase
Output: code-review-context-recent-phase-{timestamp}.md
```

### Compatible Format Specifications

**PRDs**: Based on [create-prd.mdc](https://github.com/snarktank/ai-dev-tasks/blob/main/create-prd.mdc)
- File naming: `prd-[feature-name].md` in `/tasks/` directory
- Structured markdown with Goals, User Stories, Functional Requirements

**Task Lists**: Based on [generate-tasks.mdc](https://github.com/snarktank/ai-dev-tasks/blob/main/generate-tasks.mdc)
- File naming: `tasks-[prd-file-name].md` in `/tasks/` directory
- Hierarchical phases (1.0, 2.0) with sub-tasks (1.1, 1.2)
- Checkbox progress tracking (`- [ ]` / `- [x]`)

## 🚨 Troubleshooting

### Common Issues

**API Key Not Found:**
```bash
ERROR: GEMINI_API_KEY not found
```
**Solution:**
```bash
# Get API key: https://ai.google.dev/gemini-api/docs/api-key
export GEMINI_API_KEY=your_key_here
# Or create ~/.task-list-code-review-mcp.env file
```

**Scope Parameter Errors:**
```bash
ERROR: phase_number is required when scope is 'specific_phase'
```
**Solution:**
```bash
uvx task-list-code-review-mcp /project --scope specific_phase --phase-number 2.0
```

**File Not Found:**
```bash
ERROR: No PRD or task list files found
```
**Solution:** Ensure your project has:
- PRD file: `tasks/prd-*.md`
- Task list: `tasks/tasks-*.md`

### File Permissions
```bash
# Fix .env file permissions
chmod 600 ~/.task-list-code-review-mcp.env

# Fix context file permissions  
chmod 644 /path/to/context.md
```

### Git Repository Issues
```bash
# Initialize git if needed
git init

# Ensure you're in a git repository
ls -la .git
```

## 📋 What This Tool Generates

- **Phase Progress Summary** - Completed phases and sub-tasks
- **PRD Context** - Original requirements (auto-summarized with Gemini)
- **Git Changes** - Detailed diff of all modified/added/deleted files
- **File Tree** - ASCII project structure representation
- **File Content** - Full content of changed files for review
- **AI Code Review** - Comprehensive feedback using Gemini 2.5
- **Structured Output** - Professional markdown ready for human review

## 📦 Development

```bash
# Clone and install in development mode
git clone <repository-url>
cd task-list-code-review-mcp
pip install -e .

# Run tests
pytest
```

## 📄 Project Structure

- `src/generate_code_review_context.py` - Core context generation
- `src/ai_code_review.py` - Standalone AI review tool
- `src/server.py` - MCP server wrapper
- `src/model_config.json` - Model configuration and aliases
- `tests/` - Comprehensive test suite
- `pyproject.toml` - Project configuration and entry points