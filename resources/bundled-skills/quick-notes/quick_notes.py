#!/usr/bin/env python3
"""
Quick Notes - Fast note taking and task management
Capture ideas, tasks, and notes instantly.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# Notes directory
NOTES_DIR = Path.home() / '.quick-notes'
NOTES_FILE = NOTES_DIR / 'notes.json'


def ensure_notes_dir():
    """Ensure notes directory exists."""
    NOTES_DIR.mkdir(exist_ok=True)


def load_notes() -> List[Dict]:
    """
    Load notes from file.

    Returns:
        List of note dictionaries
    """
    ensure_notes_dir()

    if not NOTES_FILE.exists():
        return []

    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_notes(notes: List[Dict]):
    """
    Save notes to file.

    Args:
        notes: List of note dictionaries
    """
    ensure_notes_dir()

    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(content: str, note_type: str = 'note') -> Dict:
    """
    Add a new note.

    Args:
        content: Note content
        note_type: Type of note (note, task, idea)

    Returns:
        Created note dictionary
    """
    notes = load_notes()

    note = {
        'id': len(notes) + 1,
        'type': note_type,
        'content': content,
        'created_at': datetime.now().isoformat(),
        'completed': False
    }

    notes.append(note)
    save_notes(notes)

    return note


def list_notes(note_type: Optional[str] = None) -> List[Dict]:
    """
    List notes, optionally filtered by type.

    Args:
        note_type: Filter by type (note, task, idea)

    Returns:
        Filtered list of notes
    """
    notes = load_notes()

    if note_type:
        notes = [n for n in notes if n['type'] == note_type]

    return notes


def search_notes(keyword: str) -> List[Dict]:
    """
    Search notes by keyword.

    Args:
        keyword: Search keyword

    Returns:
        List of matching notes
    """
    notes = load_notes()
    keyword_lower = keyword.lower()

    return [
        n for n in notes
        if keyword_lower in n['content'].lower()
    ]


def complete_task(task_id: int) -> bool:
    """
    Mark a task as completed.

    Args:
        task_id: Task ID

    Returns:
        True if successful, False otherwise
    """
    notes = load_notes()

    for note in notes:
        if note['id'] == task_id and note['type'] == 'task':
            note['completed'] = True
            save_notes(notes)
            return True

    return False


def delete_note(note_id: int) -> bool:
    """
    Delete a note.

    Args:
        note_id: Note ID

    Returns:
        True if successful, False otherwise
    """
    notes = load_notes()

    for i, note in enumerate(notes):
        if note['id'] == note_id:
            notes.pop(i)
            save_notes(notes)
            return True

    return False


def clear_notes():
    """Clear all notes."""
    ensure_notes_dir()

    if NOTES_FILE.exists():
        NOTES_FILE.unlink()

    print("All notes cleared.")


def export_notes(filepath: str):
    """
    Export notes to a text file.

    Args:
        filepath: Output file path
    """
    notes = load_notes()

    if not notes:
        print("No notes to export.")
        return

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Quick Notes Export\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for note in notes:
                icon = {
                    'note': '📝',
                    'task': '✅' if note['completed'] else '⬜',
                    'idea': '💡'
                }.get(note['type'], '📌')

                f.write(f"{icon} [{note['type'].upper()}] {note['content']}\n")
                f.write(f"   Created: {note['created_at']}\n\n")

        print(f"Notes exported to: {filepath}")
    except IOError as e:
        print(f"Error exporting notes: {e}")


def format_note(note: Dict) -> str:
    """
    Format a note for display.

    Args:
        note: Note dictionary

    Returns:
        Formatted string
    """
    icon = {
        'note': '📝',
        'task': '✅' if note['completed'] else '⬜',
        'idea': '💡'
    }.get(note['type'], '📌')

    created = note['created_at'][:19].replace('T', ' ')

    return f"{icon} [{note['id']}] {note['content']}\n   Type: {note['type']} | Created: {created}"


def print_notes(notes: List[Dict]):
    """
    Print notes in a readable format.

    Args:
        notes: List of note dictionaries
    """
    if not notes:
        print("No notes found.")
        return

    print(f"\n{'=' * 60}")
    print(f"Found {len(notes)} note(s)")
    print('=' * 60)

    for note in notes:
        print()
        print(format_note(note))

    print()


def main():
    """
    Main entry point.
    """
    if len(sys.argv) < 2:
        print("Quick Notes - Fast note taking")
        print("\nUsage: quick-notes <command> [args]")
        print("\nCommands:")
        print("  add <text>      - Add a note")
        print("  task <text>     - Add a task")
        print("  idea <text>     - Add an idea")
        print("  list            - List all notes")
        print("  tasks           - List only tasks")
        print("  ideas           - List only ideas")
        print("  search <keyword> - Search notes")
        print("  complete <id>   - Mark task as completed")
        print("  delete <id>     - Delete a note")
        print("  clear           - Clear all notes")
        print("  export <file>   - Export notes to file")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'add':
        if len(sys.argv) < 3:
            print("Error: Note content required")
            sys.exit(1)
        content = ' '.join(sys.argv[2:])
        note = add_note(content, 'note')
        print(f"✓ Note added: {note['content']}")

    elif command == 'task':
        if len(sys.argv) < 3:
            print("Error: Task content required")
            sys.exit(1)
        content = ' '.join(sys.argv[2:])
        note = add_note(content, 'task')
        print(f"✓ Task added: {note['content']}")

    elif command == 'idea':
        if len(sys.argv) < 3:
            print("Error: Idea content required")
            sys.exit(1)
        content = ' '.join(sys.argv[2:])
        note = add_note(content, 'idea')
        print(f"✓ Idea captured: {note['content']}")

    elif command == 'list':
        notes = list_notes()
        print_notes(notes)

    elif command == 'tasks':
        notes = list_notes('task')
        print_notes(notes)

    elif command == 'ideas':
        notes = list_notes('idea')
        print_notes(notes)

    elif command == 'search':
        if len(sys.argv) < 3:
            print("Error: Search keyword required")
            sys.exit(1)
        keyword = ' '.join(sys.argv[2:])
        notes = search_notes(keyword)
        print(f"Searching for: {keyword}")
        print_notes(notes)

    elif command == 'complete':
        if len(sys.argv) < 3:
            print("Error: Task ID required")
            sys.exit(1)
        task_id = int(sys.argv[2])
        if complete_task(task_id):
            print(f"✓ Task {task_id} marked as completed")
        else:
            print(f"✗ Task {task_id} not found")

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Error: Note ID required")
            sys.exit(1)
        note_id = int(sys.argv[2])
        if delete_note(note_id):
            print(f"✓ Note {note_id} deleted")
        else:
            print(f"✗ Note {note_id} not found")

    elif command == 'clear':
        clear_notes()

    elif command == 'export':
        if len(sys.argv) < 3:
            print("Error: Output file path required")
            sys.exit(1)
        filepath = sys.argv[2]
        export_notes(filepath)

    else:
        print(f"Unknown command: {command}")
        print("Run 'quick-notes' without arguments for help")
        sys.exit(1)


if __name__ == '__main__':
    main()
