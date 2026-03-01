---
name: quick-notes
description: Quickly capture ideas, tasks, and notes with voice or text. Perfect for recording thoughts on the fly, creating to-do lists, and managing personal notes without typing.
allowed-tools: Bash(uv run python ~/.openclaw/skills/quick-notes/quick_notes.py *)
---

# Quick Notes

Quickly capture ideas, tasks, and notes with voice or text. Perfect for recording thoughts on the fly, creating to-do lists, and managing personal notes without typing.

## Usage

### Add a Note

Quickly add a note:

```bash
quick-notes add "Your note here"
```

### Add a Task

Add a task to your to-do list:

```bash
quick-notes task "Buy groceries"
```

### Add an Idea

Capture an idea:

```bash
quick-notes idea "Build a new app"
```

### List All Notes

View all your notes:

```bash
quick-notes list
```

### List Tasks

View only tasks:

```bash
quick-notes tasks
```

### List Ideas

View only ideas:

```bash
quick-notes ideas
```

### Search Notes

Search through your notes:

```bash
quick-notes search "keyword"
```

### Clear Notes

Clear all notes:

```bash
quick-notes clear
```

### Export Notes

Export notes to a file:

```bash
quick-notes export notes.txt
```

## Examples

```bash
# Quick note
quick-notes add "Meeting with team at 3pm"

# Add task
quick-notes task "Finish project report"

# Capture idea
quick-notes idea "New feature: dark mode"

# List all
quick-notes list

# Search
quick-notes search "meeting"

# Export
quick-notes export my-notes.txt
```

## Note Types

- **Notes**: General notes and reminders
- **Tasks**: Actionable items with checkboxes
- **Ideas**: Creative thoughts and inspirations

## Storage

Notes are stored locally in `~/.quick-notes/` directory.

## Benefits

- **Fast**: Capture thoughts instantly
- **Voice-ready**: Works with voice commands
- **Organized**: Separate notes, tasks, and ideas
- **Searchable**: Find notes quickly
- **Exportable**: Backup your notes anytime
