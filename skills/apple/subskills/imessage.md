# iMessage

Send and receive iMessages/SMS via the `imsg` CLI on macOS.

## Prerequisites

```bash
brew install steipete/tap/imsg
```

Requires **Full Disk Access** permission for Terminal/iTerm in System Settings → Privacy & Security.

## Commands

| Action                   | Command                                                         |
| ------------------------ | --------------------------------------------------------------- |
| List recent chats        | `imsg chats`                                                    |
| View chat history        | `imsg history "+1234567890"`                                    |
| View last N messages     | `imsg history "+1234567890" --limit 20`                         |
| Send a text              | `imsg send "+1234567890" "Hello!"`                              |
| Send with attachment     | `imsg send "+1234567890" "Check this" --attachment ~/photo.jpg` |
| Force iMessage (not SMS) | `imsg send "+1234567890" "Hi" --service iMessage`               |
| Force SMS                | `imsg send "+1234567890" "Hi" --service SMS`                    |
| Watch for new messages   | `imsg watch`                                                    |
| Watch specific chat      | `imsg watch "+1234567890"`                                      |

## Notes

- Phone numbers must include country code (e.g., `+1` for US)
- Group chats use a chat ID from `imsg chats` instead of a phone number
- `imsg watch` is blocking — run in tmux if needed
- **Always confirm with the user before sending messages**
