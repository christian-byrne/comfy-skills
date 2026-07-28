# Apple Reminders

Manage Apple Reminders via the `remindctl` CLI. Syncs to iPhone/iPad via iCloud.

## Prerequisites

```bash
brew install steipete/tap/remindctl
```

## Commands

| Action                  | Command                                                    |
| ----------------------- | ---------------------------------------------------------- |
| List today's reminders  | `remindctl list --day today`                               |
| List this week          | `remindctl list --day week`                                |
| List by date            | `remindctl list --day 2024-03-15`                          |
| List all lists          | `remindctl lists`                                          |
| List from specific list | `remindctl list --list "Shopping"`                         |
| Create a reminder       | `remindctl create "Buy groceries"`                         |
| Create with due date    | `remindctl create "Call dentist" --due "2024-03-20 14:00"` |
| Create in specific list | `remindctl create "Milk" --list "Shopping"`                |
| Complete a reminder     | `remindctl complete "Buy groceries"`                       |
| Delete a reminder       | `remindctl delete "Old reminder"`                          |
| Manage lists            | `remindctl lists create "New List"`                        |

## Notes

- Changes sync to all Apple devices via iCloud automatically
- This manages **Apple Reminders** — not agent cron jobs or scheduled tasks
- Due dates accept natural language in some cases but ISO format is most reliable
