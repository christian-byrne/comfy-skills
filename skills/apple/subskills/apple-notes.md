# Apple Notes

Manage Apple Notes via the `memo` CLI on macOS. Notes sync across Apple devices via iCloud.

## Prerequisites

```bash
brew install antoniorodr/memo/memo
```

## Commands

| Action               | Command                                                |
| -------------------- | ------------------------------------------------------ |
| List all notes       | `memo list`                                            |
| List notes in folder | `memo list --folder "Work"`                            |
| View a note          | `memo view "Note Title"`                               |
| Search by title      | `memo search "keyword"`                                |
| Search by content    | `memo search --body "keyword"`                         |
| Create a note        | `memo create "Title" --body "Content here"`            |
| Create in folder     | `memo create "Title" --folder "Work" --body "Content"` |
| Edit a note          | `memo edit "Title"`                                    |
| Delete a note        | `memo delete "Title"`                                  |
| Move to folder       | `memo move "Title" --folder "Archive"`                 |
| Export to Markdown   | `memo export "Title" --format markdown`                |
| Export to HTML       | `memo export "Title" --format html`                    |

## Notes

- Notes sync to iPhone/iPad/Mac via iCloud automatically
- Folder names are case-sensitive
- Use `memo list` first to find exact note titles before operating on them
- Supports fuzzy search for finding notes by partial title matches
