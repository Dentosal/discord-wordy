# Discord bot that give "Wordy" role to winner of yesterday's Wordle.

Maybe it will do more in the future. Maybe not.

## Usage

Set following env variables, possibly using `.env` file. Generate invite from Discord API console.

```
DISCORD_TOKEN=<your-token-here>
WORDLE_CHANNEL_ID=<channel-id>
GUILD_ID=<server-id>
```

## Dev

```bash
python3 -m venv .venv
source .venv/bin/activate
```