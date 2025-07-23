import discord
from os import getenv
import re
from dotenv import load_dotenv

load_dotenv()

def getenv_and_convert(varname, default=None, type_func=str):
    value = getenv(varname)
    if value is None:
        value = default
    if value is None:
        exit("Missing environment variable: " + varname)
    try:
        return type_func(value)
    except:
        exit(f"Environment variable {varname}={value} requires {type_func.__name__}")

DISCORD_TOKEN = getenv_and_convert("DISCORD_TOKEN", None, str)
WORDLE_CHANNEL_ID = getenv_and_convert("WORDLE_CHANNEL_ID", None, int)
WORDLE_APP_USER_ID = getenv_and_convert("WORDLE_APP_USER_ID", "1211781489931452447", int)
GUILD_ID = getenv_and_convert("GUILD_ID", None, int)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

async def ensure_role():
    """Ensure the 'Wordy' role exists, and return it."""
    guild = client.get_guild(GUILD_ID)

    if guild is None:
        raise ValueError("Guild not found. Please check the GUILD_ID.")

    role_name = "Wordy"
    existing = discord.utils.get(guild.roles, name=role_name)
    if existing:
        print(f"Role '{role_name}' already exists.")
        return existing

    new_role = await guild.create_role(
        name=role_name,
        colour=discord.Colour.gold(),
        hoist=True,  # Show role separately in user list
        mentionable=True,  # Allow @ mention
    )
    print(f"Created role: {new_role.name}")
    return new_role


async def update_role_members(winners, role):
    """Update members' roles based on the winners list."""
    guild = client.get_guild(GUILD_ID)

    if guild is None:
        print("Guild not found.")
        return

    async for member in guild.fetch_members(limit=None):
        # Not all some winners are user IDs, some might be in @Name format.
        is_winner = False
        for winner in winners:
            if winner in [member.id, member.name, member.global_name, member.display_name]:
                is_winner = True
                break

        has_role = role in member.roles

        if is_winner and not has_role:
            await member.add_roles(role)
        elif not is_winner and has_role:
            await member.remove_roles(role)

async def lookback_winner():
    """Look back in the Wordle channel for yesterday's winner."""
    channel = client.get_channel(WORDLE_CHANNEL_ID)

    if channel is None:
        print(f"Could not find channel with ID {WORDLE_CHANNEL_ID}")
        return

    async for message in channel.history(limit=1000):
        if winners := extract_winner_ids(message):
            return winners


def extract_winner_ids(message) -> list:
    """If a message contains a winner mention, return the user IDs."""
    if message.author.id != WORDLE_APP_USER_ID:
        return []

    if "yesterday's results:" in message.content:
        lines = message.content.splitlines()
        if len(lines) < 2:
            return []
        if not lines[1].startswith("👑") or (":" not in lines[1]):
            return []
        text = lines[1].split(":", 1)[1].strip()
        
        winners = []
        # Some ids have format <@123456> but other might be just @Name and it can contain spaces too.
        # Parse the proper DIs first and then extract the rest.
        for name in re.findall("<@\d+>", text):
            winners.append(int(name[2:-1]))  # Extract the user ID from <@123456>
            text = text.replace(name, "")

        for name in re.findall(r"@[^@]+", text):
            winners.append(name[1:].strip())  # Extract the name without @

        return winners

    return []

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # Ensure the role exists
    role = await ensure_role()
    if winners := await lookback_winner():
        await update_role_members(winners, role)


@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")

    if winners := extract_winner_ids(message):
        role = await ensure_role()
        await update_role_members(winners, role)


client.run(getenv("DISCORD_TOKEN"))
